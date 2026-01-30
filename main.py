import os
import asyncio
from pyrogram import Client, filters
import yt_dlp
import instaloader # إعادة إضافة مكتبة إنستغرام

# إعدادات الحساب المستمدة من بيئة العمل
API_ID = int(os.environ.get("API_ID", 26644107))
API_HASH = os.environ.get("API_HASH", "7a081449705be63d5fc3338aa5f0314f")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
L = instaloader.Instaloader()

@app.on_message(filters.command("info"))
async def get_info(client, message):
    chat = message.chat
    info_text = f"📢 بيانات القناة الحالية:\n- الاسم: {chat.title}\n- الآيدي: `{chat.id}`"
    await message.reply_text(info_text)

@app.on_message(filters.text & ~filters.command(["start", "info"]))
async def handle_all(client, message):
    text = message.text

    # 1. إذا كان النص يوزر إنستغرام يبدأ بـ @
    if text.startswith("@"):
        msg = await message.reply_text("📸 جاري جلب بروفايل إنستغرام...")
        try:
            username = text.replace("@", "")
            profile = instaloader.Profile.from_username(L.context, username)
            await client.send_photo(message.chat.id, photo=profile.profile_pic_url, caption=f"👤 حساب: {username}")
            await msg.delete()
        except Exception:
            await msg.edit("❌ لم يتم العثور على الحساب")
            
    # 2. إذا كان النص رابطاً (يوتيوب، إنستا، فيسبوك، سناب، تيك توك)
    elif text.startswith(("http://", "https://")):
        msg = await message.reply_text("⏳ جاري سحب الميديا...")
        try:
            # معالجة روابط الصور المباشرة
            if any(ext in text.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', 'unsplash']):
                await client.send_photo(message.chat.id, photo=text, caption="✅ تم سحب الصورة")
                await msg.delete()
            
            # معالجة الفيديوهات من كل المواقع
            else:
                ydl_opts = {'format': 'best', 'outtmpl': 'media_file.mp4', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([text])
                await client.send_video(message.chat.id, video='media_file.mp4', caption="✅ تم النشر بواسطة المدير")
                os.remove('media_file.mp4')
                await msg.delete()
        except Exception:
            await msg.edit("❌ خطأ: الرابط غير مدعوم أو خاص")
            if os.path.exists('media_file.mp4'): os.remove('media_file.mp4')

    # 3. إذا كان نصاً عادياً (قصيدة) لا يفعل شيئاً (يحل مشكلة صورة 1000025349.jpg)
    else:
        return

app.run()
            
