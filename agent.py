import os
import json
from openai import OpenAI
from tools import TOOLS, AVAILABLE_TOOLS, NEEDS_APPROVAL, safe_path


client = OpenAI(
    api_key = os.environ["DEEPSEEK_API_KEY"],
    base_url = "https://api.deepseek.com",
)

MODEL = "deepseek-flash"

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
    answer = input("是否允许？(y/n) ")
    return answer.strip().lower() == "y"

messages = [{"role": "system","content": "你是一个说话简洁但精准的助手，修改已有文件时只用 edit_file。edit_file 失败时，先用 read_file 查看原文，再提供更精确的 old_text 重试，不要改用 write_file 重写整个文件。"}]

while True:
    user_input = input("User:")
    if user_input.lower() in ["exit","quit"]:
        print("see you later")
        break
    if user_input == "":
        continue
    messages.append({"role":"user","content":user_input})
    i = 0
    while True:
        if i > 10:
            print("超过最大轮数！")
            messages.append({"role":"assistant","content":"[任务未能在限定步数内完成]"})
            break
        i = i + 1
        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            tools = TOOLS,
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                if name not in AVAILABLE_TOOLS:
                    result = f"错误：工具 {name} 不存在。可用的工具有：{list(AVAILABLE_TOOLS.keys())}"
                else:
                    try:
                        args = json.loads(call.function.arguments)
                        if name in NEEDS_APPROVAL and not ask_approval(name,args):
                            result = "用户拒绝了这次操作"
                        else:
                            result = str(AVAILABLE_TOOLS[name](**args))
                    except Exception as e:
                        result = f"工具执行出错：{type(e).__name__}:{e}"
                messages.append({
                    "role":"tool",
                    "tool_call_id":call.id,
                    "content":result,
                })
        else:
            print("model:",msg.content)
            messages.append({"role":"assistant","content":msg.content})
            break


