from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Replace these with your own values
api_id = 20352207
api_hash = 'f34d99e7c959eb3474e6ae18009b1ab7'

print("Enter your phone number:")
phone_number = input().strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start(phone=phone_number)
    session_string = client.session.save()
    print(f'Session string: {session_string}')
# import asyncio
# from datetime import datetime
#
# from telethon import TelegramClient, events, Button
# from telethon.errors import UserAlreadyParticipantError, FloodWaitError, RPCError
# from telethon.sessions import StringSession
# from telethon.tl.functions.channels import InviteToChannelRequest
#
# source_channel = -4763136998  # Replace with your actual source channel ID
# target_channel = -4740223156 # Replace with your target channel ID
#   # Replace with the actual target channel ID
# api_id = 20009068
# api_hash = '20159f383884c4757c6f67d148eff996'
# string_session = '1ApWapzMBuxxxl1k2LUm2ETrqyVPMLL4T6jNUMqT_pEWFGYghIABa0PkZm8n1szw1cm51FXSd9XSgA9u-FH94OJaH6odkkkwe7JRV7NJ5ny26VjaSL-wBAcS97obb5bjjBnZ2qgEBUQOS5n4HfJeAmM4jU4GLfvddMyWXl347y40AUiFvDwoZlMb6JIJfjM-ZYYrCSLW16ZJ2iNn1pu2b8GLUbONdWPwF2hiVRsins6dBMMhVGvmS95GCJz92-fyRwHki6NorMIobbNGupledmqVdNQTOi5_mnINYePcZeK8KGosFMIML4-5GTnBC-VQXYHn7_uqvHBpYh9Xi1lp1bOgVvEmNU7g='
# client = TelegramClient(StringSession(string_session), api_id, api_hash)
#
# greeted_users = {}
#
# banned_words = ['kot', 'mol', 'garang', 'tom', 'kalanga', 'kt', 'axmoq', 'jinni','it','eshak','ahmoq']
#
# @client.on(events.NewMessage(incoming=True))
# async def handler(event):
#     if event.is_private:
#         print("Fetching members from the source channel...")
#         user_id = event.sender_id
#         users = await client.get_participants(source_channel)
#         for user in users:
#             # try:
#             #         user_to_add = await client.get_input_entity(user.id)  # Userni to‘g‘ri formatga o‘tkazish
#             #         await client(InviteToChannelRequest(target_channel, [user_to_add]))
#             #         print(f"✅ Added {user.username or user.id} to the target channel.")
#             #
#             #         await client.send_message(user.id, "Salom! Sizni yangi kanalimizga qo'shdik. 😊 Foydali ma'lumotlar uchun kuzatib boring!")
#             #
#             # except UserAlreadyParticipantError:
#             #         print(f"⚠️ {user.username or user.id} is already in the target channel.")
#             #
#             # except FloodWaitError as e:
#             #         print(f"⏳ Flood wait error: Sleeping for {e.seconds} seconds...")
#             #         await asyncio.sleep(e.seconds)
#             #
#             # except RPCError as e:
#             #         print(f"❌ Could not add {user.username or user.id}. Error: {e}")
#             #
#             # except Exception as e:
#             #         print(f"⚠️ Unexpected error adding {user.username or user.id}: {e}")
#
#
#             current_date = datetime.now().date()
#
#
#             last_greeted = greeted_users.get(user_id)
#             if last_greeted is None or last_greeted < current_date:
#                 await event.respond('Assalomu alaykum. Men xusanboy tomonidan yasalgan avto javob beraman. Habaringizni yuboring', buttons=[Button.text('salom')])
#                 greeted_users[user_id] = current_date
#
#             message_text = event.message.message.lower()
#             if message_text == 'ok':
#                 await event.respond('Men xusanboy tomonidan yaratilgan botman kim xoxlasa menga yozsiz yo bomasam stop disa toxteman')
#             if any(banned_word in message_text for banned_word in banned_words):
#                 await event.respond('Yomon soz gapirmasdan gaplashelik iltimos')
#
#             if event.message.text.lower().startswith('/yomon_soz_qoshish '):
#                 new_word = event.message.text[len('/yomon_soz_qoshish '):].strip().lower()
#                 if new_word and new_word not in banned_words:
#                     banned_words.append(new_word)
#                     await event.respond(f'Taqiqlangan soz  "{new_word}" muafiqiyatli qoshildi')
#                 elif new_word in banned_words:
#                     await event.respond(f'Tanlangan soz "{new_word}" allaqachon yozilgan')
#                 else:
#                     await event.respond('qoshishga berilgan soz yo\'q')
#
#
#
#
#
# with client:
#     print("Client is running...")
#     client.run_until_disconnected()