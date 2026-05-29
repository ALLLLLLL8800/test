import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, KeyboardButton
import json
import re

# ==================== تنظیمات ====================
TOKEN = "317697879:AAH7aWVDWwyd6BOHn-dB7PhJnlFmHlGmOOA"
# آدرس پراکسی خودت رو در صورت نیاز همین‌جا بذار:
PROXY_URL = None

# آدرس API نوبیتکس برای ارزهای دیجیتال
NOBITEX_API_URL = "https://apiv2.nobitex.ir/market/stats"
HEADERS_NOBITEX = {"User-Agent": "Mozilla/5.0"}

# ==================== منوی شیشه‌ای ====================
def glass_menu():
    buttons = [
        [KeyboardButton("✨ طلا"), KeyboardButton("💎 ارز (دلار/یورو)")],
        [KeyboardButton("₿ بیت‌کوین"), KeyboardButton("💲 تتر")],
        [KeyboardButton("📊 همه"), KeyboardButton("❓ راهنما")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ==================== دریافت اطلاعات از API ====================
def fetch_nobitex_price(src_currency, dst_currency):
    """دریافت قیمت رمزارز از نوبیتکس (srcCurrency مانند btc، dstCurrency مانند rls)"""
    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
    params = {"srcCurrency": src_currency, "dstCurrency": dst_currency}
    try:
        response = requests.get(NOBITEX_API_URL, headers=HEADERS_NOBITEX, params=params, proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            market_key = f"{src_currency}-{dst_currency}"
            if data.get("status") == "ok" and market_key in data.get("stats", {}):
                return data["stats"][market_key]["bestSell"]
        return None
    except Exception as e:
        print(f"خطا در دریافت از نوبیتکس: {e}")
        return None

def fetch_tgju_price(item_key, name_in_url):
    """دریافت قیمت طلا، دلار، یورو از TGJU"""
    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
    url = f"https://www.tgju.org/profile/{name_in_url}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, proxies=proxies, timeout=10)
        if response.status_code == 200:
            match = re.search(r'data-price=([\"\'])?([^\"\' >]+)', response.text)
            if match:
                raw_price = match.group(2).replace(',', '')
                return int(float(raw_price))
        return None
    except Exception as e:
        print(f"خطا در دریافت از TGJU: {e}")
        return None

# ==================== فرمت‌دهی پاسخ‌ها ====================
def format_gold():
    price = fetch_tgju_price("gold", "geram18")
    if price:
        return f"✨ *قیمت طلا (هر گرم ۱۸ عیار)*\n\nقیمت: `{price:,}` تومان"
    return "⚠️ دریافت قیمت طلا امکان‌پذیر نیست."

def format_currency():
    usd = fetch_tgju_price("usd", "price_dollar_rl")
    eur = fetch_tgju_price("eur", "price_eur")
    result = ""
    if usd:
        result += f"• دلار آمریکا: `{usd:,}` تومان\n"
    if eur:
        result += f"• یورو: `{eur:,}` تومان\n"
    if result:
        return f"💎 *قیمت ارزهای جهانی*\n\n{result}"
    return "⚠️ دریافت قیمت ارزها امکان‌پذیر نیست."

def format_btc():
    price = fetch_nobitex_price("btc", "rls")
    if price:
        return f"₿ *قیمت بیت‌کوین*\n\nقیمت: `{int(float(price)):,}` تومان"
    return "⚠️ دریافت قیمت بیت‌کوین امکان‌پذیر نیست."

def format_usdt():
    price = fetch_nobitex_price("usdt", "rls")
    if price:
        return f"💲 *قیمت تتر (USDT)*\n\nقیمت: `{int(float(price)):,}` تومان"
    return "⚠️ دریافت قیمت تتر امکان‌پذیر نیست."

# ==================== هندلرهای ربات ====================
async def start(update, context):
    await update.message.reply_text(
        "🔮 به ربات قیمت خوش آمدید!\nاز دکمه‌های زیر استفاده کنید:",
        reply_markup=glass_menu()
    )

async def gold(update, context):
    await update.message.reply_text("دریافت قیمت طلا... 🔍")
    await update.message.reply_text(format_gold(), parse_mode="Markdown")

async def currency(update, context):
    await update.message.reply_text("دریافت قیمت دلار و یورو... 💱")
    await update.message.reply_text(format_currency(), parse_mode="Markdown")

async def btc(update, context):
    await update.message.reply_text("دریافت قیمت بیت‌کوین... ₿")
    await update.message.reply_text(format_btc(), parse_mode="Markdown")

async def usdt(update, context):
    await update.message.reply_text("دریافت قیمت تتر... 💲")
    await update.message.reply_text(format_usdt(), parse_mode="Markdown")

async def all_info(update, context):
    await update.message.reply_text("دریافت همه اطلاعات... 📊")
    await update.message.reply_text(format_gold(), parse_mode="Markdown")
    await update.message.reply_text(format_currency(), parse_mode="Markdown")
    await update.message.reply_text(format_btc(), parse_mode="Markdown")
    await update.message.reply_text(format_usdt(), parse_mode="Markdown")

async def help_command(update, context):
    await update.message.reply_text(
        "📖 *راهنما*\n\n"
        "از دکمه‌های زیر استفاده کنید:\n"
        "✨ طلا: قیمت گرم طلای ۱۸ عیار (از TGJU)\n"
        "💎 ارز: قیمت دلار و یورو (از TGJU)\n"
        "₿ بیت‌کوین: آخرین قیمت بیت‌کوین (از نوبیتکس)\n"
        "💲 تتر: آخرین قیمت تتر (USDT) (از نوبیتکس)\n"
        "📊 همه: مشاهده همه موارد با هم\n\n"
        "ساخته شده با ❤️ و APIهای نوبیتکس + TGJU",
        parse_mode="Markdown"
    )

async def handle_message(update, context):
    text = update.message.text
    if text == "✨ طلا":
        await gold(update, context)
    elif text == "💎 ارز (دلار/یورو)":
        await currency(update, context)
    elif text == "₿ بیت‌کوین":
        await btc(update, context)
    elif text == "💲 تتر":
        await usdt(update, context)
    elif text == "📊 همه":
        await all_info(update, context)
    elif text == "❓ راهنما":
        await help_command(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=glass_menu())

# ==================== راه‌اندازی ربات ====================
def main():
    builder = ApplicationBuilder().token(TOKEN)
    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
    app = builder.build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("usdt", usdt))
    app.add_handler(CommandHandler("all", all_info))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات با API نوبیتکس و TGJU روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
