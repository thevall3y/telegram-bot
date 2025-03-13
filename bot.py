import logging
import os
import yt_dlp
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Replace with your bot token
BOT_TOKEN = "7667728415:AAFTFJxkse85cbQ-dyXK0Bm8X-E1hA4Tu8E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

async def download_video(url):
    """Downloads video from YouTube, TikTok, Facebook, or Instagram"""
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Send me a video URL from TikTok, YouTube, Instagram, or Facebook.")

@dp.message_handler()
async def handle_message(message: types.Message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "facebook.com" in url or "instagram.com" in url:
        await message.reply("Downloading your video, please wait...")
        video_path = await download_video(url)

        if video_path and os.path.exists(video_path):
            await bot.send_video(message.chat.id, open(video_path, "rb"))
            os.remove(video_path)
        else:
            await message.reply("Failed to download the video.")
    else:
        await message.reply("Invalid URL. Please send a valid video link.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
