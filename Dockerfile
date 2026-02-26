# استخدام نسخة بايثون مستقرة
FROM python:3.10-slim

# تثبيت ffmpeg وتحديث النظام
RUN apt-get update && apt-get install -y ffmpeg

# تحديد مسار العمل
WORKDIR /app

# نسخ ملفات المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات البوت
COPY . .

# أمر التشغيل
CMD ["python", "main.py"]
