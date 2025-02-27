import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated, BotCommand, ChatInviteLink, \
    CallbackQuery

from invite_tracker import get_or_create_user, increment_invite_count, get_top_invites, me, init, get_channel, \
    create_channel

# Replace with your bot token
BOT_TOKEN = "6778014003:AAHm5szBDWkIrPOfp985Xt19ytmilbmgRLU"

# Required channels
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def get_channel_link(channel_id):
    try:
        chat = await bot.get_chat(channel_id)
        if chat.username:  # If the channel has a username
            return f"https://t.me/{chat.username}"
        else:
            raise AttributeError  # Force fallback if no username
    except Exception:
        try:
            invite_link: ChatInviteLink = await bot.create_chat_invite_link(channel_id)
            return invite_link.invite_link  # Fallback to invite link
        except Exception as e:
            return f"Error: {e}"  # Handle errors gracefully


async def check_membership(user_id: int):
    """Checks which channels the user is not a member of."""
    not_joined = []
    CHANNELS = await get_channel(action=True)
    for channel in CHANNELS:
        try:
            chat_member = await bot.get_chat_member(chat_id=f"{channel.channel_id}", user_id=user_id)
            if chat_member.status in ["left", "kicked"]:
                not_joined.append(channel.channel_id)
        except TelegramBadRequest:
            pass  # If bot has no access
    return not_joined


async def keyboard(user_id):
    channels = []
    keyboard1 = []
    CHANNELS = await get_channel()
    for channel in CHANNELS:
        try:
            chat_member = await bot.get_chat_member(chat_id=f"{await get_channel_link(channel_id=channel.channel_id)}",
                                                    user_id=user_id)
            if chat_member.is_member:
                channels.append(channel.channel_id)
                keyboard1.append(InlineKeyboardButton(text=f"{channel}", callback_data=f"ch_{channel}"))
        except TelegramBadRequest:
            pass  # If bot has no access


async def get_join_buttons(not_joined_channels):
    """Generates inline keyboard buttons for channels the user hasn't joined."""
    buttons = [
        [InlineKeyboardButton(text=f"{(await bot.get_chat(channel)).full_name}",
                              url=f"{await get_channel_link(channel_id=channel)}")]
        for channel in not_joined_channels
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name[:25]

    # Ensure the user is in the database
    await get_or_create_user(user_id, name=first_name)

    # Check if the user has joined the required channels
    not_joined = await check_membership(user_id)

    if not_joined:  # User has NOT joined all channels
        text = "🚀 To continue, please join the required channels below:"
        await message.answer(text, reply_markup=await get_join_buttons(not_joined))
        return

    # If it's a private chat
    if message.chat.type == "private":
        await message.answer("🔹 Iltimos, quyidagi funksiyalardan birini tanlang:\n\n"
                             "📌 /me – Shaxsiy ma'lumotlaringizni ko‘rish\n"
                             "🏆 /top – Top 20 ta eng faol foydalanuvchilarni ko‘rish")
        # channels = await get_channel(action='all')  # Get all required channels
        #
        # keyboard2 = InlineKeyboardMarkup(inline_keyboard=[])  # Initialize an empty keyboard
        #
        # for channel in channels:
        #     user_channel = await bot.get_chat_member(chat_id=int(channel.channel_id), user_id=user_id)
        #     if user_channel:
        #         print('a')
        #         channel_name = (await bot.get_chat(chat_id=channel.channel_id)).full_name
        #         button = InlineKeyboardButton(text=f"{channel_name}", callback_data=f"ch_{channel.channel_id}")
        #         keyboard2.inline_keyboard.append([button])  # Append each button as a new row
        # await bot.send_message(
        #     chat_id=user_id,
        #     text=f'👋 Assalomu alykum {first_name}!\n\nQaysi kanaldagi natijangizni korishni xoxlaysiz?',
        #     reply_markup=keyboard2
        # )

    else:
        await message.delete()


@dp.callback_query(F.data.startswith("ch_"))
async def ch(call: CallbackQuery):
    data = call.data.split("_")[1]
    channel = await me(call.from_user.id, data)
    channel_name = await bot.get_chat(chat_id=data)
    if channel:
        text = (f'📢 Kanal nomi: <a href="{get_channel_link(data)}">{channel_name.full_name}</a>\n\n'
                f"<a href='tg://user?id={call.from_user.id}'>{(await get_or_create_user(call.from_user.id)).name}</a> - <code>{channel.count}</code> ta odam qo\'shgansiz")
        await call.message.edit_text(text=text + '\n\n/start botni boshqatan boshlash uchun',parse_mode="HTML")
    else:
        text = (f'📢 Kanal nomi:{channel_name.full_name}\n\n'
                f"Siz hali bitta ham odam qoshmagansiz")
        await call.message.edit_text(text=text + '\n\n/start botni boshqatan boshlash uchun',parse_mode="HTML")


@dp.chat_member(ChatMemberUpdatedFilter)
async def chat_member_update(event: ChatMemberUpdated):
    user_id = event.new_chat_member.user.id
    first_name = event.new_chat_member.user.first_name[:30]
    inviter_id = event.from_user.id if event.from_user else None  # Check if someone invited
    try:
        await bot.delete_message(chat_id=event.chat.id, message_id=event.message.message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")
    # Get or create user
    await get_or_create_user(user_id, name=first_name)

    # Check if the user was added by someone else
    if event.old_chat_member.status in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED} and \
            event.new_chat_member.status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR}:

        if inviter_id and inviter_id != user_id:  # Make sure the inviter exists and is not the same as the user
            await increment_invite_count(inviter_id, user_id, event.chat.id)  # Only increment if invited

    not_joined = await check_membership(user_id)
    if not_joined:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ You must join the required channels to use the bot.",
                reply_markup=await get_join_buttons(not_joined)
            )
        except TelegramBadRequest:
            pass  # Handle user blocking the bot
    else:
        try:
            welcome_messages = [
                f"👋 Salom {event.from_user.full_name}! Xush kelibsiz! 🚀",
                f"🎉 Wow! {event.from_user.full_name} bizga qo‘shildi! Xush kelibsiz! 🥳",
                f"🔥 {event.from_user.full_name}, siz yetib keldingiz! Marhamat! 🎯",
                f"🌟 Xush kelibsiz, {event.from_user.full_name}! Yorqin porlang! 💎✨",
                f"🚀 Start! {event.from_user.full_name} safimizga qo‘shildi! 🌌",
                f"🎊 Bayram boshlansin! {event.from_user.full_name} yetib keldi! 🎈🥳",
                f"🤩 {event.from_user.full_name}, sizni kutib olamiz! Boshladik! 🏆",
                f"💡 Xush kelibsiz, {event.from_user.full_name}! Sizni yangi imkoniyatlar kutmoqda! 🌍",
                f"🛸 {event.from_user.full_name}, kosmik sayohatga xush kelibsiz! 👽",
                f"🎮 O‘yinga xush kelibsiz, {event.from_user.full_name}! 🕹️🔥",
                f"🔑 Yangi uyingizga xush kelibsiz, {event.from_user.full_name}! 🏠💖",
                f"⚡ Boom! {event.from_user.full_name} yetib keldi! Energiya to‘la! ⚡🔥",
                f"🚀 Belbog‘ingizni bog‘lang, {event.from_user.full_name}! Hozir boshlanadi! 🎢",
                f"🏆 Xush kelibsiz, chempion {event.from_user.full_name}! G‘alaba sari! 💪🥇",
                f"🎶 Ding-dong! {event.from_user.full_name} chatga kirdi! 🎵🎉",
                f"💎 Noyob odam qo‘shildi! Xush kelibsiz, {event.from_user.full_name}! 💎✨",
                f"🍕 Kim qo‘shimcha zavq buyurtma qildi? {event.from_user.full_name} qo‘shildi! 🍕🎉",
                f"🌈 Sehrli olamga xush kelibsiz, {event.from_user.full_name}! 🦄✨",
                f"💼 Ishbilarmonlar orasiga xush kelibsiz, {event.from_user.full_name}! 🏢🔥",
                f"🛠️ {event.from_user.full_name}, hozir ajoyib narsalar sodir bo‘ladi! 🚧",
                f"🚦 Yashil chiroq yondi! {event.from_user.full_name} start berdi! 🏁",
                f"🎯 Maqsad aniq! {event.from_user.full_name} biz bilan! 🚀",
                f"🔔 Diqqat! {event.from_user.full_name} yangi mehmon! 🎉",
                f"📢 E’tibor bering! {event.from_user.full_name} keldi! 🔥",
                f"🚲 Sayohat endi boshlanadi! {event.from_user.full_name}, xush kelibsiz! 🌍",
                f"🎤 Mikrofon sizda! {event.from_user.full_name}, o‘z so‘zingizni ayting! 🎙️",
                f"📈 Yangi bosqichga chiqdingiz! {event.from_user.full_name}, marhamat! 📊",
                f"🦸 {event.from_user.full_name}, super kuchingizni ko‘rsatishga tayyormisiz? 💥",
                f"🎆 Foydalanuvchilar orasida yangi yulduz! {event.from_user.full_name}! 🌟",
                f"💪 Katta jamoaga xush kelibsiz, {event.from_user.full_name}! 🔥",
                f"🎲 Taxtani o‘rnating! {event.from_user.full_name} o‘yin boshladi! 🎮",
                f"🚀 Raketa uchirildi! {event.from_user.full_name} qo‘shildi! 🚀",
                f"🌍 Dunyo bo‘ylab sayohat boshlanadi! {event.from_user.full_name}, xush kelibsiz! ✈️",
                f"⚽ Stadion to‘ldi! {event.from_user.full_name} maydonda! 🏟️",
                f"🍩 Shirin mehmon keldi! {event.from_user.full_name}, xush kelibsiz! 🍰",
                f"📚 Yangi bilimlar sari! {event.from_user.full_name}, xush kelibsiz! 📖",
                f"🤖 Botlar ham xursand! {event.from_user.full_name}, xush kelibsiz! 🤖",
                f"⏳ Sabr bilan kutgan edik! {event.from_user.full_name} keldi! 🎉",
                f"🎩 Sehr-jodu boshlanadi! {event.from_user.full_name}, marhamat! 🎩✨",
                f"🚢 Kema yo‘lga tushdi! {event.from_user.full_name} qo‘shildi! ⚓",
                f"🎭 Tomosha endi boshlanadi! {event.from_user.full_name}, xush kelibsiz! 🎬",
                f"🌟 Sehrli portal ochildi! {event.from_user.full_name}, xush kelibsiz! 🌀",
                f"🕶️ Trenddagi foydalanuvchi! {event.from_user.full_name} endi biz bilan! 🔥",
                f"🚀 Kosmik sarguzasht! {event.from_user.full_name}, xush kelibsiz! 🌠",
                f"🎩 Sehrgarlar jamoasiga xush kelibsiz, {event.from_user.full_name}! ✨",
                f"💼 Tadbirga rasmiy qo‘shildingiz! {event.from_user.full_name}, marhamat! 🏢",
                f"🎲 Omad siz bilan bo‘lsin! {event.from_user.full_name}, xush kelibsiz! 🍀",
                f"💌 Xabaringiz qabul qilindi! {event.from_user.full_name}, marhamat! 📩",
                f"🎮 O‘yin qoidalarini bilasizmi? {event.from_user.full_name}, xush kelibsiz! 🕹️",
                f"📸 Kamera tayyor! {event.from_user.full_name}, tabassum! 📷",
                f"🎉 Barchani hushnud etadigan mehmon! {event.from_user.full_name}, xush kelibsiz! 🎊",
                f"🎯 Hamma diqqat qilsin! {event.from_user.full_name} kelib qo‘shildi! 🏹",
                f"📢 Yangilik! {event.from_user.full_name} endi biz bilan! 🎙️",
                f"🚦 Start tugmasi bosildi! {event.from_user.full_name}, tayyormisiz? 🏎️",
                f"⚔️ Sarguzasht endi boshlanadi! {event.from_user.full_name}, xush kelibsiz! 🏹",
                f"🎵 Musikaga mos ravishda harakatlaning! {event.from_user.full_name}, xush kelibsiz! 🎧",
                f"🏆 Mukofot o‘z egasini topdi! {event.from_user.full_name}, xush kelibsiz! 🥇",
                f"🔑 Yangi eshik ochildi! {event.from_user.full_name}, xush kelibsiz! 🚪",
                f"🔥 Jamoaga yangi energiya qo‘shildi! {event.from_user.full_name}, xush kelibsiz! ⚡",
                f"📜 Sarguzasht tafsilotlarini o‘qib chiqing! {event.from_user.full_name}, xush kelibsiz! 📖",
                f"🏹 Maqsadga yetishamiz! {event.from_user.full_name}, xush kelibsiz! 🎯",
                f"💼 Muvaffaqiyat sari bir qadam! {event.from_user.full_name}, xush kelibsiz! 📊",
                f"🎭 Sahna sizniki! {event.from_user.full_name}, o‘z rolini bajaring! 🎬",
                f"🏰 Qasrning yangi a’zosi! {event.from_user.full_name}, xush kelibsiz! 🏰",
                f"🛰️ Aloqa o‘rnatildi! {event.from_user.full_name}, xush kelibsiz! 📡",
                f"⚡ Qudratli kuch! {event.from_user.full_name}, xush kelibsiz! 🔥",
                f"🎲 Tavakkal qiling! {event.from_user.full_name}, xush kelibsiz! 🎲"
            ]

            await bot.send_message(
                chat_id=user_id,
                text=welcome_messages[
                         random.randint(0, len(welcome_messages) - 1)] + '\n\n/start -botni qayta yurgazish uchun'
            )
        except TelegramBadRequest:
            pass  # Handle user blocking the bot


@dp.message(Command("top"))
async def top_invites_handler(message: types.Message):
    """Shows the leaderboard of top inviters."""
    if message.chat.type == "private":
        channels = await get_channel(action='all')  # Get all required channels

        keyboard2 = InlineKeyboardMarkup(inline_keyboard=[])  # Initialize an empty keyboard

        for channel in channels:
            user_channel = await bot.get_chat_member(chat_id=int(channel.channel_id), user_id=message.from_user.id)
            if user_channel:
                channel_name = (await bot.get_chat(chat_id=channel.channel_id)).full_name
                button = InlineKeyboardButton(text=f"{channel_name}", callback_data=f"cht_{channel.channel_id}")
                keyboard2.inline_keyboard.append([button])  # Append each button as a new row
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'👋 Assalomu alykum {message.from_user.first_name}!\n\nQaysi kanaldagi natijangizni korishni xoxlaysiz?',
            reply_markup=keyboard2
        )
        return
    top_users = await get_top_invites(message.chat.id)

    if not top_users:
        await message.answer("🏆 No invitations yet!")
        return

    leaderboard = "🏆 Top Inviters:\n" + "\n".join(
        [
            f"{i + 1}. <a href='tg://user?id={user.user_id}'>{(await get_or_create_user(user_id=user.user_id)).name}</a> - {user.count} invites"
            for i, user in enumerate(top_users)]
    )
    await message.answer(leaderboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith('cht_'))
async def cht(call: CallbackQuery):
    channel_id = call.data.split('_')[1]  # Assuming `data` is stored in call.data

    # Get top invites
    top_invites = await get_top_invites(channel_id, limit=20)

    # Get channel name
    channel_name = await bot.get_chat(chat_id=channel_id)

    # Prepare text message
    text = f'📢 Kanal nomi: {channel_name.full_name}\n\n'

    if top_invites:
        text += "\n".join(
            [
                f"{i + 1}. <a href='tg://user?id={invite.user_id}'>{(await get_or_create_user(invite.user_id)).name}</a> - {invite.count} ta odam"
                for i, invite in enumerate(top_invites)]
        )
    else:
        text += "Hali hech kim taklif qilmagan."

    await call.message.edit_text(text=text + '\n\n/start botni boshqatan boshlash uchun', parse_mode="HTML")


@dp.message(Command("me"))
async def personal_stats_handler(message: types.Message):
    """Shows the user's invite count."""
    if message.chat.type == "private":
        channels = await get_channel(action='all')  # Get all required channels

        keyboard2 = InlineKeyboardMarkup(inline_keyboard=[])  # Initialize an empty keyboard

        for channel in channels:
            user_channel = await bot.get_chat_member(chat_id=int(channel.channel_id), user_id=message.from_user.id)
            if user_channel:
                channel_name = (await bot.get_chat(chat_id=channel.channel_id)).full_name
                button = InlineKeyboardButton(text=f"{channel_name}", callback_data=f"ch_{channel.channel_id}")
                keyboard2.inline_keyboard.append([button])  # Append each button as a new row
        await bot.send_message(
            chat_id=message.from_user.id,
            text="📊 Qaysi kanal bo‘yicha natijangizni ko‘rmoqchisiz? Tanlang ⬇️",
            reply_markup=keyboard2
        )
        return
    print(message.from_user.id, message.chat.id)
    user = await me(message.from_user.id, message.chat.id)
    if not user:
        await message.answer("🔹 You haven't invited anyone yet!")
    else:
        await message.answer(f"🔹 You have invited {user.count} people!")


@dp.message(CommandStart)
async def start(message: types.Message):
    if message.chat.type == "private":
        await message.answer('/start ni bosing botni yurgazish uchun')


async def commands():
    await bot.set_my_commands(commands=[BotCommand(command="start", description="Start the bot"),
                                        BotCommand(command="top", description="Show the top invites"),
                                        BotCommand(command='me', description='To get your invited people count')])
    await create_channel('-1002488771920', action=True)
    await create_channel('-1002303095317', action=True)


async def main():
    """Start the bot."""
    await init()
    await commands()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('bye')
