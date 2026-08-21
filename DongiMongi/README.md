\# سیستم مدیریت مینی‌اپ و ربات تلگرام



این پروژه شامل دو بخش اصلی است:

1\. \*\*پنل مدیریت (Admin Panel):\*\* برای مدیریت کاربران، فعال‌سازی اشتراک‌ها و گزارش‌های مالی.

2\. \*\*ربات تلگرام:\*\* برای تعامل با کاربران و اتصال به دیتابیس سوپابیس.



\## پیش‌نیازها

\- یک پروژه در \[Supabase](https://supabase.com/).

\- توکن ربات تلگرام (از طریق BotFather دریافت کنید).

\- پایتون نسخه ۳.۹ یا بالاتر.



\## ساختار دیتابیس (SQL)

مطمئن شوید جداول زیر در سوپابیس شما وجود دارند:

\- `admin\_settings`: شامل `key` و `value` (برای ذخیره رمز هش‌شده).

\- `users`: شامل `id`, `full\_name`, `username`, `plan`, `expire\_at`.

\- `payments`: شامل `amount`, `user\_id`.

\- `groups`: شامل `id`, `user\_id`, `group\_name`, `is\_locked`.

\- `expenses`: شامل `group\_id`, `title`, `amount`.



\## نحوه اجرا

1\. \*\*پنل:\*\* فایل `index.html` را روی یک هاست یا سرویس استاتیک (مثل Vercel یا GitHub Pages) آپلود کنید.

2\. \*\*ربات:\*\* فایل `bot.py` را روی یک سرور مجازی (VPS) اجرا کنید:

&#x20;  ```bash

&#x20;  pip install python-telegram-bot supabase

&#x20;  python bot.py

