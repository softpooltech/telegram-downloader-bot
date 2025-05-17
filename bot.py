import os
import telebot
import yt_dlp

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Send me a YouTube or Instagram video link to download.")

@bot.message_handler(func=lambda msg: 'youtube.com' in msg.text or 'youtu.be' in msg.text or 'instagram.com' in msg.text)
def download_handler(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Downloading... Please wait.")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file_size = os.path.getsize(filename)
        max_size = 50 * 1024 * 1024  # 50MB limit

        with open(filename, 'rb') as f:
            if file_size <= max_size:
                if filename.endswith(('.mp4', '.mkv', '.webm')):
                    bot.send_video(message.chat.id, f)
                else:
                    bot.send_document(message.chat.id, f)
            else:
                bot.send_message(message.chat.id, "⚠️ File too large for Telegram.")

        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

print("✅ Bot is running...")
bot.polling()
