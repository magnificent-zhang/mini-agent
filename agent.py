import os
import json
from openai import OpenAI
from tools import TOOLS, AVAILABLE_TOOLS, NEEDS_APPROVAL, ask_approval
from context import compact_tool_results
from logger import log_event
import uuid
import time


client = OpenAI(
    api_key = os.environ["DEEPSEEK_API_KEY"],
    base_url = "https://api.deepseek.com",
)

MODEL = "deepseek-flash"


def main():
    session_id = uuid.uuid4().hex[:8]
    messages = [{"role": "system","content": "你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。"}]

    while True:
        user_input = input("User:")
        if user_input.lower() in ["exit","quit"]:
            print("see you later")
            break
        if user_input == "":
            continue
        messages.append({"role":"user","content":user_input})
        log_event(session_id,"user_message",content = user_input)
        i = 0
        while True:
            if i > 20:
                print("超过最大轮数！")
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
            print(f"completions_token为：{usage.completion_tokens},prompt_token为：{usage.prompt_tokens}")
            log_event(session_id,"model_call",round = i,prompt_tokens = usage.prompt_tokens,completion_tokens = usage.completion_tokens,seconds = next_time - pre_time,isUseTools = True if msg.tool_calls else False)
            if msg.tool_calls:
                messages.append(msg)
                for call in msg.tool_calls:
                    name = call.function.name
                    args = {}
                    cost_time = 0
                    isApproval = False
                    isError = False
                    if name not in AVAILABLE_TOOLS:
                        result = f"错误：工具 {name} 不存在。可用的工具有：{list(AVAILABLE_TOOLS.keys())}"
                    else:
                        try:
                            args = json.loads(call.function.arguments)
                            isApproval = name not in NEEDS_APPROVAL or ask_approval(name,args)
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
                    log_event(session_id,"tool_call",name = name,arguments = call.function.arguments,approved = True if isApproval else False,result = result,seconds = cost_time,isError = isError)
                    messages.append({
                        "role":"tool",
                        "tool_call_id":call.id,
                        "content":result,
                    })
            else:
                print("model:",msg.content)
                messages.append({"role":"assistant","content":msg.content})
                log_event(session_id,"final_answer",content = msg.content)
                break

if __name__ == "__main__":
    main()

