import telebot
import json
import time
from telebot import types

TOKEN = "BOT_TOKEN"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)

# load data
def load_users():
    try:
        with open("users.json") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json","w") as f:
        json.dump(data,f)

def load_tasks():
    try:
        with open("tasks.json") as f:
            return json.load(f)
    except:
        return {}

def save_tasks(data):
    with open("tasks.json","w") as f:
        json.dump(data,f)

users = load_users()
tasks = load_tasks()

# start
@bot.message_handler(commands=['start'])
def start(message):

    uid = str(message.from_user.id)
    args = message.text.split()

    if uid not in users:

        users[uid] = {
            "coin":0,
            "last_task":0,
            "ref":0
        }

        # kiểm tra có ref không
        if len(args) > 1:
            ref = args[1]

            if ref in users and ref != uid:
                users[ref]["coin"] += 400
                users[ref]["ref"] += 1

                bot.send_message(ref,"🎉 Bạn vừa nhận 400đ từ lượt mời")

        save_users(users)

    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add("👤 Tài khoản","📋 Nhiệm vụ")
    menu.add("👥 Giới thiệu","💸 Rút tiền")

    bot.send_message(uid,"Chào mừng đến bot kiếm tiền",reply_markup=menu)

    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "coin":0,
            "last_task":0,
            "ref":0
        }
        save_users(users)

    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add("👤 Tài khoản","📋 Nhiệm vụ")
    menu.add("👥 Giới thiệu","💸 Rút tiền")

    bot.send_message(uid,"Chào mừng đến bot kiếm tiền",reply_markup=menu)

# tài khoản
@bot.message_handler(func=lambda m: m.text=="👤 Tài khoản")
def account(message):

    uid=str(message.from_user.id)

    coin=users[uid]["coin"]

    bot.send_message(uid,f"""
👤 ID: {uid}
💰 Coin: {coin}
""")

# nhiệm vụ
@bot.message_handler(func=lambda m: m.text=="📋 Nhiệm vụ")
def task_list(message):

    if len(tasks)==0:
        bot.send_message(message.chat.id,"Chưa có nhiệm vụ")
        return

    for tid in tasks:

        link=tasks[tid]["link"]
        reward=tasks[tid]["reward"]

        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Làm nhiệm vụ",url=link))
        markup.add(types.InlineKeyboardButton("Gửi ảnh",callback_data="task_"+tid))

        bot.send_message(message.chat.id,f"""
Nhiệm vụ #{tid}

Phần thưởng: {reward} coin
""",reply_markup=markup)

# gửi ảnh nhiệm vụ
@bot.callback_query_handler(func=lambda call:call.data.startswith("task_"))
def send_proof(call):

    tid=call.data.split("_")[1]

    msg=bot.send_message(call.message.chat.id,"Gửi ảnh hoàn thành nhiệm vụ")
    bot.register_next_step_handler(msg,receive_photo,tid)

def receive_photo(message,tid):

    if not message.photo:
        bot.send_message(message.chat.id,"Phải gửi ảnh")
        return

    uid=message.from_user.id

    markup=types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Duyệt",callback_data=f"done_{uid}_{tid}"),
        types.InlineKeyboardButton("❌ Từ chối",callback_data=f"reject_{uid}_{tid}")
    )

    bot.send_photo(ADMIN_ID,message.photo[-1].file_id,
    caption=f"user {uid} gửi nhiệm vụ {tid}",reply_markup=markup)

    bot.send_message(uid,"⏳ Đã gửi admin duyệt")

# admin duyệt
@bot.callback_query_handler(func=lambda call:call.data.startswith("done_"))
def approve(call):

    data=call.data.split("_")

    uid=data[1]
    tid=data[2]

    reward=tasks[tid]["reward"]

    users[str(uid)]["coin"]+=reward

    save_users(users)

    bot.send_message(uid,f"✅ Nhiệm vụ hoàn thành +{reward} coin")

# tạo nhiệm vụ admin
@bot.message_handler(commands=['taonhiemvu'])
def create_task(message):

    if message.from_user.id!=ADMIN_ID:
        return

    msg=bot.send_message(message.chat.id,"Nhập link nhiệm vụ")
    bot.register_next_step_handler(msg,task_link)

def task_link(message):

    link=message.text

    msg=bot.send_message(message.chat.id,"Nhập thưởng coin")
    bot.register_next_step_handler(msg,task_reward,link)

def task_reward(message,link):

    reward=int(message.text)

    tid=str(len(tasks)+1)

    tasks[tid]={
        "link":link,
        "reward":reward
    }

    save_tasks(tasks)

    bot.send_message(message.chat.id,"✅ Đã tạo nhiệm vụ")

# chống spam
@bot.message_handler(content_types=['text'])
def anti_spam(message):

    uid=str(message.from_user.id)

    now=time.time()

    if now-users[uid]["last_task"]<5:
        bot.send_message(uid,"⚠️ Spam quá nhanh")
        return

    users[uid]["last_task"]=now
    save_users(users)

bot.infinity_polling()
