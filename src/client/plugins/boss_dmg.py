# 把不想改的祖传代码封装一下

from plugins import dmg_record, lock_boss, reserve


class Boss_dmg:
    def __init__(self, glo_setting: dict):
        self.setting = glo_setting

    @staticmethod
    def match(cmd: str) -> int:
        func = lock_boss.Lock.match(cmd)
        if func != 0:
            return func | 0x1000
        func = dmg_record.Record.match(cmd)
        if func != 0:
            return func | 0x2000
        func = reserve.Reserve.match(cmd)
        if func != 0:
            return func | 0x3000
        return 0

    def execute(self, match_num: int, msg: dict) -> dict:
        if msg["message_type"] == "group":
            reply = "此功能仅可用于群聊"
            return {"reply": reply, "block": True}
        swit = match_num & 0xf000
        func = match_num & 0x0fff
        cmd_list = (str(msg["group_id"]),
                    str(msg["sender"]["user_id"]),
                    msg["sender"]["card"])
        cmdi = msg["raw_message"].split("//", 1)
        cmd = cmdi[0]
        if len(cmdi) == 1:
            cmt = None
        else:
            cmt = cmdi[1]
        if (cmd.startswith("重新开始") or cmd.startswith("选择") or cmd.startswith("切换")
                or cmd.startswith("修正") or cmd.startswith("修改") or cmd == "上传报告"):
            super_admins = self.setting.get("super-admin", list())
            restrict = self.setting.get("setting-restrict", 3)
            if msg["sender"]["user_id"] in super_admins:
                role = 0
            else:
                role_str = msg["sender"].get("role",None)
                if role_str == "owner":
                    role = 1
                elif role_str == "admin":
                    role = 2
                else:
                    role = 3
            if role > restrict:
                reply = "你的权限不足"
                return {"reply": reply, "block": True}
        txt_list = []
        if swit == 0x1000:
            lockboss = lock_boss.Lock(cmd_list[:3])
            lockboss.lockboss(cmd, func, comment=cmt)
            txt_list.extend(lockboss.txt_list)
        if swit == 0x2000:
            report = dmg_record.Record(cmd_list[:3])
            report.rep(cmd, func)
            txt_list.extend(report.txt_list)
            if (cmd.endswith("尾刀") or cmd.endswith("收尾")
                    or cmd.endswith("收掉") or cmd.endswith("击败")):
                rsv = reserve.Reserve(cmd_list[:3])
                rsv.rsv(cmd, 0x20)
                txt_list.extend(rsv.txt_list)
            if func == 2 or func == 3 or func == 400 or func == 401:
                lockboss = lock_boss.Lock(cmd_list[:3])
                lockboss.boss_challenged()
                txt_list.extend(lockboss.txt_list)
        if swit == 0x3000:
            rsv = reserve.Reserve(cmd_list[:3])
            rsv.rsv(cmd, func)
            txt_list.extend(rsv.txt_list)
        return {
            "reply": "\n".join(txt_list),
            "block": True}
