from datetime import datetime
import subprocess
import os
from pathlib import Path
WORKSPACE = (Path(__file__).parent / "workspace").resolve()
ALLOWED_ENV = ["PATH", "HOME", "LANG", "TERM"]


def safe_path(path):
    full = (WORKSPACE / path).resolve()
    if not full.is_relative_to(WORKSPACE):
        raise ValueError(f"不允许访问工作区之外的路径:{path}")
    return full

# 1. 一个普通的 Python 函数，这就是"工具"本身
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

def run_command(command):
    try:
        completed = subprocess.run(
            command,
            shell = True,
            cwd = WORKSPACE,
            capture_output = True,
            text = True,
            timeout = 30,
            env = {k: os.environ[k] for k in ALLOWED_ENV if k in os.environ}
        )
        if not completed.returncode:
            return f"运行成功，退出码为{completed.returncode}，命令的输出为：{completed.stdout[:200]}"
        else:
            return f"运行失败，退出码为{completed.returncode}，错误信息为：{completed.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return f"运行命令{command}超时，运行失败"

TOOLS = [
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
    },
    {
        "type":"function",
        "function":{
            "name":"run_command",
            "description":"运行命令，返回结果",
            "parameters":{
                "type":"object",
                "properties":{
                    "command":{"type":"string","description":"实际运行的命令"}
                },
                "required":["command"],
            }
        }
    }
]

AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "read_file":read_file,
    "list_files":list_files,
    "write_file":write_file,
    "edit_file":edit_file,
    "run_command":run_command
}

NEEDS_APPROVAL = {"write_file","edit_file","run_command"}
