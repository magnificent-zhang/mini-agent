import tempfile
from pathlib import Path
import tools
import eval_tasks
import agent


for task in eval_tasks.TASKS:
    for i in range(3):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tools.WORKSPACE = workspace
            if task.get("file")["buggy.py"]:
                workspace.mkdir("buggy.py",encoding = "utf-8")
                (workspace / "buggy.py").write_text(eval_tasks.BUGGY_CODE)
