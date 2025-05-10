import os
from dotenv import load_dotenv
import openai
import backoff

load_dotenv(dotenv_path=".env.txt")

client = openai.AsyncOpenAI()

@backoff.on_exception(backoff.expo, openai.RateLimitError)
async def make_api_call_to_gpt(prompt: str, model: str = "gpt-4o-2024-08-06"):
    """
    Exactly as in your original: wraps ChatCompletion.acreate with retries.
    """
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        timeout=20
    )
    return response.choices[0].message.content
