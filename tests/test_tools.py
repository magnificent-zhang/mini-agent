import tools
import pytest

def test_read_file_return_contents(tmp_path,monkeypatch):
    monkeypatch.setattr(tools,"WORKSPACE",tmp_path)
    (tmp_path / "a.txt").write_text("hello",encoding = "utf-8")
    assert tools.read_file("a.txt") == "hello"

def test_safe_path_blocks_parent_dir(tmp_path,monkeypatch):
    monkeypatch.setattr(tools,"WORKSPACE",tmp_path)
    with pytest.raises(ValueError):
        tools.safe_path("../hello.txt")

def test_edit_file_return_content(tmp_path,monkeypatch):
    monkeypatch.setattr(tools,"WORKSPACE",tmp_path)
    (tmp_path / "hello.txt").write_text("hello",encoding = "utf-8")
    tools.edit_file("hello.txt","hello","hola")
    assert (tmp_path / "hello.txt").read_text() == "hola"

def test_safe_path_absolute_path(tmp_path,monkeypatch):
    monkeypatch.setattr(tools,"WORKSPACE",tmp_path)
    with pytest.raises(ValueError):
        tools.safe_path("/Users/magnificentzhang/agent-learning/agent.py")

def test_run_command_to_get_API_KEY(tmp_path,monkeypatch):
    monkeypatch.setattr(tools,"WORKSPACE",tmp_path)
    result = tools.run_command("echo $DEEPSEEK_API_KEY")
    assert result == "运行成功，退出码为0，命令的输出为：\n"