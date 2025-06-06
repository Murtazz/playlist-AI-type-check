from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from track_downloader import search_youtube, download_video
from audio_analysis import extract_features_from_file
import os
import requests
import urllib.parse

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


@app.get("/")
def login():
    scopes = "user-top-read user-library-read"
    url = (
        "https://accounts.spotify.com/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&scope={urllib.parse.quote(scopes)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    )
    return RedirectResponse(url)


@app.get("/callback")
def callback(request: Request, code: str = None):
    token_url = "https://accounts.spotify.com/api/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return {"error": "Failed to get access token", "details": token_data}

    headers = {"Authorization": f"Bearer {access_token}"}
    top_tracks_response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)

    if top_tracks_response.status_code != 200:
        return {
            "error": "Failed to fetch top tracks",
            "details": top_tracks_response.json(),
            "status_code": top_tracks_response.status_code,
        }

    top_tracks_data = top_tracks_response.json()
    features = {}

    for track in top_tracks_data.get("items", []):
        track_name = f"{track['name']} {track['artists'][0]['name']}"
        filename = f"{track['id']}.mp3"

        try:
            youtube_url = search_youtube(track_name)
            download_video(youtube_url, filename)
            features = extract_features_from_file(filename)
            os.remove(filename)  # cleanup
            break  # process only one
        except Exception as e:
            print(f"Error processing {track_name}: {e}")

    return {
        "access_token": access_token,
        "extracted_features": features,
        "raw_tracks": top_tracks_data,
    }


@app.get("/analyze")
def analyze_track(query: str = Query(..., description="Search term for the track")):
    filename = query.replace(" ", "_").lower() + ".mp3"

    try:
        youtube_url = search_youtube(query)
        download_video(youtube_url, filename)
        features = extract_features_from_file(filename)
        os.remove(filename)
        return {
            "track": query,
            "features": features,
        }
    except Exception as e:
        return {"error": f"Failed to analyze '{query}': {str(e)}"}