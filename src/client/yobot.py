# coding=utf-8
import json
import os
import sys
from typing import List

import check_ver
import dmg_record
import gacha
import jjc_consult
import lock_boss
import reserve
import switcher
import yobot_msg
from plugins.yobot_errors import File_error


class Yobot:
    def __init__(self):
        dirname = os.path.dirname(sys.argv[0])
        config_f_path = os.path.join(dirname, "yobot_config.json")
        if not os.path.exists(config_f_path):
            raise File_error(config_f_path + " not exists")
        with open(config_f_path, "r", encoding="utf-8") as config_file:
            try:
                self.glo_setting = json.load(config_file)
            except:
                raise File_error(config_f_path + " been damaged")

        inner_info = {
            "dirname": dirname,
            "version": {
                "ver_name": "3.0.0_alpha_b1",
                "ver_id": 2906
                "check_url": "https://gitee.com/yobot/yobot/raw/master/docs/v3/ver.json"}}
        self.glo_setting.update(inner_info)

        self.plugins = []
        self.plugins.append(check_ver.Check(self.glo_setting))
        self.plugins.append(switcher.Switcher(self.glo_setting))
        self.plugins.append(yobot_msg.Message(self.glo_setting))
        self.plugins.append(gacha.Gacha(self.glo_setting))
        self.plugins.append(jjc_consult.Consult(self.glo_setting))
        self.plugins.append(lock_boss.Lock(self.glo_setting))
        self.plugins.append(dmg_record.Record(self.glo_setting))
        self.plugins.append(reserve.Reserve(self.glo_setting))

    def proc(self, msg: dict) -> List[str]:
        replys = []
        for pitem in self.plugins:
            func_num = pitem.match(msg["raw_message"])
            if func_num:
                res = pitem.excute(func_num, msg)
                replys.append(res["reply"])
                if res["block"]:
                    break
        return replys
