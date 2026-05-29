from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, KeyboardButton
import requests
#import json

# ==================== تنظیمات شما ====================
TOKEN = "317697879:AAH7aWVDWwyd6BOHn-dB7PhJnlFmHlGmOOA"
PROXY_URL = None   # پراکسی SOCKS5 شما (اگر خراب است None کن)
API_URL = "https://Api.BrsApi.ir/Market/Gold_Currency.php?key=BNr8jccDreKFSweAJHFjIJ71CBy16UmZ"

# ==================== منوی شیشه‌ای ====================
def glass_menu():
    buttons = [
        [KeyboardButton("✨ طلا"), KeyboardButton("💎 ارز (دلار/یورو)")],
        [KeyboardButton("₿ بیت‌کوین"), KeyboardButton("📊 همه")],
        [KeyboardButton("❓ راهنما")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ==================== دریافت داده از API ====================
def fetch_data():
    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
    try:
        resp = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"}, proxies=proxies, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except:
        return None

# ==================== فرمت‌دهی ====================
def format_gold(data):
    items = data.get("gold", [])[:7]
    if not items:
        return "⚠️ اطلاعات طلا موجود نیست."
    msg = "✨ *قیمت طلا (تومان)*\n"
    for i in items:
        msg += f"\n• {i['name']}: `{i['price']:,}`"
    return msg

def format_currency(data):
    items = data.get("currency", [])
    result = []
    for i in items:
        if i.get("symbol") in ["USD", "EUR"]:
            result.append(f"• {i['name']}: `{i['price']:,}` تومان")
    if not result:
        return "⚠️ دلار/یورو یافت نشد."
    return "💎 *قیمت دلار و یورو*\n" + "\n".join(result)

def format_btc(data):
    crypto = data.get("cryptocurrency", [])
    btc = None
    for c in crypto:
        if c.get("symbol") == "BTC":
            btc = c
            break
    if not btc:
        return "⚠️ بیت‌کوین موجود نیست."
    # تبدیل به تومان با نرخ دلار
    usd_price = None
    for cur in data.get("currency", []):
        if cur.get("symbol") == "USD":
            usd_price = int(float(cur.get("price", 0)))
            break
    if usd_price:
        btc_toman = int(float(btc["price"]) * usd_price)
        return f"₿ *بیت‌کوین*: `{btc_toman:,}` تومان"
    else:
        return f"₿ *بیت‌کوین*: `{btc['price']}` دلار"

# ==================== هندلرها ====================
async def start(update, context):
    await update.message.reply_text(
        "🔮 به ربات قیمت خوش آمدید!\nاز دکمه‌های زیر استفاده کنید:",
        reply_markup=glass_menu()
    )

async def gold(update, context):
    await update.message.reply_text("دریافت قیمت طلا...")
    data = fetch_data()
    if data:
        await update.message.reply_text(format_gold(data), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات.")

async def currency(update, context):
    await update.message.reply_text("دریافت قیمت دلار و یورو...")
    data = fetch_data()
    if data:
        await update.message.reply_text(format_currency(data), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ خطا.")

async def btc(update, context):
    await update.message.reply_text("دریافت قیمت بیت‌کوین...")
    data = fetch_data()
    if data:
        await update.message.reply_text(format_btc(data), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ خطا.")

async def all_cmd(update, context):
    await update.message.reply_text("دریافت همه اطلاعات...")
    data = fetch_data()
    if data:
        await update.message.reply_text(format_gold(data), parse_mode="Markdown")
        await update.message.reply_text(format_currency(data), parse_mode="Markdown")
        await update.message.reply_text(format_btc(data), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ خطا.")

async def help_cmd(update, context):
    await update.message.reply_text(
        "📖 *راهنما*\n\n"
        "✨ طلا: قیمت طلا و سکه\n"
        "💎 ارز: دلار و یورو\n"
        "₿ بیت‌کوین: قیمت بیت‌کوین به تومان\n"
        "📊 همه: هر سه مورد با هم\n\n"
        "ساخته شده با عشق."
    )

async def handle_message(update, context):
    text = update.message.text
    if text == "✨ طلا":
        await gold(update, context)
    elif text == "💎 ارز (دلار/یورو)":
        await currency(update, context)
    elif text == "₿ بیت‌کوین":
        await btc(update, context)
    elif text == "📊 همه":
        await all_cmd(update, context)
    elif text == "❓ راهنما":
        await help_cmd(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=glass_menu())

# ==================== راه‌اندازی ====================
def main():
    builder = ApplicationBuilder().token(TOKEN)
    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
    app = builder.build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("all", all_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات با منوی شیشه‌ای روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
