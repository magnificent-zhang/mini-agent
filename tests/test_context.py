import context
def test_compact_tool_results_zore():
    messages = []
    context.compact_tool_results(messages)
    assert messages == []

def test_compact_tool_results_two():
    messages = [{"role":"tool","content":"hi"},{"role":"tool","content":"hi"}]
    context.compact_tool_results(messages)
    assert messages == [{"role":"tool","content":"hi"},{"role":"tool","content":"hi"}]

def test_compact_tool_results_three():
    messages = [{"role":"tool","content":"我爱你。这三个字太轻，装不下我想说的全部。想说的是清晨的粥、深夜的灯，是你打喷嚏时我下意识递上的纸巾，是你皱眉时我先一步关掉的窗。我爱你，不在节日里，在每一天的琐碎里；不在誓言里，在一遍遍重复的、平淡的、认真的日常里。愿你收下这句笨拙的话，连同我余生的所有安静与热闹。如果有一天你忘了带伞，我就是那场及时赶到的雨；如果你嫌夜里太黑，我就把窗留着，让月光替你开着门。你不用回答，只要点点头，我就知道该往哪儿走。哪怕慢一点。"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"}]
    context.compact_tool_results(messages)
    assert messages == [{"role":"tool","content":"我爱你。这三个字太轻，装不下我想说的全部。想说的是清晨的粥、深夜的灯，是你打喷嚏时我下意识递上的纸巾，是你皱眉时我先一步关掉的窗。我爱你，不在节日里，在每一天的琐碎里；不在誓言里，在一遍遍重复的、平淡的、认真的日常里。愿你收下这句笨拙的话，连同我余生的所有安静与热闹。如果有一天你忘了带伞，我就是那场及时赶到的雨；如果你嫌夜里太黑，我就把窗留着，让月光替你开着门。你不用回答，只要点点头，我就知道该往哪儿走。哪怕慢一点。"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"}]

def test_compact_tool_results_five():
    messages = [{"role":"tool","content":"我爱你。这三个字太轻，装不下我想说的全部。想说的是清晨的粥、深夜的灯，是你打喷嚏时我下意识递上的纸巾，是你皱眉时我先一步关掉的窗。我爱你，不在节日里，在每一天的琐碎里；不在誓言里，在一遍遍重复的、平淡的、认真的日常里。愿你收下这句笨拙的话，连同我余生的所有安静与热闹。如果有一天你忘了带伞，我就是那场及时赶到的雨；如果你嫌夜里太黑，我就把窗留着，让月光替你开着门。你不用回答，只要点点头，我就知道该往哪儿走。哪怕慢一点。"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"},{"role":"tool","content":"我爱你。这三个字太轻，装不下我想说的全部。想说的是清晨的粥、深夜的灯，是你打喷嚏时我下意识递上的纸巾，是你皱眉时我先一步关掉的窗。我爱你，不在节日里，在每一天的琐碎里；不在誓言里，在一遍遍重复的、平淡的、认真的日常里。愿你收下这句笨拙的话，连同我余生的所有安静与热闹。如果有一天你忘了带伞，我就是那场及时赶到的雨；如果你嫌夜里太黑，我就把窗留着，让月光替你开着门。你不用回答，只要点点头，我就知道该往哪儿走。哪怕慢一点。"}]
    context.compact_tool_results(messages)
    assert messages == [{"role":"tool","content":"[旧的工具结果已省略，如需要请重新调用工具获取]"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"},{"role":"tool","content":"hi"},{"role":"tool","content":"我爱你。这三个字太轻，装不下我想说的全部。想说的是清晨的粥、深夜的灯，是你打喷嚏时我下意识递上的纸巾，是你皱眉时我先一步关掉的窗。我爱你，不在节日里，在每一天的琐碎里；不在誓言里，在一遍遍重复的、平淡的、认真的日常里。愿你收下这句笨拙的话，连同我余生的所有安静与热闹。如果有一天你忘了带伞，我就是那场及时赶到的雨；如果你嫌夜里太黑，我就把窗留着，让月光替你开着门。你不用回答，只要点点头，我就知道该往哪儿走。哪怕慢一点。"}]