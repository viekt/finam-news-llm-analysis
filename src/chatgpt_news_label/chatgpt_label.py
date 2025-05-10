import pandas as pd
import asyncio
import json

from .config import make_api_call_to_gpt

def create_prompt(group: pd.DataFrame) -> str:
    prompt = f"""Забудь все предыдущие инструкции. Ты финансовый эксперт с опытом рекомендации на российском рынке акций. 
Проанализируй следующие новости в России, чтобы оценить ее влияние на цену акций {group.shortname.iloc[0]}.
Ответь одним из трех вариантов: «ВВЕРХ», если новости позитивно повлияют. «ВНИЗ», если новости негативно повлияютя. «НЕИЗВЕСТНО», если новости, скорее всего, не окажут существенного влияния.\n"""
    count = 1
    for _, row in group.iterrows():
        prompt += f"Новость {count} : {row['title']}\nТекст: {row['text']}\n"
        count += 1
    prompt += 'Верни сначала только единый сигнал для всех новостей компании.'
    return prompt

def parse_signal(response: str) -> tuple[int | None, str]:
    response_low = response.replace('*', '').lower()
    if response_low.startswith("вверх"):
        return 1, response.strip()
    elif response_low.startswith("вниз"):
        return -1, response.strip()
    elif response_low.startswith("неизвестно"):
        return 0, response.strip()
    elif response_low.find('сигнал: вверх') != -1:
        return 1, response.strip()
    elif response_low.find('сигнал: вниз') != -1:
        return -1, response.strip()
    elif response_low.find('сигнал: неизвестно') != -1:
        return 0, response.strip()
    else:
        down = response_low.count('вниз')
        up = response_low.count('вверх')
        undetected = response_low.count('неизвестно')
        decision = {1: up, -1: down, 0: undetected}
        print(decision, max(decision, key=decision.get))
        return max(decision, key=decision.get), response 

async def _run_all(prompts: list[str], model: str):
    tasks = [make_api_call_to_gpt(p, model=model) for p in prompts]
    return await asyncio.gather(*tasks)

def run(
    input_excel: str,
    output_xlsx: str,
    model: str = "gpt-4o-2024-08-06"
):
    df = pd.read_excel(input_excel)
    df['date'] = pd.to_datetime(df['date'])
    df['date_only_trading'] = df['trading_time'].dt.date

    grouped = (
        df
        .groupby(['ticker', 'date_only_trading'])
        .apply(create_prompt)
        .reset_index(name='combined_prompt')
    )
    prompts = grouped['combined_prompt'].tolist()

    responses = asyncio.run(_run_all(prompts, model))

    signals_expls = [parse_signal(resp) for resp in responses]
    signals, explanations = zip(*signals_expls)
    grouped['signal'] = signals
    grouped['explanation'] = explanations

    df_out = pd.merge(
        df,
        grouped[['ticker', 'date_only_trading', 'signal', 'explanation']],
        on=['ticker', 'date_only_trading'],
        how='right'
    )

    df_out.to_excel(output_xlsx, index=False)
