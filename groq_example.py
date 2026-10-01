"""Optional standalone example. Not the app entry point."""
import os
from groq import Groq

if __name__ == "__main__":
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Explain the importance of fast language models"}],
        model="openai/gpt-oss-120b",
    )
    print(chat_completion.choices[0].message.content)
