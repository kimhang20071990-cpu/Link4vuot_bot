import telebot
import json
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8753063856:AAGI0AkzuHFUW_-fSg6pSXV0gUdI4Ktnzlo"
ADMIN_ID = 8614970068

bot = telebot.TeleBot(TOKEN)

# load users
def load_users():
    try:
        with open("users.json","r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json","w") as f:
        json.dump(data,f)

users = load_users()

tasks=[]


def get_user(uid):
    if uid not in users:
        users[uid]={
            "coin":0,
            "ref":0,
            "inviter":None,
            "task_done":0,
            "last_checkin":0
        }
    return users[uid]


def menu():
    m=ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("💰 Số dư","👥 Mời bạn")
    m.add("📋 Nhiệm vụ","📅 Điểm danh")
    m.add("🏆 Bảng xếp hạng","💳 Rút tiền")
    return m


@bot.message_handler(commands=["start"])
def start(message):

    uid=str(message.from_user.id)
    user=get_user(uid)

    args=message.text.split()

    if len(args)>1:
        inviter=args[1]

        if inviter!=uid and user["inviter"]==None:
            user["inviter"]=inviter

    save_users(users)

    bot.send_message(uid,"Chào mừng bạn!",reply_markup=menu())


@bot.message_handler(func=lambda m:m.text=="💰 Số dư")
def balance(message):

    uid=str(message.from_user.id)
    user=get_user(uid)

    bot.send_message(uid,f"Số dư: {user['coin']}đ")


@bot.message_handler(func=lambda m:m.text=="👥 Mời bạn")
def ref(message):

    uid=str(message.from_user.id)

    link=f"https://t.me/YOURBOT?start={uid}"

    bot.send_message(uid,
f"""
Link mời:

{link}

Mỗi lượt mời nhận 400đ
""")


@bot.message_handler(func=lambda m:m.text=="📅 Điểm danh")
def checkin(message):

    uid=str(message.from_user.id)
    user=get_user(uid)

    now=time.time()

    if now-user["last_checkin"]<86400:
        bot.send_message(uid,"Bạn đã điểm danh hôm nay")
        return

    user["coin"]+=100
    user["last_checkin"]=now

    save_users(users)

    bot.send_message(uid,"+100đ điểm danh thành công")


@bot.message_handler(func=lambda m:m.text=="🏆 Bảng xếp hạng")
def top(message):

    ranking=sorted(users.items(),
                   key=lambda x:x[1]["ref"],
                   reverse=True)[:10]

    text="🏆 TOP MỜI BẠN\n\n"

    i=1
    for uid,data in ranking:

        text+=f"{i}. {uid} — {data['ref']} ref\n"
        i+=1

    bot.send_message(message.chat.id,text)


@bot.message_handler(func=lambda m:m.text=="📋 Nhiệm vụ")
def show_tasks(message):

    if len(tasks)==0:
        bot.send_message(message.chat.id,"Chưa có nhiệm vụ")
        return

    text="Danh sách nhiệm vụ\n\n"

    for t in tasks:
        text+=f"{t}\n"

    bot.send_message(message.chat.id,text)


@bot.message_handler(func=lambda m:m.text=="💳 Rút tiền")
def withdraw(message):

    uid=str(message.from_user.id)
    user=get_user(uid)

    if user["coin"]<10000:
        bot.send_message(uid,"Min rút 10k")
        return

    bot.send_message(uid,"Nhập số tiền muốn rút")


    bot.register_next_step_handler(message,process_withdraw)


def process_withdraw(message):

    uid=str(message.from_user.id)
    amount=int(message.text)

    if amount<10000:
        bot.send_message(uid,"Min rút 10k")
        return

    if users[uid]["coin"]<amount:
        bot.send_message(uid,"Không đủ tiền")
        return

    users[uid]["coin"]-=amount
    save_users(users)

    bot.send_message(ADMIN_ID,
f"""
YÊU CẦU RÚT TIỀN

User: {uid}
Số tiền: {amount}
""")

    bot.send_message(uid,"Yêu cầu rút tiền đã gửi admin")


@bot.message_handler(commands=["addtask"])
def addtask(message):

    if message.from_user.id!=ADMIN_ID:
        return

    bot.send_message(message.chat.id,"Nhập nhiệm vụ")

    bot.register_next_step_handler(message,save_task)


def save_task(message):

    tasks.append(message.text)

    bot.send_message(message.chat.id,"Đã thêm nhiệm vụ")


@bot.message_handler(commands=["done"])
def done_task(message):

    uid=str(message.from_user.id)
    user=get_user(uid)

    user["task_done"]+=1

    if user["task_done"]==1:

        inviter=user["inviter"]

        if inviter and inviter in users:

            users[inviter]["coin"]+=400
            users[inviter]["ref"]+=1

            bot.send_message(inviter,"Bạn nhận 400đ từ ref")

    save_users(users)

    bot.send_message(uid,"Đã hoàn thành nhiệm vụ")


bot.infinity_polling()
