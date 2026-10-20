import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"


def log_event(session_id, event_type, **data):
    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session": session_id,
        "type": event_type,
        **data,
    }
    LOG_DIR.mkdir(exist_ok=True)
    try:
        line = json.dumps(record,ensure_ascii = False,default = str)
    except Exception as e:
        line = json.dumps({"time":record["time"],"session":record["session"],"type":record["type"],"error_mag":e})
    try:
        with open(LOG_DIR / f"{session_id}.jsonl","a",encoding = "utf-8") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"[警告]，日志写入失败：{e}")