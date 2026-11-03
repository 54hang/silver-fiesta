"""Version-209 protocol-to-solution checks; no game traffic or mouse input."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from game_known_plaintext import js_plaintext
from test_auto_capture import HASH, ack, map_bytes, start
from world_capture import WorldCapture


def encrypted(value):
    engine = Cipher(algorithms.AES(b'0123456789abcdef'), modes.OFB(b'fedcba9876543210')).encryptor()
    return engine.update(value) + engine.finalize()


class WorldIntegrationTests(unittest.TestCase):
    def test_version_209_encrypted_seed_to_independently_verified_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture = WorldCapture(Path(tmp), auto_download=False, auto_solve=True,
                                   crypto_probe=False, publish_legacy=False)
            try:
                capture.accept_start(start(), path='/sheep/v1/game/world/game_start')
                capture.accept_map(HASH, map_bytes())
                identifier = capture.current['seed2']
                params = {'info': base64.b64encode(b'\0\x75\xbf' + encrypted(
                    bytes([10, len(identifier)]) + identifier.encode())).decode(), 'encryptKeyVersion': 209}
                flow = SimpleNamespace(metadata={}, request=SimpleNamespace(
                    pretty_url='https://cat-match.easygame2021.com/sheep/v1/game/map_info_ex_seed',
                    content=json.dumps(params).encode()),
                    response=SimpleNamespace(status_code=200, content=encrypted(ack())))
                capture.request(flow)
                capture.response(flow)
                self.assertFalse(capture.state['complete'])
                body = {'rank_state': 2, 'map_seed_2': 'marker', 'play_info': 'fixture-only' * 30}
                body['encrypt_data'] = base64.b64encode(encrypted(js_plaintext(body))).decode()
                body['encrypt_key_version'] = 209
                settlement = SimpleNamespace(metadata={}, request=SimpleNamespace(
                    pretty_url='https://cat-match.easygame2021.com/sheep/v1/game/world/game_over',
                    content=json.dumps(body).encode()))
                capture.request(settlement)
                deadline = time.monotonic() + 15
                while capture.state.get('solver') in ('not_started', 'running') and time.monotonic() < deadline:
                    time.sleep(.1)
                self.assertTrue(capture.state['complete'])
                self.assertEqual(capture.state['seed_source'], 'validated_settlement_stream')
                self.assertEqual(capture.state['solver'], 'solved')
                answer_path = Path(capture.state['solution_path'])
                answer = json.loads(answer_path.read_text(encoding='utf-8'))
                map_path = Path(capture.state['current_map'])
                self.assertEqual(answer['map_sha256'], hashlib.sha256(map_path.read_bytes()).hexdigest())
                self.assertEqual(len(answer['sequence']), 6)
                from desktop_assistant import validate_solution
                validate_solution(answer)
                for file in Path(tmp).rglob('*.json'):
                    text = file.read_text(encoding='utf-8')
                    self.assertNotIn('encrypt_data', text)
                    self.assertNotIn('DO_NOT_RETAIN', text)
            finally:
                capture.pool.shutdown(wait=True, cancel_futures=True)
                capture.done()


if __name__ == '__main__':
    unittest.main()
