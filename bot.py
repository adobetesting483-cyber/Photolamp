import os
from telethon import TelegramClient, events, Button
import io
from PIL import Image
import pytesseract

API_ID = os.environ['TELEGRAM_API_ID']
API_HASH = os.environ['TELEGRAM_API_HASH']
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ADMIN_ID = 5419958723
PRODUCT_PRICE = "99"

SOURCE_CHANNEL = -1003868184891
START_PHOTO_MSG_ID = 4
DEMO_MSG_IDS = [5, 6, 7, 9, 10]
QR_CODE_MSG_ID = 11

client = TelegramClient('lamp_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user_states = {}

START_TEXT = f"""
✨ **Premium Customized Photo Night Lamp** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━
Apni ya apne apno ki tasveer ko ek haseen yaad mein badlein! Yeh lamp na sirf aapke kamre ko roshan karega, balki aapke jazbaaton ko bhi ek naya andaaz dega. 🎁

🌟 **Hamari Khaasiyat (Why Choose Us?):**
✅ **Crystal Clear Printing:** High-definition 4x4 photo quality.
✅ **Premium Wooden Base:** Mazboot aur stylish finish.
✅ **Energy Efficient:** Kam bijli khapat aur long-lasting LED.
✅ **1 Year Replacement Warranty:** Poore ek saal ka bharosa.
✅ **Perfect for Gifting:** Birthday, Anniversary ya kisi bhi mauke ke liye best.

💰 **Special Launch Offer:** Just at **₹{PRODUCT_PRICE}** (Limited Time Only) ⏳
━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 **Order karne ke liye niche "Order Now" par click karein.**
"""

PAYMENT_TEXT = f"""
💳 **Final Step: Payment**

Aapka order almost ready hai! Kripya niche diye gaye QR par **₹{PRODUCT_PRICE}** pay karein aur uske baad **Payment Screenshot** yahan bhejein.

Screenshot milte hi aapka order confirmation message mil jayega. ✅
"""

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    buttons = [
        [Button.inline("🛒 Order Now", b"order_now")],
        [Button.inline("🎥 Demo", b"demo"), Button.inline("🎧 24x7 Support", b"support")]
    ]
    try:
        msg = await client.get_messages(SOURCE_CHANNEL, ids=START_PHOTO_MSG_ID)
        await client.send_file(event.chat_id, msg.photo, caption=START_TEXT, buttons=buttons)
    except:
        await event.respond(START_TEXT, buttons=buttons)

@client.on(events.CallbackQuery)
async def callback_handler(event):
    chat_id = event.chat_id
    if event.data == b"order_now":
        user_states[chat_id] = {'step': 'AWAIT_PHOTO'}
        await event.respond("📸 **Step 1:** Kripya wo **Photo** bhejein jo aap lamp par lagwana chahte hain.")
    elif event.data == b"next_to_address":
        user_states[chat_id]['step'] = 'AWAIT_ADDRESS'
        example = "Name: Rahul Verma\nAddress: H.No 123, Sector 15, Rohini, Delhi\nPincode: 110085\nMobile: 9812345678"
        await event.respond(f"📝 **Step 2: Delivery Address**\n\nKripya niche diye gaye format mein details bhejein:\n\n`{example}`")
    elif event.data == b"next_to_payment":
        user_states[chat_id]['step'] = 'AWAIT_SCREENSHOT'
        qr_msg = await client.get_messages(SOURCE_CHANNEL, ids=QR_CODE_MSG_ID)
        await client.send_file(chat_id, qr_msg.photo, caption=PAYMENT_TEXT)
    elif event.data == b"support":
        await event.respond("🎧 **Customer Support**\n\nKoi bhi sawal ho toh humein yahan message karein:\n👉 @Bookmyframesupport")
    elif event.data == b"demo":
        await event.answer("Loading Samples...", alert=False)
        demo_msgs = await client.get_messages(SOURCE_CHANNEL, ids=DEMO_MSG_IDS)
        for m in demo_msgs:
            if m.media:
                await client.send_file(chat_id, m.media)

@client.on(events.NewMessage)
async def flow_handler(event):
    chat_id = event.chat_id
    if chat_id not in user_states or event.text == '/start':
        return
    state = user_states[chat_id]['step']

    if state == 'AWAIT_PHOTO' and event.photo:
        user_states[chat_id]['user_photo'] = event.photo
        await event.respond("✅ Photo Received!", buttons=[Button.inline("Next: Address ➡️", b"next_to_address")])

    elif state == 'AWAIT_ADDRESS' and event.text:
        if len(event.text) > 15:
            user_states[chat_id]['address'] = event.text
            await event.respond("✅ Address saved successfully!", buttons=[Button.inline("Next: Payment ➡️", b"next_to_payment")])
        else:
            await event.respond("❌ Kripya pura address sahi se likh kar bhejien.")

    elif state == 'AWAIT_SCREENSHOT' and event.photo:
        await event.respond("⏳ **Verifying...** Kripya 1 minute intezar karein.")
        photo_bytes = await event.download_media(file=io.BytesIO())
        img = Image.open(photo_bytes)
        text = pytesseract.image_to_string(img)

        if PRODUCT_PRICE in text:
            await event.respond(f"🎊 **Order Confirmed!**\n\nPayment verify ho gayi hai. Aapka order process kar diya gaya hai aur 2 dino mein deliver ho jayega. Shukriya! ❤️")
            await client.send_message(ADMIN_ID, "🚀 **NEW ORDER RECEIVED!**")
            await client.send_file(ADMIN_ID, user_states[chat_id]['user_photo'], caption="Lamp Photo")
            await client.send_message(ADMIN_ID, f"📍 **Address:**\n{user_states[chat_id]['address']}")
            await client.send_file(ADMIN_ID, event.photo, caption="Verified Screenshot")
            del user_states[chat_id]
        else:
            await event.respond(f"❌ **Payment Check Failed!**\n\nScreenshot mein ₹{PRODUCT_PRICE} ka amount nahi mila. Kripya sahi screenshot bhejien.")

print("🪔 Lamp Bot is Ready!")
client.run_until_disconnected()