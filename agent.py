import os
import json
from openai import OpenAI
from tools import TOOLS, AVAILABLE_TOOLS, NEEDS_APPROVAL, safe_path
from context import compact_tool_results
from logger import log_event
import uuid
import time


client = OpenAI(
    api_key = os.environ["DEEPSEEK_API_KEY"],
    base_url = "https://api.deepseek.com",
)

MODEL = "deepseek-flash"
SYSTEM_PROMPT = "你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。环境为：Python 3.14"

def auto_approve(name, args):
    return True

def ask_approval(name, args):
    print(f"\n[需要审批] 工具：{name}")
    if name == "write_file":
        path = args.get("path")
        full = safe_path(path)
        if full.exists():
            print("将覆盖已有文件")
    if name == "edit_file":
        old_text = args.get("old_text")
        new_text = args.get("new_text")
        print(f"被修改的文本为：{old_text}\n修改后的文本为：{new_text}")
    if name == "run_command":
        command = args.get("command")
        print(f"运行的命令是：{command}")
    answer = input("是否允许？(y/n) ")
    return answer.strip().lower() == "y"

def run_agent_turn(messages,session_id,approve):
    i = 0
    final_answer = ""
    prompt_tokens_count = 0
    completion_tokens_count = 0
    isHitMaxSteps = False
    while True:
        if i >= 20:
            print("超过最大轮数！")
            isHitMaxSteps = True
            messages.append({"role":"assistant","content":"[任务未能在限定步数内完成]"})
            log_event(session_id,"max_steps",warning = "超过最大轮数限制")
            break
        i = i + 1
        compact_tool_results(messages)
        pre_time = time.perf_counter()
        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            tools = TOOLS,
        )
        next_time = time.perf_counter()
        msg = response.choices[0].message
        usage = response.usage
        prompt_tokens_count += usage.prompt_tokens
        completion_tokens_count += usage.completion_tokens
        # print(f"completion_token为：{usage.completion_tokens},prompt_token为：{usage.prompt_tokens}")
        log_event(session_id,"model_call",round = i,prompt_tokens = usage.prompt_tokens,completion_tokens = usage.completion_tokens,seconds = next_time - pre_time,isUseTools = True if msg.tool_calls else False)
        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                args = {}
                cost_time = 0
                isApproval = None
                isError = False
                if name not in AVAILABLE_TOOLS:
                    result = f"错误：工具 {name} 不存在。可用的工具有：{list(AVAILABLE_TOOLS.keys())}"
                else:
                    try:
                        args = json.loads(call.function.arguments)
                        isApproval = name not in NEEDS_APPROVAL or approve(name,args)
                        if not isApproval:
                            result = "用户拒绝了这次操作"
                        else:
                            pre_time = time.perf_counter()
                            result = str(AVAILABLE_TOOLS[name](**args))
                            next_time = time.perf_counter()
                            cost_time = next_time - pre_time
                    except Exception as e:
                        isError = True
                        result = f"工具执行出错：{type(e).__name__}:{e}"
                log_event(session_id,"tool_call",name = name,arguments = call.function.arguments,approved = isApproval ,result = result,seconds = cost_time,isError = isError)
                messages.append({
                    "role":"tool",
                    "tool_call_id":call.id,
                    "content":result,
                })
        else:
            final_answer = msg.content
            messages.append({"role":"assistant","content":msg.content})
            log_event(session_id,"final_answer",content = msg.content)
            break
    return {
        "final_answer": final_answer,
        "rounds": i,
        "prompt_tokens": prompt_tokens_count,
        "completion_tokens": completion_tokens_count,
        "hit_max_steps": isHitMaxSteps,
    }


def main():
    session_id = uuid.uuid4().hex[:8]
    messages = [{"role": "system","content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("User:")
        except (KeyboardInterrupt, EOFError):
            print()
            print("see you later")
            break
        if user_input.lower() in ["exit","quit"]:
            print("see you later")
            break
        if user_input == "":
            continue
        messages.append({"role":"user","content":user_input})
        log_event(session_id,"user_message",content = user_input)
        result = run_agent_turn(messages,session_id, approve = ask_approval)
        answer = (result["final_answer"] or "").strip()
        print("model:",answer if answer else "[模型返回了空内容]")
        

if __name__ == "__main__":
    main()

