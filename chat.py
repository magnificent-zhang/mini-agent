import os
from openai import OpenAI

client = OpenAI(
    api_key = os.environ['DEEPSEEK_API_KEY'],
    base_url = "https://api.deepseek.com",
)


messages = [{"role": "system", "content": "你是一个说话简洁但精准的助手。"}]
    
while True:
    user_input = input("User:")
    if user_input.lower() in ["exit", "quit"]:
        break
    if user_input == "":
        continue
    messages.append({"role": "user", "content": user_input})
    # messages_least = messages[-6:]  # Keep only the last 6 messages for context 会出现system消息重复的问题
    recent = messages[1:][-7:]
    print("recent:", recent)
    response = client.chat.completions.create(
        model = "deepseek-flash",
        messages = messages[:1] + recent  # Include the system message for context,
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    print(reply)
    print(response.usage)

