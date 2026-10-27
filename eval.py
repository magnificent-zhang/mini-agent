import tempfile
from pathlib import Path
import tools
import eval_tasks
import agent
import time
import json
from datetime import datetime

EVAL_DIR = Path(__file__).parent / "eval_results"

now_time = datetime.now().strftime("%Y%m%d-%H%M%S")

def run_once(task, run_index, approve):
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp).resolve()
        tools.WORKSPACE = workspace
        for name, content in task["files"].items():
            (workspace / name).write_text(content, encoding="utf-8")

        messages = [
            {"role": "system", "content": agent.SYSTEM_PROMPT},
            {"role": "user", "content": task["prompt"]},
        ]
        session_id = f"eval-{task['id']}-{run_index}"
        start = time.perf_counter()
        try:
            result = agent.run_agent_turn(messages, session_id, approve)
            passed = task["check"](workspace, result)
            error = None
        except Exception as e:
            result = {"rounds": 0, "prompt_tokens": 0, "completion_tokens": 0, "hit_max_steps": False}
            passed = False
            error = f"{type(e).__name__}: {e}"

        return {
            "task": task["id"],
            "run": run_index,
            "passed": passed,
            "seconds": time.perf_counter() - start,
            "rounds": result["rounds"],
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "hit_max_steps": result["hit_max_steps"],
            "error": error,
        }

for task in eval_tasks.TASKS:
    success_times = 0
    avarage_cost_time = 0
    prompt_tokens = 0
    completion_tokens = 0
    for i in range(3):
        result = run_once(task,i+1,agent.auto_approve)
        try:
            line = json.dumps(result,ensure_ascii = False,default = str)
        except Exception as e:
            line = json.dumps({
                "id":task["id"],
                "error": f"{type(e).__name__}: {e}",
            },ensure_ascii = False)
        try:
            with open(EVAL_DIR / f"{now_time}.jsonl","a",encoding = "utf-8") as f:
                f.write(line + "\n")
        except OSError as e:
            print(f"[警告]，日志写入失败：{e}")

