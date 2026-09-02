import os
import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.request import HTTPXRequest
from supabase import create_client, Client
from dotenv import load_dotenv

# بارگذاری اطلاعات از فایل امن .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("توکن ربات در فایل .env یافت نشد!")

# اتصال به دیتابیس Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# تنظیمات لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- تابع بررسی وضعیت کاربر و تاریخ انقضا ---
def check_and_update_user(tg_user):
    """
    کاربر را در دیتابیس ثبت می‌کند. اگر پریمیوم باشد و تاریخ انقضایش گذشته باشد،
    او را به پلن رایگان برمی‌گرداند.
    """
    user_id = str(tg_user.id)
    username = tg_user.username or ""
    full_name = f"{tg_user.first_name or ''} {tg_user.last_name or ''}".strip()

    try:
        # جستجوی کاربر در دیتابیس
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not response.data:
            # اگر کاربر جدید است، در دیتابیس ثبت شود
            new_user = {
                'id': user_id,
                'username': username,
                'full_name': full_name,
                'plan': 'free'
            }
            supabase.table('users').insert(new_user).execute()
            return 'free'
        else:
            # بررسی تاریخ انقضا برای کاربران قدیمی
            db_user = response.data[0]
            plan = db_user.get('plan', 'free')
            expire_at = db_user.get('expire_at')
            
            if plan == 'premium' and expire_at:
                # تبدیل رشته تاریخ به آبجکت دیت‌تایم برای مقایسه
                expire_date = datetime.fromisoformat(expire_at.replace('Z', '+00:00'))
                
                if datetime.now(timezone.utc) > expire_date:
                    # تاریخ منقضی شده است! بازگشت به پلن رایگان
                    supabase.table('users').update({
                        'plan': 'free', 
                        'expire_at': None
                    }).eq('id', user_id).execute()
                    return 'free'
            return plan
            
    except Exception as e:
        logger.error(f"Error checking user in DB: {e}")
        return 'free'

# --- دستور استارت و معرفی ربات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # همگام‌سازی کاربر با دیتابیس و پنل ادمین
    user_plan = check_and_update_user(user)
    
    plan_text = "💎 حساب شما: **ویژه (Premium)**" if user_plan == 'premium' else "🆓 حساب شما: **رایگان (Free)**"

    keyboard = [
        [InlineKeyboardButton("🔗 افزودن به گروه", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("💎 خرید اشتراک پریمیوم", callback_data="buy_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! به ربات مدیریت دانگ و هزینه‌ها (دنگی‌مونگی) خوش آمدید.\n\n"
        f"{plan_text}\n\n"
        "برای شروع، ربات را به گروه خود اضافه کنید یا از دکمه‌های زیر استفاده کنید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# --- دستور راهنما ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **راهنمای استفاده از ربات دنگی‌مونگی:**\n\n"
        "1️⃣ ربات را به گروه خود اضافه کنید.\n"
        "2️⃣ هزینه‌ها را به صورت متنی در گروه بنویسید.\n"
        "3️⃣ برای ارتقا به حساب پریمیوم، از منوی شروع اقدام کنید.",
        parse_mode="Markdown"
    )

# --- دستور پشتیبانی ---
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 **پشتیبانی دنگی‌مونگی:**\n\n"
        "برای ارتباط با پشتیبانی یا گزارش مشکل، به ادمین پیام دهید:\n"
        "👤 @DrSiteofficial",
        parse_mode="Markdown"
    )

# --- نمایش اطلاعات پرداخت ---
async def premium_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    # ثبت کاربر در دیتابیس به محض کلیک روی دکمه خرید
    check_and_update_user(user)
    
    await query.answer()
    
    if query.data == "buy_premium":
        await query.message.reply_text(
            "💎 **ارتقا به حساب پریمیوم دنگی‌مونگی**\n\n"
            "💰 **مبلغ اشتراک:** ۴۹,۰۰۰ تومان (۳۰ روزه)\n"
            "💳 **شماره کارت:**\n"
            "`5892-1012-5863-6535`\n"
            "👤 **به نام:** علیرضا محمودیان کرویه\n\n"
            "لطفاً پس از واریز، **تصویر رسید** را همین‌جا بفرستید تا برای بررسی به ادمین ارسال شود.",
            parse_mode="Markdown"
        )

# --- دریافت تصویر رسید و ارسال به پی‌وی ادمین ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # ثبت کاربر در دیتابیس به محض ارسال رسید
    check_and_update_user(user)
    
    photo_file_id = update.message.photo[-1].file_id
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_file_id,
                caption=f"📩 **رسید جدید پرداخت اشتراک!**\n\n"
                f"👤 نام: {user.first_name}\n"
                f"🔗 ارتباط: @{user.username or 'ندارد'}\n"
                f"🆔 شناسه کاربر: `{user.id}`",
                parse_mode="Markdown"
            )
            await update.message.reply_text("✅ رسید شما با موفقیت دریافت شد و برای ادمین ارسال گردید. پس از تایید، پیامی دریافت خواهید کرد.")
        except Exception as e:
            logger.error(f"Error sending photo to admin: {e}")
            await update.message.reply_text("⚠️ متاسفانه در ارسال رسید مشکلی پیش آمد. لطفا دقایقی دیگر تلاش کنید.")
    else:
        await update.message.reply_text("⚠️ ادمینی برای دریافت رسید تنظیم نشده است.")

# --- مدیریت پیام‌های متنی در گروه (ثبت هزینه‌ها) ---
async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    text = update.message.text

    if chat.type in ['group', 'supergroup']:
        check_and_update_user(user)
        logger.info(f"Expense message in group {chat.title}: {text} by {user.username}")

if __name__ == '__main__':
    # تنظیم پروکسی برای PythonAnywhere جهت رفع خطای 503
    custom_request = HTTPXRequest(proxy="http://proxy.server:3128")
    
    application = ApplicationBuilder().token(BOT_TOKEN).request(custom_request).build()
    
    # ثبت تمام هندلرهای ربات
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(CallbackQueryHandler(premium_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_expense))
    
    print("🤖 DongiMongi Bot is running securely with PythonAnywhere proxy...")
    application.run_polling()