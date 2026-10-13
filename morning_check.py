"""早上开抢前自检: 登录态 / 人脸核身 / 购买资格 / 今日场次 business id.

用法: 在 D:\\tencentyun-allen 下执行  python morning_check.py
全绿后再运行 launch_today.py 拉起两场监听.
"""
import sys
from datetime import datetime

import snap_up_server as srv

BASE = "https://act-api.cloud.tencent.com"


def main():
    ok_all = True
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    print(f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        session, csrf, src = srv.build_session()
    except Exception as e:
        print(f"❌ cookies.json 加载失败: {e}")
        print("   → 需重新扫码登录: python get_cookies.py")
        return 1
    headers = srv.make_headers(csrf)
    print(f"凭据: {src}")

    # 1) 登录态
    try:
        r = session.post(BASE + "/user/get-vip-info", json={}, headers=headers, timeout=15)
        code = str(r.json().get("code"))
    except Exception as e:
        code = f"ERR {e}"
    logged = code == "0"
    ok_all &= logged
    print(("✅" if logged else "❌") + f" 登录态: code={code}"
          + ("" if logged else "  → 需重新扫码: python get_cookies.py"))

    # 2) 人脸核身
    face = srv.check_face(session, headers)
    ok_all &= face is True
    mark = "✅" if face is True else ("❌ 未通过" if face is False else "⚠️ 查询失败")
    print(f"{mark} 人脸核身: ever_pass={face}")
    if face is False:
        print("   → https://cloud.tencent.com/act/pro/face_authentication 完成核身, 否则抢购必报 1100202")

    # 3) 购买资格
    try:
        check = {
            "activity_id": srv.CONFIG["ACTIVITY_ID"],
            "goods": [{"act_id": srv.CONFIG["CHECK_ACT_ID"], "region_id": [1, 4, 8]}],
            "preview": 0,
        }
        d = session.post(BASE + "/dianshi/check-available", json=check,
                         headers=headers, timeout=15).json()
        g = (d.get("data") or [{}])[0]
        elig = str(g.get("user_available")) == "1"
        ok_all &= elig
        print(("✅" if elig else "❌") + f" 购买资格: user_available={g.get('user_available')}"
              f" idcard_available={g.get('idcard_available')}")
    except Exception as e:
        print(f"⚠️ 资格查询失败: {e}")

    # 4) 今日场次 business id
    try:
        r = session.post(BASE + "/dianshi/query-seckill-by-date",
                         json={"activity_id": srv.CONFIG["ACTIVITY_ID"], "preview": 0,
                               "seckill_type": "block", "goods_type": "goods", "days": 3},
                         headers=headers, timeout=15)
        flash = (r.json().get("data") or {}).get("flashResult") or {}
        got = {s.get("start_time"): s.get("id") for s in flash.get(today, [])}
        for t in ("10:00:00", "15:00:00"):
            bid = got.get(t)
            ok_all &= bool(bid)
            print(("✅" if bid else "❌") + f" 今日 {t[:5]} 场: business_id={bid}")
    except Exception as e:
        print(f"⚠️ 场次查询失败: {e}")

    print()
    if ok_all:
        print("== 全绿！启动两场监听: python launch_today.py ==")
        return 0
    print("== 有 ❌ 项未通过，先处理再启动！ ==")
    return 1


if __name__ == "__main__":
    sys.exit(main())
