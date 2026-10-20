def compact_tool_results(messages, keep_last=3):
    tool_msgs = [m for m in messages if isinstance(m,dict) and m.get("role") == "tool"]
    for m in tool_msgs[:-keep_last]:
        if len(m["content"]) > 200:
             m["content"] = "[旧的工具结果已省略，如需要请重新调用工具获取]"