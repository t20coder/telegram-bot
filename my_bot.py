from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  #Load from .env file

# 👇 Use environment variable (from .env or Render secrets)
bot_token = os.getenv("BOT_TOKEN")

# 🛡️ Admin ID
ADMIN_ID = 6352552205

# 💱 Currency pairs
currency_pairs = [
    "EUR/GBP","EUR/USD","USD/ARS","USD/BDT ","USD/PKR ","EUR/CAD","USD/IDR", "EUR/CHF","EUR/NZD","USD/COP","USD/PHP",
    "AUD/USD","NZD/CAD","USD/CAD","USD/CHF","USD/NGN","USD/TRY","EUR/JPY","USD/ZAR","CAD/CHF","CHF/JPY","USD/JPY",
    "AUD/CAD","AUD/CHF","AUD/JPY","GBP/AUD","GBP/USD","NZD/CHF","NZD/JPY","GBP/CAD","USD/DZD","EUR/AUD","USD/EGP",
    "USD/MXN","CAD/JPY","NZD/USD","GBP/NZD"
]

broadcast_chat_ids = [
    6352552205,
    -1002861471371
]

# Admin-only decorator
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        await func(update, context)
    return wrapper

# Create signal buttons
def create_signal_buttons(pairs):
    keyboard = []
    for pair in pairs:
        keyboard.append([
            InlineKeyboardButton(f"📈 {pair} (OTC) UP", callback_data=f"{pair}|UP"),
            InlineKeyboardButton(f"📉 {pair} (OTC) DOWN", callback_data=f"{pair}|DOWN")
        ])
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = create_signal_buttons(currency_pairs)
    await update.message.reply_text(
        "💵 *All OTC Currency Pairs*\nTap to send signal:\n\nUse /search usd to filter.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        keyword = context.args[0].upper()
        filtered = [pair for pair in currency_pairs if keyword in pair]
        if filtered:
            markup = create_signal_buttons(filtered)
            await update.message.reply_text(f"🔍 *Filtered by:* `{keyword}`", reply_markup=markup, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ No matches found.")
    else:
        await update.message.reply_text("🔍 Use: /search usd")

# Signal handler
async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pair, direction = query.data.split("|")
    arrow = "⬆️" if direction == "UP" else "⬇️"

    message = (
        f"📊 *Premium OTC Signal Alert!*\n\n"
        f"📌 *Asset:* `{pair} (OTC)`\n"
        f"🕐 *Timeframe:* 1 Minute\n"
        f"📈 *Direction:* {arrow} *{direction.upper()}*\n\n"
        f"📣 _Use proper entry strategy & risk management._\n"
        f"🔔 *Signal Time:* `{datetime.now().strftime('%I:%M %p')}`"
    )

    for chat_id in broadcast_chat_ids:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# /admin
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Admin Panel\nUse /broadcast <message>")

# /broadcast
@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("📢 Usage: /broadcast <message>")
        return
    for chat_id in broadcast_chat_ids:
        await context.bot.send_message(chat_id=chat_id, text=f"📢 Broadcast:\n\n{msg}")

# /getid
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Chat ID: `{update.effective_chat.id}`", parse_mode='Markdown')

# Start bot
app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("getid", get_chat_id))
app.add_handler(CallbackQueryHandler(handle_signal))

print("🚀 NMJ Trader Bot is Live")
app.run_polling()
