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
    if len(content) > 5000:
        return content[:5000] + "[文件过长，已截断，仅显示前 5000 个字符]"
    else:
        return content

def list_files(path):
    full = safe_path(path)
    names = [p.name + ("/" if p.is_dir() else "") for p in full.iterdir()]
    return "\n".join(names)

def write_file(path,content):
    full = safe_path(path)
    full.parent.mkdir(parents = True,exist_ok = True)
    full.write_text(content,encoding="utf-8")
    return f"已写入{path},共{len(content)}个字符"

def edit_file(path,old_text,new_text):
    full = safe_path(path)
    content = full.read_text(encoding="utf-8")
    times = content.count(old_text)
    if times == 0:
        return "没找到这段原文，请先用 read_file 确认文件内容"
    elif times > 1:
        return f"这段文本出现了 {times} 次，请提供更多上下文使它唯一"
    else:
        full.write_text(content.replace(old_text, new_text), encoding="utf-8")
        return "编辑成功"

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
                    "path":{"type":"string","description":"相对于工作区的文件夹路径，列出工作区根目录请用."}
                },
                "required":["path"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"write_file",
            "description":"创建新文件，或完整重写文件。修改已有文件的局部内容请用 edit_file",
            "parameters":{
                "type":"object",
                "properties":{
                    "path":{"type":"string","description":"相对于工作区的文件路径，例如 work/hello.txt"},
                    "content":{"type":"string","description":"需要被写进新文件的内容"}
                },
                "required":["path","content"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"edit_file",
            "description":"把文件中的一段原文替换为新文本。old_text 必须与文件中的内容完全一致（包括空格和换行），并且在文件中只出现一次。修改前请先用 read_file 查看原文。",
            "parameters":{
                "type":"object",
                "properties":{
                    "path":{"type":"string","description":"相对于工作区的文件路径，例如 work/hello.txt"},
                    "old_text":{"type":"string","description":"需要变更修改的旧内容"},
                    "new_text":{"type":"string","description":"需要编辑替换的新内容"}
                },
                "required":["path","old_text","new_text"]
            }
        }
    }
]

available_tools = {
    "get_current_time": get_current_time,
    "multiply": multiply,
    "divide": divide,
    "read_file":read_file,
    "list_files":list_files,
    "write_file":write_file,
    "edit_file":edit_file
}

NEEDS_APPROVAL = {"write_file","edit_file"}

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
            tools = tools,
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                if name not in available_tools:
                    result = f"错误：工具 {name} 不存在。可用的工具有：{list(available_tools.keys())}"
                else:
                    try:
                        args = json.loads(call.function.arguments)
                        if name in NEEDS_APPROVAL and not ask_approval(name,args):
                            result = "用户拒绝了这次操作"
                        else:
                            result = str(available_tools[name](**args))
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


