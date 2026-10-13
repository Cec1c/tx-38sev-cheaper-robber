"""按当前日期拉起今天 10:00 与 15:00 两场后台监听.

用法: 在 D:\\tencentyun-allen 下执行  python launch_today.py
监听进程独立于本终端, 日志写入 run_1000.log / run_1500.log.
"""
import datetime
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
today = datetime.date.today().strftime("%Y-%m-%d")

for t, log in (("10:00:00", "run_1000.log"), ("15:00:00", "run_1500.log")):
    ts = f"{today} {t}"
    f = open(BASE / log, "a", encoding="utf-8")
    p = subprocess.Popen(
        [sys.executable, "-u", "snap_up_server.py", ts],
        cwd=str(BASE), stdout=f, stderr=subprocess.STDOUT,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print(f"已启动 {ts} 场监听 PID={p.pid} -> {log}")
print("完成。开抢前可随时看日志确认存活。")
