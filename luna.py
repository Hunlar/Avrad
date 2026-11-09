
import os
import asyncio
from asyncio import gather, sleep

from aiohttp import ClientSession
from pyrogram import Client, filters, idle
from Python_ARQ import ARQ

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

luna = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)

bot_id = int(bot_token.split(":")[0])
arq = None

KEYWORDS = [
    "minnak",
    "adsız",
    "yenge",
    "öztürk",
    "sikes",
    "emre",
    "can",
    "atilla",
    "q7",
    "qua",
]

NAME_QUESTIONS = [
    "adın ne",
    "adın nedir",
    "ismin ne",
    "ismin nedir",
    "sen kimsin",
    "kim olduğunu söyle",
]


async def lunaQuery(query: str, user_id: int):
    try:
        print(f"ARQ REQUEST | User: {user_id} | Query: {query}")

        if LANGUAGE != "tr":
            translated = await arq.translate(query, "en")
            query = translated.result.translatedText

        result = await arq.luna(query, user_id)

        print(f"ARQ RAW RESPONSE: {result}")

        resp = result.result

        if not resp:
            raise ValueError("ARQ boş yanıt döndürdü.")

        if LANGUAGE != "tr":
            translated = await arq.translate(resp, LANGUAGE)
            resp = translated.result.translatedText

        return resp

    except Exception as e:
        print(f"ARQ ERROR: {type(e).__name__}: {e}")
        raise


async def type_and_send(message):
    user_id = message.from_user.id if message.from_user else 0
    query = message.text.strip()

    normalized_query = query.casefold()

    if any(question in normalized_query for question in NAME_QUESTIONS):
        await message.reply_text("Ben Minnak! 🐾")
        return

    try:
        response, _ = await gather(
            lunaQuery(query, user_id),
            sleep(2)
        )

        await message.reply_text(response)

    except Exception as e:
        print(f"MESSAGE ERROR: {type(e).__name__}: {e}")

        await message.reply_text(
            "Şu anda cevap veremiyorum. Biraz sonra tekrar dene."
        )


@luna.on_message(filters.command("repo"))
async def repo(_, message):
    await message.reply_text(
        "[Emekli](https://t.me/emeklisanalci)"
        + " | [Group](https://t.me/ozturkordusu)"
    )


@luna.on_message(filters.command("help"))
async def start(_, message):
    await sleep(2)
    await message.reply_text("/repo - Get Repo Link")


@luna.on_message(
    ~filters.private
    & filters.text
    & ~filters.command("help"),
    group=69,
)
async def chat(_, message):
    if not message.text:
        return

    # Botun kendi mesajına yanıt verilirse cevap ver.
    if message.reply_to_message:
        replied = message.reply_to_message

        if replied.from_user and replied.from_user.id == bot_id:
            await type_and_send(message)
            return

    # Belirlenen kelimelerden biri geçerse cevap ver.
    text = message.text.casefold()

    if any(keyword in text for keyword in KEYWORDS):
        await type_and_send(message)


@luna.on_message(
    filters.private & ~filters.command("help")
)
async def chatpm(_, message):
    if not message.text:
        return

    await type_and_send(message)


async def main():
    global arq

    session = ClientSession()
    arq = ARQ(ARQ_API_BASE_URL, ARQ_API_KEY, session)

    try:
        await luna.start()

        print(
            """
-----------------
| Minnak Started! |
-----------------
"""
        )

        await idle()

    finally:
        await luna.stop()
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
