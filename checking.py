# import os

# api_key = "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"
# if api_key:
#     print("API Key found:", api_key[:6] + "..." + api_key[-4:])  # Partial print for security
# else:
#     print("API Key not found in environment variables.")
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="deepseek/deepseek-chat-v3-0324:free",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)
print(completion.choices[0].message.content)