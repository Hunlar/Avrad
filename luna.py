
import re
import os
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
    query = (
        query
        if LANGUAGE == "tr"
        else (await arq.translate(query, "en")).result.translatedText
    )

    resp = (await arq.luna(query, user_id)).result

    return (
        resp
        if LANGUAGE == "tr"
        else (
            await arq.translate(resp, LANGUAGE)
        ).result.translatedText
    )


async def type_and_send(message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    query = message.text.strip()

    normalized_query = query.casefold()

    if any(question in normalized_query for question in NAME_QUESTIONS):
        await message.reply_text("Ben Minnak! 🐾")
        return

    await message._client.send_chat_action(chat_id, "typing")

    response, _ = await gather(
        lunaQuery(query, user_id),
        sleep(2)
    )

    await message.reply_text(response)
    await message._client.send_chat_action(chat_id, "cancel")


@luna.on_message(filters.command("repo"))
async def repo(_, message):
    await message.reply_text(
        "[Emekli](https://t.me/emeklisanalci)"
        + " | [Group](t.me/ozturkordusu)",
        disable_web_page_preview=True,
    )


@luna.on_message(filters.command("help"))
async def start(_, message):
    await luna.send_chat_action(message.chat.id, "typing")
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

    if message.reply_to_message:
        replied = message.reply_to_message

        if replied.from_user and replied.from_user.id == bot_id:
            await type_and_send(message)
            return

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
    import asyncio
    asyncio.run(main())
