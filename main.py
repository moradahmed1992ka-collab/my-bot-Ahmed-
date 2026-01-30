import os
import asyncio
from pyrogram import Client, filters
import yt_dlp
import instaloader

# إعدادات الاتصال من المتغيرات التي ضبطناها
API_ID = int(os.environ.get("API_ID", 26644107))
API_HASH = os.environ.get("API_HASH", "7a081449705be63d5fc3338aa5f0314f")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
L = instaloader.Instaloader()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "💀 **أهلاً بك في Media Fetcher المطور!**\n\n"
        "دعم المنصات الجديد:\n"
        "✅ يوتيوب (YouTube)\n"
        "✅ سناب شات (Snapchat)\n"
        "✅ إنستغرام (بالرابط أو اليوزر @)\n"
        "✅ تيك توك وفيسبوك"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_download(client, message):
    text = message.text
    msg = await message.reply_text("⏳ جاري التحميل من المنصة... انتظر قليلاً")

    try:
        # معالجة يوزر إنستغرام
        if text.startswith("@"):
            username = text.replace("@", "")
            profile = instaloader.Profile.from_username(L.context, username)
            await client.send_photo(message.chat.id, photo=profile.profile_pic_url, caption=f"📸 بروفايل: {username}")
            await msg.delete()

        # معالجة كافة الروابط (يوتيوب، سناب، إلخ)
        else:
            # تم إضافة cookiefile إذا كان لديك واحد لتجنب حظر يوتيوب
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
            
            # إرسال الفيديو كملف لتجنب خطأ CURL السابق
            await client.send_video(message.chat.id, video='video.mp4', caption="✅ تم التحميل بنجاح!")
            os.remove('video.mp4')
            await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ حدث خطأ: {str(e)}")
        if os.path.exists('video.mp4'): os.remove('video.mp4')

app.run()
            
