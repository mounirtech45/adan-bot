import logging
import sqlite3
import requests
import asyncio
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- الإعدادات ---
TOKEN = "YOUR_BOT_TOKEN_HERE"

# روابط الأذان والملصقات (نفس الروابط السابقة)
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

# قائمة الولايات الجزائرية (بالإنجليزية للـ API وبالعربية للأزرار)
ALGERIA_STATES = [
    ("Adrar", "أدرار"), ("Chlef", "الشلف"), ("Laghouat", "الأغواط"), ("Oum El Bouaghi", "أم البواقي"),
    ("Batna", "باتنة"), ("Bejaia", "بجاية"), ("Biskra", "بسكرة"), ("Bechar", "بشار"),
    ("Blida", "البليدة"), ("Bouira", "البويرة"), ("Tamanrasset", "تمنراست"), ("Tebessa", "تبسة"),
    ("Tlemcen", "تلمسان"), ("Tiaret", "تيارت"), ("Tizi Ouzou", "تيزي وزو"), ("Algiers", "الجزائر"),
    ("Djelfa", "الجلفة"), ("Jijel", "جيجل"), ("Setif", "سطيف"), ("Saida", "سعيدة"),
    ("Skikda", "سكيكدة"), ("Sidi Bel Abbes", "سيدي بلعباس"), ("Annaba", "عنابة"), ("Guelma", "قالمة"),
    ("Constantine", "قسنطينة"), ("Medea", "المدية"), ("Mostaganem", "مستغانم"), ("M'Sila", "المسيلة"),
    ("Mascara", "معسكر"), ("Ouargla", "ورقلة"), ("Oran", "وهران"), ("El Bayadh", "البيض"),
    ("Illizi", "إليزي"), ("Bordj Bou Arreridj", "برج بوعريريج"), ("Boumerdes", "بومرداس"), ("El Tarf", "الطارف"),
    ("Tindouf", "تندوف"), ("Tissemsilt", "تيسمسيلت"), ("El Oued", "الوادي"), ("Khenchela", "خنشلة"),
    ("Souk Ahras", "سوق أهراس"), ("Tipaza", "تيبازة"), ("Mila", "ميلة"), ("Ain Defla", "عين الدفلى"),
    ("Naama", "النعامة"), ("Ain Temouchent", "عين تموشنت"), ("Ghardaia", "غرداية"), ("Relizane", "غليزان"),
    ("Timimoun", "تيميمون"), ("Bordj Badji Mokhtar", "برج باجي مختار"), ("Ouled Djellal", "أولاد جلال"),
    ("Beni Abbes", "بني عباس"), ("In Salah", "عين صالح"), ("In Guezzam", "عين قزام"),
    ("Touggourt", "توقرت"), ("Djanet", "جانت"), ("El M'Ghair", "المغير"), ("El Meniaa", "المنيعة")
]

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('prayer_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subs 
                 (chat_id INTEGER PRIMARY KEY, city_en TEXT, city_ar TEXT, timezone TEXT)''')
    conn.commit()
    conn.close()

# --- الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق أن البوت في مجموعة أو قناة
    chat_type = update.effective_chat.type
    if chat_type == "private":
        await update.message.reply_text("⚠️ عذراً، هذا البوت مخصص للعمل في القنوات والمجموعات فقط.")
        return

    keyboard = []
    # بناء الأزرار صفوف (كل صف فيه زرين)
    for i in range(0, len(ALGERIA_STATES), 2):
        row = [
            InlineKeyboardButton(ALGERIA_STATES[i][1], callback_data=f"set_{ALGERIA_STATES[i][0]}_{ALGERIA_STATES[i][1]}"),
        ]
        if i + 1 < len(ALGERIA_STATES):
            row.append(InlineKeyboardButton(ALGERIA_STATES[i+1][1], callback_data=f"set_{ALGERIA_STATES[i+1][0]}_{ALGERIA_STATES[i+1][1]}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📍 يرجى اختيار الولاية لضبط مواقيت الصلاة لها في هذه المجموعة/القناة:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    city_en = data[1]
    city_ar = data[2]
    chat_id = query.message.chat_id

    # جلب التوقيت الزمني للمدينة
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city_en}&country=Algeria"
    res = requests.get(url).json()
    timezone = res['data']['meta']['timezone']

    conn = sqlite3.connect('prayer_bot.db')
    c = conn.cursor()
    c.execute("REPLACE INTO subs VALUES (?, ?, ?, ?)", (chat_id, city_en, city_ar, timezone))
    conn.commit()
    conn.close()

    await query.answer()
    await query.edit_message_text(f"✅ تم بنجاح ضبط مواقيت الصلاة لولاية: {city_ar}")

async def prayer_cron(context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('prayer_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM subs")
    subs = c.fetchall()
    conn.close()

    for chat_id, city_en, city_ar, tz_name in subs:
        try:
            user_tz = pytz.timezone(tz_name)
            now_time = datetime.now(user_tz).strftime("%H:%M")
            
            url = f"http://api.aladhan.com/v1/timingsByCity?city={city_en}&country=Algeria&method=3"
            res = requests.get(url).json()
            timings = res['data']['timings']
            
            target_prayers = {"Fajr":"الفجر", "Dhuhr":"الظهر", "Asr":"العصر", "Maghrib":"المغرب", "Isha":"العشاء"}
            
            for p_key, p_ar in target_prayers.items():
                if now_time == timings[p_key]:
                    # إرسال المحتوى
                    await context.bot.send_sticker(chat_id=chat_id, sticker=STICKERS[p_key])
                    
                    caption = f"""
🕌 تذكير موعد الصلاة

⏰ صلاة {p_ar}
📍 المدينة: {city_ar}
🕒 موعد الأذان: {timings[p_key]}

📅 التاريخ
🌙 هجري: {res['data']['date']['hijri']['day']} {res['data']['date']['hijri']['month']['ar']}
📆 ميلادي: {res['data']['date']['gregorian']['date']}

ـــــــــــــــــــــــــــــــــــــ
🌌 {HADITHS[p_key]}
ـــــــــــــــــــــــــــــــــــــ
▪️ تقبل الله منا ومنكم
🎙 المؤذن: مشاري راشد العفاسي
                    """
                    await context.bot.send_message(chat_id=chat_id, text=caption)
                    await context.bot.send_audio(chat_id=chat_id, audio=ADHAN_AUDIO[p_key])
                    await asyncio.sleep(60) # تجنب التكرار
        except:
            continue

if __name__ == '__main__':
    init_db()
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    job_queue = application.job_queue
    job_queue.run_repeating(prayer_cron, interval=60)
    
    application.run_polling()
