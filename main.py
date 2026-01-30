import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import yt_dlp
import instaloader

# إعدادات الحساب الصحيحة
API_ID = int(os.environ.get("API_ID", 26644107))
API_HASH = os.environ.get("API_HASH", "7a081449705be63d5fc3338aa5f0314f")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
L = instaloader.Instaloader()

# 1. رسالة الترحيب والتعليمات
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "💀 **مرحباً بك في لوحة تحكم صدى القوافي!**\n\n"
        "أنا الآن مدير قناتك، يمكنني:\n"
        "✅ سحب ميديا (يوتيوب، تيك توك، سناب، إنستا)\n"
        "✅ جلب معلومات الأعضاء والقنوات عبر /info\n"
        "✅ الترحيب بالأعضاء الجدد تلقائياً"
    )

# 2. أمر المعلومات (إصلاح خطأ الصورة 1000025338.jpg)
@app.on_message(filters.command("info"))
async def get_info(client, message):
    chat = message.chat
    user = message.from_user
    info_text = f"📢 **بيانات القناة الحالية:**\n- الاسم: {chat.title}\n- الآيدي: `{chat.id}`\n"
    if user:
        info_text += f"👤 **المرسل:** {user.first_name}\n- آيديك: `{user.id}`"
    await message.reply_text(info_text)

# 3. ميزة الترحيب التلقائي بالأعضاء الجدد
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for member in message.new_chat_members:
        await message.reply_text(f"مرحباً بك {member.mention} في قناة صدى القوافي! 🌙")

# 4. محرك سحب الميديا والنشر (يوتيوب، سناب، إنستا، تيك توك)
@app.on_message(filters.text & ~filters.command(["start", "info"]))
async def handle_media(client, message):
    text = message.text
    msg = await message.reply_text("⏳ جاري المعالجة والنشر...")

    try:
        # سحب بروفايل إنستغرام عبر اليوزر
        if text.startswith("@"):
            username = text.replace("@", "")
            profile = instaloader.Profile.from_username(L.context, username)
            await client.send_photo(message.chat.id, photo=profile.profile_pic_url, caption=f"📸 بروفايل: {username}")
            await msg.delete()
        
        # سحب الفيديوهات من كافة المواقع
        else:
            ydl_opts = {'format': 'best', 'outtmpl': 'video_file.mp4', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
            
            # رفع الفيديو كملف لتجنب خطأ CURL
            await client.send_video(message.chat.id, video='video_file.mp4', caption="✅ تم السحب بواسطة المدير")
            os.remove('video_file.mp4')
            await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ حدث خطأ: تأكد من صحة الرابط")
        if os.path.exists('video_file.mp4'): os.remove('video_file.mp4')

app.run()

