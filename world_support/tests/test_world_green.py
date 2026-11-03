import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import app_bridge
from board_align import fit, check_silhouette, pale_faces

FIXTURE = Path(__file__).parent / 'fixtures/world-green'


class WorldGreenTests(unittest.TestCase):
    def test_background_is_not_a_tile(self):
        colors = np.array([[[207, 252, 152], [247, 255, 210]]])
        self.assertEqual(pale_faces(colors).tolist(), [[False, True]])

    def test_real_tutorial_identified_without_accepting_main_level(self):
        candidates = app_bridge.fresh_board_candidates(FIXTURE, FIXTURE / 'board.png', 2)
        self.assertEqual([c['level'] for c in candidates], [0])

    def test_extra_tile_still_rejected(self):
        data = app_bridge.read(FIXTURE / 'map_0.json')
        cards = [{**c, 'layer': int(k)} for k, v in data['levelData'].items() for c in v]
        calibration, _ = fit(FIXTURE / 'board.png', cards)
        with tempfile.TemporaryDirectory() as directory:
            image = Image.open(FIXTURE / 'board.png').convert('RGB')
            ImageDraw.Draw(image).rectangle((50, 380, 85, 417), fill=(247, 255, 210))
            path = Path(directory) / 'extra.png'
            image.save(path)
            with self.assertRaises(ValueError):
                check_silhouette(path, cards, calibration)
