import yt_dlp
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from ytmusicapi import YTMusic
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC

# Telegram bot token
API_TOKEN = "7667728415:AAFTFJxkse85cbQ-dyXK0Bm8X-E1hA4Tu8E"

# Initialize bot & dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize YT Music API
ytmusic = YTMusic()

# Function to download song from YouTube Music
def download_yt_music(song_url, filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([song_url])

# Function to get song details from YT Music
def get_song_details(song_name):
    search_results = ytmusic.search(song_name, filter="songs")
    if search_results:
        song = search_results[0]
        video_id = song["videoId"]
        title = song["title"]
        artist = song["artists"][0]["name"]
        album = song["album"]["name"] if "album" in song else "Unknown Album"
        cover_url = song["thumbnails"][-1]["url"]  # Get the highest resolution cover
        return video_id, title, artist, album, cover_url
    return None, None, None, None, None

# Function to embed metadata in MP3
def add_metadata(mp3_file, title, artist, album, cover_url):
    audio = MP3(mp3_file, ID3=ID3)
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TALB(encoding=3, text=album))

    response = requests.get(cover_url)
    with open("cover.jpg", "wb") as f:
        f.write(response.content)

    with open("cover.jpg", "rb") as f:
        audio.tags.add(APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read()
        ))

    audio.save()

# Handle /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("🎵 Send me a **song name**, and I'll download it from YouTube Music with album details!")

# Handle song search & download
@dp.message_handler()
async def fetch_song(message: types.Message):
    song_name = message.text
    filename = "song.mp3"

    # Get song details
    video_id, title, artist, album, cover_url = get_song_details(song_name)

    if not video_id:
        await message.reply("❌ Song not found on YouTube Music!")
        return

    youtube_url = f"https://music.youtube.com/watch?v={video_id}"

    # Download song
    await message.reply("⏳ Downloading from YouTube Music...")
    download_yt_music(youtube_url, filename)

    # Add metadata
    add_metadata(filename, title, artist, album, cover_url)

    # Send MP3 file
    caption = f"🎵 **{title}**\n👤 {artist}\n📀 {album}"
    await bot.send_audio(message.chat.id, audio=open(filename, 'rb'), caption=caption)

executor.start_polling(dp)
