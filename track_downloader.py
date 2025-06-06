from youtubesearchpython import VideosSearch
import yt_dlp

def search_youtube(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    video_id = result['result'][0]['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

def download_video(url, filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

