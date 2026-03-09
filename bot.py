import telebot
import json
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "TOKEN_BOT"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)

TASK_LINK = "https://example.com"

try:
    with open("users.json","r") as f:
        users = json.load(f)
except:
    users = {}

def save():
    with open("users.json","w") as f:
        json.dump(users,f)

def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👤 Tài khoản","🔗 Nhiệm vụ")
    kb.add("👥 Giới thiệu","💰 Kiếm tiền")
    kb.add("📅 Điểm danh")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)

    if uid not in users:
        users[uid] = {
            "coin":0,
            "ref":0,
            "checkin":False
        }
        save()

    bot.send_message(
        m.chat.id,
        "Chào mừng đến bot kiếm tiền 💰",
        reply_markup=menu()
    )

@bot.message_handler(func=lambda m: m.text=="👤 Tài khoản")
def account(m):

    uid=str(m.from_user.id)

    coin=users[uid]["coin"]
    ref=users[uid]["ref"]

    text=f"""
👤 Tài khoản

ID: {uid}
💰 Xu: {coin}
👥 Đã mời: {ref}
"""

    bot.send_message(m.chat.id,text)

@bot.message_handler(func=lambda m: m.text=="👥 Giới thiệu")
def ref(m):

    uid=m.from_user.id

    link=f"https://t.me/YOURBOT?start={uid}"

    bot.send_message(
        m.chat.id,
        f"Link mời bạn:\n{link}\n\nMỗi người +100 xu"
    )

@bot.message_handler(func=lambda m: m.text=="📅 Điểm danh")
def checkin(m):

    uid=str(m.from_user.id)

    if users[uid]["checkin"]:
        bot.send_message(m.chat.id,"Bạn đã điểm danh hôm nay")
        return

    users[uid]["coin"]+=50
    users[uid]["checkin"]=True

    save()

    bot.send_message(m.chat.id,"Điểm danh thành công +50 xu")

@bot.message_handler(func=lambda m: m.text=="🔗 Nhiệm vụ")
def task(m):

    bot.send_message(
        m.chat.id,
        f"Nhiệm vụ hôm nay:\n{TASK_LINK}\n\nSau khi vượt link gửi ảnh cho bot."
    )

@bot.message_handler(content_types=['photo'])
def photo(m):

    uid=m.from_user.id

    file_id=m.photo[-1].file_id

    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=f"User {uid} gửi ảnh\n\n/ok_{uid} duyệt\n/no_{uid} từ chối"
    )

    bot.send_message(m.chat.id,"Đã gửi admin duyệt")

@bot.message_handler(func=lambda m: m.text.startswith("/ok_"))
def ok(m):

    if m.from_user.id!=ADMIN_ID:
        return

    uid=m.text.split("_")[1]

    users[uid]["coin"]+=500

    save()

    bot.send_message(uid,"Nhiệm vụ hoàn thành +500 xu")

@bot.message_handler(func=lambda m: m.text.startswith("/no_"))
def no(m):

    if m.from_user.id!=ADMIN_ID:
        return

    uid=m.text.split("_")[1]

    bot.send_message(uid,"Ảnh không hợp lệ")

bot.infinity_polling()
