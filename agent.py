import os
import json
from openai import OpenAI
from datetime import datetime
from pathlib import Path


client = OpenAI(
    api_key = os.environ["DEEPSEEK_API_KEY"],
    base_url = "https://api.deepseek.com",
)

MODEL = "deepseek-flash"

WORKSPACE = Path("workspace").resolve()

def safe_path(path):
    full = (WORKSPACE / path).resolve()
    if not full.is_relative_to(WORKSPACE):
        raise ValueError(f"不允许访问工作区之外的路径:{path}")
    return full

# 1. 一个普通的 Python 函数，这就是"工具"本身
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2. 一个普通的乘法函数
def multiply(a, b):
    return a * b

def divide(a,b):
    return a / b

def read_file(path):
    full = safe_path(path)
    content = full.read_text(encoding="utf-8")
    return content[:5000]

def list_files(path):
    full = safe_path(path)
    names = [p.name + ("/" if p.is_dir() else "") for p in full.iterdir()]
    return "\n".join(names)


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
    },
    {
        "type":"function",
        "function":{
            "name":"divide",
            "description":"获取两个数的商",
            "parameters":{
                "type":"object",
                "properties":{
                    "a":{"type":"number","description":"被除数"},
                    "b":{"type":"number","description":"除数"},
                },
                "required":["a","b"],
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"read_file",
            "description":"读一个指定文件的内容",
            "parameters":{
                "type":"object",
                "properties":{
                    "path":{"type":"string","description":"相对于工作区的文件路径，例如 notes.txt"}
                },
                "required":["path"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"list_files",
            "description":"列举一个指定文件夹中的文件名称",
            "parameters":{
                "type":"object",
                "properties":{
                    "path":{"type":"string","description":"相对于工作区的文件夹路径，列出工作区根目录请用"}
                },
                "required":["path"]
            }
        }
    }
]

available_tools = {
    "get_current_time": get_current_time,
    "multiply": multiply,
    "divide": divide,
    "read_file":read_file,
    "list_files":list_files
}

messages = [{"role": "system","content": "You are a useful assistant."}]

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
        if i > 1:
            print("超过最大轮数！")
            messages.append({"role":"assistant","content":"[任务未能在限定步数内完成]"})
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
                    try:
                        args = json.loads(call.function.arguments)
                        result = str(func(**args))
                    except Exception as e:
                        result = f"工具执行出错：{type(e).__name__}:{e}"
                else:
                    result = f"错误：工具 {name} 不存在。可用的工具有：{list(available_tools.keys())}"
                messages.append({
                    "role":"tool",
                    "tool_call_id":call.id,
                    "content":result,
                })
        else:
            print("model:",msg.content)
            messages.append({"role":"assistant","content":msg.content})
            break


