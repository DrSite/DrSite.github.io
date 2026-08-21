import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from supabase import create_client
from dotenv import load_dotenv

# بارگذاری اطلاعات از فایل امن .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# بررسی اینکه توکن حتماً خوانده شده باشد
if not BOT_TOKEN:
    raise ValueError("توکن ربات در فایل .env یافت نشد!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# بقیه کدهای ربات مثل قبل...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"سلام {user.first_name} عزیز! ربات با امنیت کامل متصل شد.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    print("🤖 Bot is running securely...")
    application.run_polling()