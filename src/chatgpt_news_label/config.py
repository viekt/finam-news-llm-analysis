import os
from dotenv import load_dotenv
import openai
import backoff

load_dotenv(dotenv_path=".env.txt")

api_key = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=api_key)

@backoff.on_exception(backoff.expo, openai.RateLimitError)
async def make_api_call_to_gpt(prompt: str, model: str = "gpt-4o-2024-08-06"):
    """
    Async function to make an API call to OpenAI's GPT model.
    """
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        timeout=20
    )
    return response.choices[0].message.content
