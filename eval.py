import tempfile
from pathlib import Path
import tools
import eval_tasks
import agent
import time
import json
from datetime import datetime

EVAL_DIR = Path(__file__).parent / "eval_results"

now_time = datetime.now()

for task in eval_tasks.TASKS:
    success_times = 0
    avarage_cost_time = 0
    prompt_tokens = 0
    completion_tokens = 0
    for i in range(3):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp).resolve()
            tools.WORKSPACE = workspace
            if task.get("id") == "fix_buggy":
                messages = [{"role":"system","content":"你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"},{"role":"user","content":task.get("prompt")}]
                with open((workspace / "buggy.py"),"a",encoding = "utf-8") as f:
                    f.write(task["files"].get("buggy.py"))
                pre_time = time.perf_counter()
                result = agent.run_agent_turn(messages,i,agent.auto_approve)
                next_time = time.perf_counter()
                isTrue =  eval_tasks.check_fix_buggy(workspace,result)
                cost_time = next_time - pre_time
                if isTrue:
                    success_times += 1
                avarage_cost_time += cost_time
                prompt_tokens += result["prompt_tokens"]
                completion_tokens += result["completion_tokens"]
            elif task.get("id") == "create_factorial":
                messages = [{"role":"system","content":"你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"},{"role":"user","content":task.get("prompt")}]
                pre_time = time.perf_counter()
                result = agent.run_agent_turn(messages,i,agent.auto_approve)
                next_time = time.perf_counter()
                isTrue =  eval_tasks.check_create_factorial(workspace,result)
                cost_time = next_time - pre_time
                if isTrue:
                    success_times += 1
                avarage_cost_time += cost_time
                prompt_tokens += result["prompt_tokens"]
                completion_tokens += result["completion_tokens"]
            elif task.get("id") == "edit_file":
                messages = [{"role":"system","content":"你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"},{"role":"user","content":task.get("prompt")}]
                with open((workspace / "add.py"),"a",encoding = "utf-8") as f:
                    f.write(task["files"].get("add.py"))
                pre_time = time.perf_counter()
                result = agent.run_agent_turn(messages,i,agent.auto_approve)
                next_time = time.perf_counter()
                isTrue =  eval_tasks.check_edit_file(workspace,result)
                cost_time = next_time - pre_time
                if isTrue:
                    success_times += 1
                avarage_cost_time += cost_time
                prompt_tokens += result["prompt_tokens"]
                completion_tokens += result["completion_tokens"]
            elif task.get("id") == "question":
                messages = [{"role":"system","content":"你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"},{"role":"user","content":task.get("prompt")}]
                with open((workspace / "add.py"),"a",encoding = "utf-8") as f:
                    f.write(task["files"].get("add.py"))
                pre_time = time.perf_counter()
                result = agent.run_agent_turn(messages,i,agent.auto_approve)
                next_time = time.perf_counter()
                isTrue =  eval_tasks.check_question(workspace,result)
                cost_time = next_time - pre_time
                if isTrue:
                    success_times += 1
                avarage_cost_time += cost_time
                prompt_tokens += result["prompt_tokens"]
                completion_tokens += result["completion_tokens"]
            elif task.get("id") == "more_steps":
                messages = [{"role":"system","content":"你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"},{"role":"user","content":task.get("prompt")}]
                with open((workspace / "data.txt"),"a",encoding = "utf-8") as f:
                    f.write(task["files"].get("data.txt"))
                pre_time = time.perf_counter()
                result = agent.run_agent_turn(messages,i,agent.auto_approve)
                next_time = time.perf_counter()
                isTrue =  eval_tasks.check_more_steps(workspace,result)
                cost_time = next_time - pre_time
                if isTrue:
                    success_times += 1
                avarage_cost_time += cost_time
                prompt_tokens += result["prompt_tokens"]
                completion_tokens += result["completion_tokens"]
    print(f"任务：{task["id"]}，通过率为：{success_times / 3}，平均耗时：{avarage_cost_time / 3}，总prompt_tokens为：{prompt_tokens}，总completion_tokens为：{completion_tokens}")
    result = {
        "id":task["id"],
        "success_rate":{success_times / 3},
        "avarage_cost_time":{avarage_cost_time / 3},
        "prompt_tokens":{prompt_tokens},
        "completion_tokens":{completion_tokens},
    }
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

