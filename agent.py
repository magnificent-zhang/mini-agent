import os
import json
from openai import OpenAI
from datetime import datetime

client = OpenAI(
    api_key = os.environ["DEEPSEEK_API_KEY"],
    base_url = "https://api.deepseek.com",
)

MODEL = "deepseek-flash"

# 1. 一个普通的 Python 函数，这就是"工具"本身
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2. 一个普通的乘法函数
def multiply(a, b):
    return a * b

tools = [
    {
        "type":"function",
        "function": {
            "name": "get_current_time",
            "description":"获取现在的日期和时间",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "multiply",
            "description": "获取两个数的乘积。",
            "parameters":{
                "type":"object",
                "properties":{
                    "a": {"type": "number","description": "第一个乘数"},
                    "b": {"type": "number","description": "第二个乘数"}
                },
                "required":["a","b"],
            }
        }
    }
]

available_tools = {
    "get_current_time": get_current_time,
    "multiply": multiply,
}

messages = [{"role": "system","content": "You are a useful assistant."}]

while True:
    user_input = input("User:")
    if user_input in ["exit","quit"]:
        print("see you later")
        break
    if user_input == "":
        continue
    messages.append({"role":"user","content":user_input})
    i = 1 
    while True:
        if i > 10:
            print("超过最大轮数！")
            break
        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            tools = tools,
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                if name in available_tools:
                    func = available_tools[name]
                    args = json.loads(call.function.arguments)
                    result = str(func(**args))
                else:
                    result = "no useful tools exits"
                messages.append({
                    "role":"tool",
                    "tool_call_id":call.id,
                    "content":result,
                })
        else:
            print("model:",msg.content)
            messages.append({"role":"assistant","content":msg.content})
            break

