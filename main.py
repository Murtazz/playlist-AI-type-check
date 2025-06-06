from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
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

    # 🎉 Test fetching top tracks
    headers = {"Authorization": f"Bearer {access_token}"}
    top_tracks_response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)

    if top_tracks_response.status_code != 200:
        return JSONResponse(content={"error": "Failed to fetch top tracks", "details": top_tracks_response.json()}, status_code=top_tracks_response.status_code)

    top_tracks_data = top_tracks_response.json()
    preview_urls = [
        track["preview_url"]
        for track in top_tracks_data.get("items", [])
        if track.get("preview_url")
    ]
    
    return {
        "access_token": access_token,
        "preview_urls": preview_urls,
        "raw_tracks": top_tracks_data
    }
    #return {"access_token": access_token, "top_tracks": top_tracks.json()}
