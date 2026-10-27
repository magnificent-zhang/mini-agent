from pathlib import Path
import tempfile
import eval_tasks as el

with tempfile.TemporaryDirectory() as tmp:
    print("check_edit_file的结果如下：\n")
    ws = Path(tmp)
    (ws / "add.py").write_text(el.ADD_CODE.replace("a = 37","a = 5"),encoding = "utf-8")
    print("正确修改：",el.check_edit_file(ws,{}))
    (ws / "add.py").write_text(el.ADD_CODE.replace("a = 37", "a = 5").replace("b = 4","b = 7"),encoding = "utf-8")
    print("错误修改：",el.check_edit_file(ws,{}))

with tempfile.TemporaryDirectory() as tmp:
    print("check_fix_buggy的结果如下：\n")
    ws = Path(tmp)
    (ws / "buggy.py").write_text(el.BUGGY_CODE.replace("print('空列表的平均分：', average([]))","").replace("print('第三个人是：', names[2])",""),encoding = "utf-8")
    print("正确修改：",el.check_fix_buggy(ws,{}))
    (ws / "buggy.py").write_text(el.BUGGY_CODE.replace("print('空列表的平均分：', average([]))",""),encoding = "utf-8")
    print("错误修改：",el.check_fix_buggy(ws,{}))

with tempfile.TemporaryDirectory() as tmp:
    print("check_create_factorial的结果如下：\n")
    ws = Path(tmp)
    open((ws / "factorial.py"),"w").close()
    Path((ws / "factorial.py")).write_text(el.FACTORIAL_CODE,encoding = "utf-8")
    print("正确创建：",el.check_create_factorial(ws,{}))
    Path(ws / "factorial.py").unlink()
    print("错误创建：",el.check_create_factorial(ws,{}))

with tempfile.TemporaryDirectory() as tmp:
    print("check_question的结果如下：\n")
    ws = Path(tmp)
    print("正确回答：",el.check_question(ws,{"final_answer": "37"}))
    print("错误回答：",el.check_question(ws,{"final_answer":"24"}))

with tempfile.TemporaryDirectory() as tmp:
    print("check_more_steps的结果如下：\n")
    ws = Path(tmp)
    with open((ws / "data.txt"),"w",encoding = "utf-8") as f:
        f.write(el.DATA_TEXT)
    with open((ws / "avarage.py"),"w",encoding = "utf-8") as f:
        f.write(el.AVARAGE_CODE)
    print("正确结果：",el.check_more_steps(ws,{"final_answer":"15.2"}))
    print("错误结果：",el.check_more_steps(ws,{"final_answer":"15"}))
