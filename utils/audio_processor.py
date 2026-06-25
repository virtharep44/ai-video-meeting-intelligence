import yt_dlp
from pydub import AudioSegment
import os
import shutil

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    # Cookies ko /tmp/ mein copy karo (writable folder)
    cookies_src = "/etc/secrets/www.youtube.com_cookies.txt"
    cookies_tmp = "/tmp/youtube_cookies.txt"
    shutil.copy(cookies_src, cookies_tmp)
    
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "outtmpl": output_path,
        "cookiefile": cookies_tmp,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename
