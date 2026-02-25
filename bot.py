import os
import asyncio

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 1866851228
GROUP_ID = -1001234567890


app = Client("radio", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

call = PyTgCalls(app)

playing = False


# تشغيل رابط


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("play"))

async def play(client, message):

    global playing

    if len(message.command) < 2:

        await message.reply("ارسل الرابط")

        return


    link = message.command[1]


    await call.join_group_call(

        GROUP_ID,

        AudioPiped(link)

    )


    playing = True


    await message.reply("تم التشغيل")



# ايقاف


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))

async def stop(client, message):

    global playing

    await call.leave_group_call(GROUP_ID)

    playing = False

    await message.reply("تم الايقاف")



# الحالة


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("status"))

async def status(client, message):

    if playing:

        await message.reply("يعمل")

    else:

        await message.reply("متوقف")



app.start()

call.start()

print("BOT STARTED")

asyncio.get_event_loop().run_forever()