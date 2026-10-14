import os
from openai import OpenAI

client = OpenAI(
    api_key = os.environ['DEEPSEEK_API_KEY'],
    base_url = "https://api.deepseek.com",
)


messages = [{"role": "system", "content": "你是一个说话简洁但精准的助手。"}]
    
while True:
    try:
        user_input = input("User:")
    except:
        print()
        print("再见")
        break
    if user_input.lower() in ["exit", "quit"]:
        break
    if user_input == "":
        continue
    messages.append({"role": "user", "content": user_input})
    # messages_least = messages[-6:]  # Keep only the last 6 messages for context 会出现system消息重复的问题
    recent = messages[1:][-7:]
    response = None
    reply = ""
    try:
        response = client.chat.completions.create(
            model = "deepseek-flash",
            messages = messages[:1] + recent,  # Include the system message for context,
            stream = True,
            stream_options = {
                "include_usage": True
            }
        )
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta.content
                if delta:
                    print(delta,end="",flush=True)
                    reply += delta
            if chunk.usage:
                print()
                print(chunk.usage)
        messages.append({"role": "assistant", "content": reply})
    except KeyboardInterrupt:
        if response:
            response.close()
        messages.append({"role":"assistant","content":reply + "\n[被用户中断]"})
        response.close()
        print(messages)
    print()

