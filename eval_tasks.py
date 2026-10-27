import subprocess
import sys


BUGGY_CODE = """def average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

scores = [90, 85, 77, 92]
print("平均分：", average(scores))
print('空列表的平均分：', average([]))

names = ["小明", "小红"]
print('第三个人是：', names[2])
"""

ADD_CODE = """a = 37
b = 4

def add(x, y):
    return x + y

print(add(a, b))
"""

DATA_TEXT = "12\n7\n30\n18\n9\n"

AVARAGE_CODE = """
def avarage(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)
"""

FACTORIAL_CODE = """
def factorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n 必须是非负整数")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
"""

def run_python(workspace,args):
    return subprocess.run(
        [sys.executable,*args],
        cwd=workspace, capture_output=True, text=True, timeout=10,
    )

def check_fix_buggy(workspace, result):
    r = run_python(workspace,["buggy.py"])
    return r.returncode == 0 and "86" in r.stdout

def check_create_factorial(workspace,result):
    if not (workspace / "factorial.py").exists():
        return False
    code = "from factorial import factorial; print(factorial(0), factorial(1), factorial(5), factorial(10))"
    r = run_python(workspace,['-c',code])
    if r.returncode != 0:
        return False
    last_line = r.stdout.strip().splitlines()[-1]
    return last_line == "1 1 120 3628800"

def check_edit_file(workspace,result):
    old_lines = ADD_CODE.splitlines()
    new_lines = (workspace / "add.py").read_text(encoding="utf-8").splitlines()
    if len(new_lines) != len(old_lines):
        return False
    for old,new in zip(old_lines,new_lines):
        if old.startswith("a ="):
            if new.replace(" ","") != "a=5":
                return False
        elif old != new:
            return False
    return True

def check_question(workspace,result):
    answer = result["final_answer"] or ""
    return "37" in answer


def check_more_steps(workspace,result):
    numbers = [float(x) for x in DATA_TEXT.split()]
    expected = sum(numbers) / len(numbers)
    answer = result["final_answer"] or ""
    wrote_script = any(workspace.glob("*.py"))
    return wrote_script and f"{expected:g}" in answer


TASKS = [
    {
        "id": "fix_buggy",
        "files": {"buggy.py": BUGGY_CODE},
        "prompt": "运行 buggy.py，如果报错就修好它，直到能正常运行为止。",
        "check": check_fix_buggy,
    },
    {
        "id":"create_factorial",
        "files":{},
        "prompt":"写一个函数 factorial(n) 计算 n 的阶乘，保存为 factorial.py。只写函数主要功能即可，不要写示例。",
        "check": check_create_factorial,
    },
    {
        "id":"edit_file",
        "files":{"add.py":ADD_CODE},
        "prompt":"把 add.py 中变量 a 的值改成 5，其他内容不要动。",
        "check":check_edit_file,
    },
    {
        "id":"question",
        "files":{"add.py":ADD_CODE},
        "prompt":"读一下 add.py，告诉我变量 a 的值是多少。",
        "check":check_question,
    },
    {
        "id":"more_steps",
        "files":{"data.txt":DATA_TEXT},
        "prompt":"读 data.txt 里的数字，写一个命名为：avarage.py的脚本算出平均值，运行它并告诉我结果",
        "check":check_more_steps,
    }
]

