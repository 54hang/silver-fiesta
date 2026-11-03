#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/11/30 00:00
# Create User: NB-Dragon
import json
import urllib.parse
import time
from pathlib import Path
from core.map.SeedDecoder import decode_seed, valid_seed
from core.map.OnlineDataAnalyzer import OnlineDataAnalyzer
from core.map.StaticDataGenerator import StaticDataGenerator
from core.tool.GameLinkController import GameLinkController
from helper.ProjectHelper import ProjectHelper


class DataAnalyzer(object):
    def __init__(self):
        self._generation = 0
        self._pending = None
        self._project_helper = ProjectHelper()
        self._prepare_runtime_param()

    def _prepare_runtime_param(self):
        link_config = self._project_helper.get_project_config("protect", "link")
        self._game_link_controller = GameLinkController(link_config)
        self._online_data_analyzer = OnlineDataAnalyzer(self._project_helper)
        self._static_data_generator = StaticDataGenerator(self._project_helper)
        self._game_start_list = self._game_link_controller.get_game_start_list()
        self._game_seed_list = [item["seed"] for item in link_config["game"].values()]

    def request(self, flow):
        parsed = urllib.parse.urlparse(flow.request.url)
        if parsed.hostname != "cat-match.easygame2021.com":
            return
        if self._is_game_start_link(parsed.path):
            self._generation += 1
            self._pending = None
        flow.metadata["sheep_generation"] = self._generation

    def response(self, flow):
        link_parse_result = urllib.parse.urlparse(flow.request.url)
        if link_parse_result.hostname == "cat-match.easygame2021.com":
            if self._is_game_start_link(link_parse_result.path):
                if flow.metadata.get("sheep_generation") != self._generation:
                    return
                try:
                    response_data = json.loads(flow.response.content)
                    data = response_data["data"]
                    self._pending = {"hash": data["map_md5"][1], "time": time.monotonic(),
                                     "generation": self._generation}
                    self._handle_response_result(response_data)
                except (ValueError, KeyError, TypeError, IndexError) as error:
                    self._pending = None
                    print("=====> 开局数据格式不兼容: {}".format(type(error).__name__))
            elif any(link_parse_result.path.endswith(path) for path in self._game_seed_list):
                self._handle_seed_response(flow)
        elif link_parse_result.netloc == "cat-match-static.easygame2021.com":
            if self._is_game_resource_data(flow.response.content):
                print(flow.response.content.decode())

    def _handle_seed_response(self, flow):
        pending = self._pending
        if (not pending or flow.metadata.get("sheep_generation") != pending["generation"]
                or time.monotonic() - pending["time"] > 60):
            print("=====> 未找到对应的本次开局，忽略种子；请重新进入关卡")
            return
        body = flow.request.content or b""
        try:
            if body.lstrip().startswith(b"{"):
                params = json.loads(body)
            else:
                params = dict(urllib.parse.parse_qsl(body.decode("utf-8")))
        except (ValueError, UnicodeError):
            params = {}
        version = params.get("encryptKeyVersion", params.get("encrypt_key_version"))
        raw = flow.response.content or b""
        diagnostic = {"map_hash": pending["hash"], "response_bytes": len(raw),
                      "request_fields": sorted(params), "encryption_version": version}
        try:
            if flow.response.status_code != 200:
                raise ValueError("种子接口未返回 HTTP 200")
            if version not in (None, 0, "0", ""):
                raise ValueError("种子使用加密版本 {}，原项目不支持解密".format(version))
            if raw.lstrip().startswith(b"{"):
                decoded = json.loads(raw)
                decoded = decoded.get("data", decoded)
            else:
                decoded = decode_seed(raw)
            if not valid_seed(decoded.get("map_seed")):
                raise ValueError("种子响应没有四个有效整数")
            if decoded.get("map_seed_2"):
                raise ValueError("种子包含额外派生数据，尚未验证当前版本洗牌规则")
            self._static_data_generator.fill_seed_data_into_file(pending["hash"], decoded["map_seed"])
            diagnostic["status"] = "plain_seed_received"
            self._pending = None
        except (ValueError, TypeError, KeyError, UnicodeError) as error:
            diagnostic["status"] = "unsupported_seed"
            diagnostic["reason"] = str(error)
            print("=====> 已捕获种子响应（{} 字节），但无法验证: {}".format(len(raw), error))
            print("=====> 当前关卡尚不能求解，请勿使用示例地图")
        target = Path(__file__).resolve().parent / "runtime" / "capture-status.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2), encoding="utf-8")

    def _is_game_start_link(self, request_path):
        match_list = [item for item in self._game_start_list if request_path.endswith(item)]
        return len(match_list) != 0

    @staticmethod
    def _is_game_resource_data(bytes_data):
        resource_name_list = [b"gd_language", b"gd_skin_list", b"gd_game_topic_list", b"gd_block_topic_slot_data"]
        match_list = [item for item in resource_name_list if item in bytes_data]
        return len(match_list) != 0

    def _handle_response_result(self, response_data):
        map_hash = response_data["data"]["map_md5"][1]
        map_seed = response_data["data"]["map_seed"]
        self._online_data_analyzer.create_map_struct_file(map_hash)
        self._static_data_generator.fill_seed_data_into_file(map_hash, map_seed)


addons = [DataAnalyzer()]
