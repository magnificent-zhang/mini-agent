import json
from pathlib import Path
import sys

def analyze_log(session_id):
    goal_file = Path(__file__).parent / "logs"
    with open(f"{goal_file}/{session_id}.jsonl", "r", encoding = "utf-8") as f:
        data = [json.loads(line) for line in f if line.strip()]
    times = 0
    prompt_tokens = 0
    completion_tokens = 0
    tool_calls = {}
    error_times = 0
    reject_times = 0
    total_time = 0
    for line in data:
        if line.get("type") == "model_call":
            times += 1
            prompt_tokens += line.get("prompt_tokens")
            completion_tokens += line.get("completion_tokens") or 0
        elif line.get("type") == "tool_call":
            name = line.get("name")
            tool_calls[name] = tool_calls.get(name, 0) + 1
            if line.get("isError") == True:
                error_times += 1
            if line.get("approved") == False:
                reject_times += 1
        if "seconds" in line:
            total_time += line.get("seconds")
    print(f"一共调用了{times}次模型，总共输入tokens：{prompt_tokens}，输出tokens：{completion_tokens}\n")
    for name, count in tool_calls.items():
        print(f"  {name}: {count} 次")
    print(f"失败了{error_times}次，拒绝了{reject_times}次\n")
    print(f"总耗时：{total_time:.2f}")

if __name__ == "__main__":
    analyze_log(sys.argv[1])