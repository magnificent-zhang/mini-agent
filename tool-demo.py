import os
from datetime import datetime
from openai import OpenAI
import json

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"


# 1. 一个普通的 Python 函数，这就是"工具"本身
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2. 一个普通的乘法函数
def multiply(a, b):
    return a * b


# 2. 工具的"说明书"，是给模型看的
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的本地日期和时间。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
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

messages = [{"role": "user", "content": "现在几点？同时算一下小时数乘100"}]

available_tools = {
    "get_current_time": get_current_time,
    "multiply": multiply,
}

i = 1

while True:
    if i > 10:
        print("系统超过最大轮次")
        break
    i = i + 1
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        # 4. 先把模型这条"请求调用工具"的消息原样放回去
        messages.append(msg)

        # 5. 执行每一个工具调用，把结果作为 tool 消息放回去
        for call in msg.tool_calls:
            name = call.function.name
            if name in available_tools:
                func = available_tools[name]
                args = json.loads(call.function.arguments)
                result = str(func(**args))
            else:
                result = f"错误：没有名为{call.function.name}的工具"
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
    else:
        print("模型回答：", msg.content)
        break