import os
from openai import OpenAI

client = OpenAI(
    api_key = os.environ['DEEPSEEK_API_KEY'],
    base_url = "https://api.deepseek.com",
)

stream = client.chat.completions.create(
    model = "deepseek-flash",
    messages = [{"role": "user", "content": "用三句话形容一下长城。"}],
    stream = True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)

print()