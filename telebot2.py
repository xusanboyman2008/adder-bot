import asyncio
import telebot
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import create_user, get_login1, get_users, get_users_all, init
from request_login import login_main, login

BOT_TOKEN = "7374450108:AAFEg4iriMNqGiHk09Z3TJ_JCYuLZMOleLE"
bot = telebot.TeleBot(BOT_TOKEN)
UZBEKISTAN_TZ = pytz.timezone("Asia/Tashkent")


@bot.message_handler(commands=['start'])
def start(message):
    asyncio.run(create_user(name=message.from_user.first_name, tg_id=message.from_user.id, sending=False))
    bot.send_message(
        message.chat.id,
        f"Hello! Welcome to the bot {message.from_user.first_name}.\n"
        "Botga Login va parol qo‘shish uchun shu usulda foydalaning:\n"
        "👇👇👇👇👇👇👇👇👇👇👇👇👇\n"
        "add login1:parol1,login2:parol2"
    )


@bot.message_handler(func=lambda message: message.text.lower() == "data")
def show_data(message):
    data = asyncio.run(get_login1())
    bot.send_message(message.chat.id, f"Jami {len(data)} dona login bor")

    text = ""
    for i in data:
        text += f"ID: {i.id}\nLogin: {i.login} Parol: {i.password} Status: {i.status}\n"
        text += "🪵🪵🪵🪵🪵🪵🪵🪵🪵🪵🪵🪵🪵🪵\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        'Agarda sizning savollaringiz bo‘lsa 👇 Bot yaratuvchisiga yozing\n'
        '<a href="https://t.me/xusanboyman200/">Admin</a>',
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda message: message.text.startswith("add"))
def add(message):
    try:
        if ":" not in message.text:
            bot.send_message(message.chat.id, "Iltimos pasdagi ko'rinishda yozing\n add login1:parol1,login2:parol2")
            return

        data = message.text.split("add")[1].strip().split(",")
        bot.send_message(message.chat.id, f'Jami {len(data)} login uchun taxminan {len(data)*3} sekund 🕔 vaqt ketadi')

        ready = asyncio.run(login_main(data))

        if len(ready[0]) != 0:
            text = "❗️❗️❗️ Xato login yoki parollar ❗️❗️❗️\n"
            for i in ready[0]:
                text += i
            bot.send_message(message.chat.id, text)

        bot.send_message(message.chat.id, f"Muvaffaqiyatli kirgan loginlar soni ✅ {ready[1]}")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Ha ✅", callback_data="t_yes"),
                   InlineKeyboardButton("Yo‘q ❌", callback_data="t_no"))
        bot.send_message(message.chat.id, "Sizga kunlik ma'lumot kelsinmi?", reply_markup=markup)
    except Exception as error:
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {str(error)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("t"))
def callback_query(call):
    data = call.data.split("t_")[1]
    if data == "yes":
        asyncio.run(create_user(name=call.from_user.first_name, tg_id=call.from_user.id, sending=True))
    else:
        asyncio.run(create_user(name=call.from_user.first_name, tg_id=call.from_user.id, sending=False))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Siz xabar jonatishni tasdiqladingiz ✅", show_alert=True)


def send_daily_update():
    log = asyncio.run(login())
    user_ids = asyncio.run(get_users())
    print(user_ids[0].tg_id)
    print(log)
    for user in user_ids:
        try:
            message = (
                f"Kirish oxshamagan loginlar soni ❌: {len(log[0].split(','))}\n"
                f"Muaffaqiyatli kirilgan loginlar soni ✅: {log[1]}\n"
            )

            if user.role == 'Admin':
                if len(log[0])!=0:
                    message += f"Kirilmagan loginlar\n\n{log[0]}"

            bot.send_message(user.tg_id, message)
        except Exception as error:
            pass


@bot.message_handler(func=lambda message: message.text.lower() == "login")
def logins_all(message):
    bot.send_message(message.chat.id, "Sending...")
    send_daily_update()

class a:
    a = False

@bot.message_handler(func=lambda message: message.text.lower() == "send")
def send_all_users(message):
    a.a = True
    bot.send_message(message.chat.id, "Nima jo‘natsangiz ham jo‘nating")

@bot.message_handler(content_types=["text", "photo", "sticker", "video", "audio",'voice'])
def starr(message):
    if a.a == True:
        a.a=False
        users = asyncio.run(get_users_all())
        if not users:
            bot.send_message(message.chat.id, "No users found.")
            return

        for user_id in users:
            try:
                if message.text:
                    bot.send_message(user_id, message.text)
                elif message.photo:
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.sticker:
                    bot.send_sticker(user_id, message.sticker.file_id)
                elif message.video:
                    bot.send_video(user_id, message.video.file_id)
                elif message.audio:
                    bot.send_audio(user_id, message.audio.file_id)
            except Exception:
                continue

        bot.send_message(message.chat.id, "Message sent to all users.")


scheduler = BackgroundScheduler(timezone=UZBEKISTAN_TZ)
scheduler.add_job(send_daily_update, "cron", hour=8, minute=0)
scheduler.start()


if __name__ == "__main__":
    asyncio.run(init())
    bot.polling(non_stop=True,skip_pending=True)
