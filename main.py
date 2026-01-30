import os
import asyncio
from pyrogram import Client, filters
import yt_dlp
import instaloader

# إعدادات الاتصال (سيتم جلبها من Railway Variables)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

L = instaloader.Instaloader()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "💀 **مرحباً بك في بوت سحب الميديا العالمي!**\n\n"
        "أرسل لي رابطاً من:\n"
        "📸 Instagram\n"
        "🎬 TikTok\n"
        "👻 Snapchat\n"
        "👥 Facebook\n\n"
        "سأقوم بجلب الصورة أو الفيديو لك فوراً!"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_scraper(client, message):
    url = message.text
    msg = await message.reply_text("🔍 جاري فحص الرابط واستخراج الميديا...")

    try:
        # --- محرك Instagram ---
        if "instagram.com" in url:
            shortcode = url.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            await client.send_photo(message.chat.id, photo=post.url, caption="✅ تم السحب من إنستقرام")

        # --- محرك TikTok & Snapchat ---
        elif "tiktok.com" in url or "snapchat.com" in url:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                await client.send_document(message.chat.id, document=info['url'], caption="✅ تم السحب بنجاح")

        # --- محرك Facebook ---
        elif "facebook.com" in url:
            # فيسبوك غالباً ما يعمل عبر yt-dlp أيضاً للمنشورات العامة
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                await client.send_video(message.chat.id, video=info['url'], caption="✅ تم السحب من فيسبوك")

        else:
            await msg.edit("❌ عذراً، هذا الرابط غير مدعوم حالياً.")
        
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ حدث خطأ أثناء السحب: {str(e)}")

print("💀 WORM-AI IS LIVE...")
app.run()
              
