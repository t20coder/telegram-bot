import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # ⬅️ Load .env variables (used by Render)

# 🛡️ Admin ID
ADMIN_ID = 6352552205 # Replace with your own ID

# 📥 Bot Token (loaded securely)
bot_token = os.getenv("BOT_TOKEN")

# 🧑‍💼 Recipients
broadcast_chat_ids = [
    6352552205, # Your personal Telegram ID
    -1002861471371 # Your group/channel ID
]

group_chat_ids = [
    -1002861471371 # For group-specific broadcast
]

# 💱 Currency Pairs
currency_pairs = [
    "EUR/GBP", "EUR/USD", "USD/ARS", "USD/BDT", "USD/PKR", "EUR/CAD", "USD/IDR",
    "EUR/CHF", "EUR/NZD", "USD/COP", "USD/PHP", "AUD/USD", "NZD/CAD", "USD/CAD",
    "USD/CHF", "USD/NGN", "USD/TRY", "EUR/JPY", "USD/ZAR", "CAD/CHF", "CHF/JPY",
    "USD/JPY", "AUD/CAD", "AUD/CHF", "AUD/JPY", "GBP/AUD", "GBP/USD", "NZD/CHF",
    "NZD/JPY", "GBP/CAD", "USD/DZD", "EUR/AUD", "USD/EGP", "USD/MXN", "CAD/JPY",
    "NZD/USD", "GBP/NZD"
]

# 🔐 Admin-only decorator
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        await func(update, context)
    return wrapper

# ⬇️ Signal Buttons
def create_signal_buttons(pairs):
    keyboard = []
    for pair in pairs:
        keyboard.append([
            InlineKeyboardButton(f"📈 {pair} (OTC) UP", callback_data=f"{pair}|UP"),
            InlineKeyboardButton(f"📉 {pair} (OTC) DOWN", callback_data=f"{pair}|DOWN")
        ])
    return InlineKeyboardMarkup(keyboard)

# ▶️ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = create_signal_buttons(currency_pairs)
    await update.message.reply_text(
        "💵 *All OTC Currency Pairs*\nTap to send signal:\n\nUse /search usd to filter.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# 🔍 /search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        keyword = context.args[0].upper()
        filtered = [pair for pair in currency_pairs if keyword in pair]
        if filtered:
            markup = create_signal_buttons(filtered)
            await update.message.reply_text(
                f"🔍 *Filtered by:* `{keyword}`",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ No matches found.")
    else:
        await update.message.reply_text("🔍 Use: /search usd")

# 📲 Handle Signal Buttons
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

    await query.message.reply_text(message, parse_mode='Markdown')

# 🔐 /admin command
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Admin Panel\nUse /broadcast <msg> or /groupbroadcast <msg>"
    )

# 📢 /broadcast command (to users + groups)
@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("📢 Usage: /broadcast Your message here")
        return

    count = 0
    for chat_id in broadcast_chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 Broadcast:\n\n{msg}")
            count += 1
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {count} chat(s).")

# 👥 /groupbroadcast command
@admin_only
async def group_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("📢 Usage: /groupbroadcast <msg>")
        return

    count = 0
    for group_id in group_chat_ids:
        try:
            await context.bot.send_message(chat_id=group_id, text=f"📢 Group Broadcast:\n\n{msg}")
            count += 1
        except Exception as e:
            print(f"❌ Error in group {group_id}: {e}")

    await update.message.reply_text(f"✅ Sent to {count} group(s).")

# 🆔 /getid command
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"📢 This chat ID is:\n`{chat.id}`",
        parse_mode='Markdown'
    )

# 🚀 Initialize Bot
app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("groupbroadcast", group_broadcast))
app.add_handler(CommandHandler("getid", get_chat_id))
app.add_handler(CallbackQueryHandler(handle_signal))

print("🚀 NMJ Trader Bot is Live")
app.run_polling()
