import os
import logging
import sqlite3
import requests
import asyncio
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- الإعدادات ---
# تأكد من إضافة BOT_TOKEN في Variables على Railway
TOKEN = os.getenv("BOT_TOKEN")

# تعطيل السجلات الكثيفة لمنع حظر Railway
logging.basicConfig(level=logging.ERROR)

ADHAN_AUDIO = {
    "Fajr": "https://server8.mp3quran.net/afs/Adhan/01.mp3",
    "Dhuhr": "https://server8.mp3quran.net/afs/Adhan/02.mp3",
    "Asr": "https://server8.mp3quran.net/afs/Adhan/02.mp3",
    "Maghrib": "https://server8.mp3quran.net/afs/Adhan/02.mp3",
    "Isha": "https://server8.mp3quran.net/afs/Adhan/02.mp3"
}

STICKERS = {
    "Fajr": "CAACAgQAAxkBAANaaEMp1nVujJp0Z-rxg4d8unkb7L0AAtMOAALgEGFSn-ixyIDYFSg2BA",
    "Dhuhr": "CAACAgQAAxkBAANbaEMp1kJWRrCaYpEmQhubsqxJnkIAAvQPAAJE61lSE6aASL7IfBs2BA",
    "Asr": "CAACAgQAAxkBAANcaEMp1tfSAAEOPClpo7AAAV5N9709gwACFw4AAv2FYVK3WVAYkk8bODYE",
    "Maghrib": "CAACAgQAAxkBAANdaEMp1siOebpjHVecdHntLANUox0AAr0NAALd0GFSNjnQDxqQ3fg2BA",
    "Isha": "CAACAgQAAxkBAANeaEMp1ltI2C7vDrInimOS54iM51gAAl8PAAINlGBSpL2XDMeGEUw2BA"
}

HADITHS = {
    "Fajr": "«ركعتا الفجر خير من الدنيا وما فيها».",
    "Dhuhr": "«هذا أوان تُفتح فيه أبواب السماء».",
    "Asr": "«من صلى البردين دخل الجنة».",
    "Maghrib": "«لا تزال أمتي بخير ما لم يؤخروا المغرب حتى تشتبك النجوم».",
    "Isha": "«ولو يعلمون ما في العِشاءِ والصُّبحِ لأتَوْهُما ولو حَبْوًا»."
}

ALGERIA_STATES = [
    ("Adrar", "01 أدرار"), ("Chlef", "02 الشلف"), ("Laghouat", "03 الأغواط"), ("Oum_El_Bouaghi", "04 أم البواقي"),
    ("Batna", "05 باتنة"), ("Bejaia", "06 بجاية"), ("Biskra", "07 بسكرة"), ("Bechar", "08 بشار"),
    ("Blida", "09 البليدة"), ("Bouira", "10 البويرة"), ("Tamanrasset", "11 تمنراست"), ("Tebessa", "12 تبسة"),
    ("Tlemcen", "13 تلمسان"), ("Tiaret", "14 تيارت"), ("Tizi_Ouzou", "15 تيزي وزو"), ("Algiers", "16 الجزائر"),
    ("Djelfa", "17 الجلفة"), ("Jijel", "18 جيجل"), ("Setif", "19 سطيف"), ("Saida", "20 سعيدة"),
    ("Skikda", "21 سكيكدة"), ("Sidi_Bel_Abbes", "22 سيدي بلعباس"), ("Annaba", "23 عنابة"), ("Guelma", "24 قالمة"),
    ("Constantine", "25 قسنطينة"), ("Medea", "26 المدية"), ("Mostaganem", "27 مستغانم"), ("MSila", "28 المسيلة"),
    ("Mascara", "29 معسكر"), ("Ouargla", "30 ورقلة"), ("Oran", "31 وهران"), ("El_Bayadh", "32 البيض"),
    ("Illizi", "33 إليزي"), ("Bordj_Bou_Arreridj", "34 برج بوعريريج"), ("Boumerdes", "35 بومرداس"), ("El_Tarf", "36 الطارف"),
    ("Tindouf", "37 تندوف"), ("Tissemsilt", "38 تيسمسيلت"), ("El_Oued", "39 الوادي"), ("Khenchela", "40 خنشلة"),
    ("Souk_Ahras", "41 سوق أهراس"), ("Tipaza", "42 تيبازة"), ("Mila", "43 ميلة"), ("Ain_Defla", "44 عين الدفلى"),
    ("Naama", "45 النعامة"), ("Ain_Temouchent", "46 عين تموشنت"), ("Ghardaia", "47 غرداية"), ("Relizane", "48 غليزان"),
    ("Timimoun", "49 تيميمون"), ("Bordj_Badji_Mokhtar", "50 برج باجي مختار"), ("Ouled_Djellal", "51 أولاد جلال"),
    ("Beni_Abbes", "52 بني عباس"), ("In_Salah", "53 عين صالح"), ("In_Guezzam", "54 عين قزام"),
    ("Touggourt", "55 توقرت"), ("Djanet", "56 جانت"), ("El_Mghair", "57 المغير"), ("El_Meniaa", "58 المنيعة")
]

def init_db():
    conn = sqlite3.connect('prayer.db')
    conn.cursor().execute('CREATE TABLE IF NOT EXISTS subs (chat_id INTEGER PRIMARY KEY, city_en TEXT, city_ar TEXT, tz TEXT)')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("⚠️ البوت يعمل في المجموعات والقنوات فقط.")
        return
    await send_page(update, 0)

async def send_page(update, start_idx):
    keyboard = []
    end_idx = start_idx + 20
    page_states = ALGERIA_STATES[start_idx:end_idx]
    for i in range(0, len(page_states), 2):
        row = [InlineKeyboardButton(page_states[i][1], callback_data=f"set_{page_states[i][0]}_{page_states[i][1]}")]
        if i + 1 < len(page_states):
            row.append(InlineKeyboardButton(page_states[i+1][1], callback_data=f"set_{page_states[i+1][0]}_{page_states[i+1][1]}"))
        keyboard.append(row)
    
    nav = []
    if start_idx > 0: nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"p_{start_idx-20}"))
    if end_idx < len(ALGERIA_STATES): nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"p_{end_idx}"))
    if nav: keyboard.append(nav)

    if update.message:
        await update.message.reply_text("📍 اختر الولاية لضبط مواقيت الصلاة:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text("📍 اختر الولاية لضبط مواقيت الصلاة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("p_"):
        await send_page(update, int(query.data.split("_")[1]))
        return
    
    _, en, ar = query.data.split("_")
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={en.replace('_',' ')}&country=Algeria").json()
    tz = res['data']['meta']['timezone']
    
    conn = sqlite3.connect('prayer.db')
    conn.cursor().execute("REPLACE INTO subs VALUES (?, ?, ?, ?)", (query.message.chat_id, en, ar, tz))
    conn.commit()
    conn.close()
    await query.edit_message_text(f"✅ تم بنجاح ضبط مواقيت الصلاة لولاية: {ar}")

async def prayer_cron(context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('prayer.db')
    subs = conn.cursor().execute("SELECT * FROM subs").fetchall()
    conn.close()

    for chat_id, en, ar, tz in subs:
        try:
            now = datetime.now(pytz.timezone(tz)).strftime("%H:%M")
            res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={en.replace('_',' ')}&country=Algeria&method=3").json()
            t, h, m = res['data']['timings'], res['data']['date']['hijri'], res['data']['date']['gregorian']
            
            p_map = {"Fajr":"الفجر", "Dhuhr":"الظهر", "Asr":"العصر", "Maghrib":"المغرب", "Isha":"العشاء"}
            for k, v in p_map.items():
                if now == t[k]:
                    # 1. إرسال الملصق وحده أولاً
                    await context.bot.send_sticker(chat_id=chat_id, sticker=STICKERS[k])
                    
                    # 2. تجهيز النص
                    caption_text = f"🕌 تذكير صلاة {v}\n📍 المدينة: {ar}\n🕒 التوقيت: {t[k]}\n\n📅 هجري: {h['day']} {h['month']['ar']} {h['year']}\n📆 ميلادي: {m['date']}\n\nـــــــــــــــــــــــــــــــــــــ\n🌌 {HADITHS[k]}\nـــــــــــــــــــــــــــــــــــــ\n\n▪️ تقبل الله منا ومنكم\n🎙 بصوت: مشاري راشد العفاسي"
                    
                    # 3. إرسال الصوت وبداخله النص
                    await context.bot.send_audio(chat_id=chat_id, audio=ADHAN_AUDIO[k], caption=caption_text)
                    await asyncio.sleep(61)
        except: continue

if __name__ == '__main__':
    init_db()
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على متغير BOT_TOKEN")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_cb))
        if app.job_queue: app.job_queue.run_repeating(prayer_cron, interval=60)
        app.run_polling(drop_pending_updates=True)
