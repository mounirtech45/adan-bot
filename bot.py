import os
import asyncio

from pyrogram import Client, filters
from pytgcalls import PyTgPlayer
from pytgcalls.types.input_stream import AudioPiped

# --- الإعدادات ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 1866851228  # رقمك
GROUP_ID = -1001234567890  # رقم المجموعة

# --- تشغيل البوت ---
app = Client("radio", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- تشغيل الصوت ---
call = PyTgPlayer(app)

playing = False
current_link = None

# --- أوامر التحكم ---
@app.on_message(filters.private & filters.user(OWNER_ID))
async def commands(client, message):
    global playing, current_link

    if not message.text:
        return

    cmd = message.text.split()[0].lower()

    # ----- تشغيل -----
    if cmd == "/play":
        if len(message.command) < 2:
            await message.reply("❌ الرجاء إرسال رابط التشغيل بعد الأمر.\nمثال: `/play LINK`")
            return

        link = message.command[1]

        try:
            await call.join_group_call(
                GROUP_ID,
                AudioPiped(link)
            )
            playing = True
            current_link = link
            await message.reply(f"✅ جاري التشغيل: `{link}`")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء التشغيل:\n{e}")

    # ----- إيقاف -----
    elif cmd == "/stop":
        try:
            await call.leave_group_call(GROUP_ID)
            playing = False
            current_link = None
            await message.reply("🛑 تم إيقاف التشغيل")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء الإيقاف:\n{e}")

    # ----- الحالة -----
    elif cmd == "/status":
        if playing and current_link:
            await message.reply(f"▶️ يعمل حاليًا:\n`{current_link}`")
        else:
            await message.reply("⏹ متوقف حاليًا")

# --- بدء التشغيل ---
async def main():
    await app.start()
    await call.start()
    print("✅ BOT STARTED")
    await asyncio.get_event_loop().create_future()  # يبقي البوت يعمل

# --- تشغيل اللوب ---
asyncio.run(main())