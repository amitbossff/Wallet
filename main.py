from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
import db
from config import BOT_TOKEN, ADMIN_IDS


# ---------- Keyboards ----------

def user_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["💰 Balance", "📜 History"]
        ],
        resize_keyboard=True
    )


def admin_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["💰 Balance", "📜 History"],
            ["👑 Admin Panel", "👥 Users"]
        ],
        resize_keyboard=True
    )


# ---------- /start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.create_user(user.id, user.full_name)

    kb = admin_keyboard() if user.id in ADMIN_IDS else user_keyboard()

    await update.message.reply_text(
        "👛 Wallet Bot\nChoose an option 👇",
        reply_markup=kb
    )


# ---------- Text Handler ----------

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    kb = admin_keyboard() if user_id in ADMIN_IDS else user_keyboard()

    if text == "💰 Balance":
        bal = db.get_balance(user_id)
        await update.message.reply_text(
            f"💰 Your Balance: {bal}",
            reply_markup=kb
        )

    elif text == "📜 History":
        records = db.get_history(user_id)
        if not records:
            return await update.message.reply_text(
                "📭 No transactions found",
                reply_markup=kb
            )

        msg = "📜 Transaction History:\n\n"
        for amt, typ, date in records:
            icon = "➕" if typ == "ADD" else "➖"
            msg += f"{icon} {typ} | {amt} | {date}\n"

        await update.message.reply_text(msg, reply_markup=kb)

    elif text == "👑 Admin Panel":
        if user_id not in ADMIN_IDS:
            return await update.message.reply_text("❌ Admin only")

        await update.message.reply_text(
            "/add USERID AMOUNT\n"
            "/pay USERID AMOUNT\n"
            "/ubalance USERID",
            reply_markup=kb
        )

    elif text == "👥 Users":
        if user_id not in ADMIN_IDS:
            return await update.message.reply_text("❌ Admin only")

        users = db.get_all_users()
        msg = "👥 Users List\n\n"
        for uid, name in users:
            msg += f"{name}\nID: `{uid}`\n\n"

        await update.message.reply_text(msg, reply_markup=kb)


# ---------- Admin Commands ----------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        uid = int(context.args[0])
        amt = float(context.args[1])
    except:
        return await update.message.reply_text("Usage: /add USERID AMOUNT")

    db.add_balance(uid, amt)
    db.add_transaction(uid, amt, "ADD")

    await context.bot.send_message(uid, f"✅ {amt} added to your wallet")
    await update.message.reply_text("✔ Balance added")


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        uid = int(context.args[0])
        amt = float(context.args[1])
    except:
        return await update.message.reply_text("Usage: /pay USERID AMOUNT")

    if db.get_balance(uid) < amt:
        return await update.message.reply_text("❌ Insufficient balance")

    db.deduct_balance(uid, amt)
    db.add_transaction(uid, amt, "PAY")

    await context.bot.send_message(uid, f"💸 Payment successful: {amt}")
    await update.message.reply_text("✔ Payment done")


async def ubalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        uid = int(context.args[0])
    except:
        return await update.message.reply_text("Usage: /ubalance USERID")

    user = db.get_user_info(uid)
    if not user:
        return await update.message.reply_text("User not found")

    name, balance = user
    await update.message.reply_text(
        f"👤 {name}\n🆔 {uid}\n💰 Balance: {balance}"
    )


# ---------- Run ----------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("pay", pay))
app.add_handler(CommandHandler("ubalance", ubalance))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
