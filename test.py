import random
from telethon import TelegramClient
from telethon.sessions.string import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
import asyncio

api_id = 20352207
api_hash = 'f34d99e7c959eb3474e6ae18009b1ab7'
string_session = '1ApWapzMBu6fUr5W3VFCv4RAElYWq_OyXYJDgaZ91-hBAi75Y572rry_wyv2wtV8ldKLIaAkyU_Zeq5uhhYrWFfWrA0tZYKbfUxR7qmpKp7_BczO1Nr-LCFc0GaxKzo_MOGtR74ZHd8sEjyrNT_32smtp0om8CCaAjLJ5T6uq78t6u9LWiSZ_wDy7wnIH5wz5yD3WZaVLhaGLP_ecvop3-Hz1yNOgh5xN9LQCaO9M0KiyH7GsnBGXigkzi49BbRDrdyhz-DD_Z-MvAJRfUIwfzkKKOcp0uIfsPQvX8Gf0LWSOsG6jV-8H0vvoqBySHHqO-l3i0_Ke-WjzXP3ca5BbkjE9f2eHtzI='
client = TelegramClient(StringSession(string_session), api_id, api_hash)
loop = asyncio.get_event_loop()
origin = 'onus_global'
destination = 'testaiogram1'
invited = []

async def transfer():
    origin_entity = await client.get_entity(origin)  # Fetch the actual group
    destination_entity = await client.get_entity(destination)

    users = []
    async for user in client.iter_participants(origin_entity):
        users.append(user)  # Collect users first

    print(f"Total users found: {len(users)}")  # Debugging


    for user in users:  # Now loop through the list
        try:
            await client(InviteToChannelRequest(destination_entity, [user]))
            print(f"Invited {user.id}")
            await asyncio.sleep(random.randint(30, 60))  # Prevent rate limits
        except Exception as e:
            print(f"Failed to invite {user.id}: {e}")
message_text = [
    f"🚀 Don't Miss Out! Join (channel_link) now and be part of something exciting! Cutting-edge content, great discussions, and an awesome community await. See you inside! 🔥",
    f"🔥 Exclusive Access Awaits! Only a few truly know where the magic happens. You’re about to be one of them. Click (channel_link) and step into something special. 🌟",
    f"💡 Ready to upgrade your game? The smartest minds are already inside (channel_link). Are you? Join now and find out what you've been missing! 🚀",
    f"😲 Did you hear? The best conversations, insights, and content are happening at (channel_link). Don’t be the last one to know!",
    f"🌍 Connect with like-minded people and explore amazing content at (channel_link). Why wait? Join now!",
    f"🎯 One click could change everything. Tap (channel_link) and see for yourself why everyone is talking about this community!",
    f"🔥 This is your sign! Stop scrolling and tap (channel_link). You won’t regret it!",
    f"💎 Hidden gems don’t stay hidden for long. Join (channel_link) now before everyone else does!",
    f"⏳ Time-sensitive invitation: The best content and discussions are happening at (channel_link)! Will you be there?",
    f"🎉 Join the movement! (channel_link) is where all the action happens. Don’t miss out!",
    f"📢 Important announcement! Something BIG is happening at (channel_link). Join now to be a part of it!",
    f"💥 Boom! You just found your new favorite place on Telegram. Click (channel_link) and thank me later!",
    f"🚀 Ready to take things to the next level? (channel_link) is where you need to be!",
    f"🎁 Surprise! A whole new world of content is waiting for you at (channel_link). Don’t keep it waiting!",
    f"🔑 Unlock exclusive content and insider knowledge at (channel_link). Join now and stay ahead of the game!",
    f"🕵️‍♂️ Psst... I found something amazing. It’s called (channel_link). Check it out before the secret gets out!",
    f"🎯 If you're seeing this, it's your chance to join something great. Click (channel_link) and let’s go!",
    f"📌 Save this link: (channel_link). You'll want to come back to it again and again!",
    f"⚡ Energy, excitement, and exclusive content—all waiting for you at (channel_link). Join now!",
    f"📡 Transmission received: (channel_link) is the place to be. Are you in?",
    f"🧲 If you love valuable content and great discussions, you’ll be drawn to (channel_link). It’s that good!",
    f"🛎️ Ding ding! Your VIP invitation to (channel_link) is here. Click the link and claim your spot!",
    f"💥 Explosive content alert! If you want to stay in the loop, join (channel_link) right now!",
    f"🛑 Stop everything! You need to check out (channel_link) ASAP. Trust me on this one.",
    f"🎊 Congratulations! You’ve just unlocked access to something amazing. Click (channel_link) to see for yourself!",
    f"🌱 Grow your knowledge, connect with awesome people, and stay informed. (channel_link) is where it’s at!",
    f"🔮 Want to see the future? It starts at (channel_link). Don’t be late!",
    f"💯 If you love top-tier content and discussions, then (channel_link) is your new home. Join now!",
    f"🎙️ Breaking news! A must-join community is waiting for you at (channel_link). Click the link and step in!",
    f"🎈 It’s happening! The best online space is growing, and you’re invited. Join (channel_link) today!"
]

async def send_messages():
    async for user in client.iter_participants(origin):
        try:
            if user.bot:  # Skip bots
                continue

            await client.send_message(user.id, message_text[random.randint(0, len(message_text) - 1)])
            print(f"✅ Sent message to {user.id}")

            # Random delay to prevent flood limit
            delay = random.randint(30, 60)  # Wait 30-60 seconds
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"❌ Failed to send message to {user.id}: {e}")

with client:
    # client.loop.run_until_complete(transfer())
    client.loop.run_until_complete(send_messages())
