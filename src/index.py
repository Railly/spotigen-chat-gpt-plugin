import os
from typing import Annotated
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.dtos.api import TrackTitles, TrackURIs
from src.utils import get_spotify_client
from src.services.spotify import SpotifyClient

app = FastAPI()

_ENV = os.environ.get('VERCEL_ENV')

origins = ["https://chat.openai.com"] if _ENV == 'production' else ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Welcome endpoint 

@app.get("/")
async def root():
    return { "message": "Welcome to Spotigen - a ChatGPT plugin for Spotify!" }


# Basic ChatGPT plugin endpoints

@app.get("/logo.png")
async def plugin_logo():
    filename = './static/logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    if _ENV == 'production':
        print(_ENV, "production")
        return FileResponse("static/ai-plugin.json")
    else:
        print(_ENV, "development")
        return FileResponse("static/ai-plugin-dev.json")

@app.get("/openapi.yaml")
async def openapi_spec():
    print("openapi.yaml", _ENV)
    return FileResponse("static/openapi.yaml")


# ChatGPT plugin endpoints for Spotify

# Route: /playlist

@app.get("/playlist")
async def get_playlist(name: str, spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)]):
    playlist = spotify_client.find_playlist(name)
    if playlist is None:
        return JSONResponse(status_code=404, content={"message": "Playlist not found"})
    else:
        return playlist

@app.post("/playlist")
async def create_playlist(name: str, public: bool, spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)]):
    playlist_id = spotify_client.create_playlist(name, public)
    return { "playlist_id": playlist_id }

# Route: /playlist/{playlist_id}/tracks

@app.get("/playlist/{playlist_id}/tracks")
async def get_playlist_tracks(playlist_id: str, spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)]):
    tracks = spotify_client.get_tracks_from_playlist(playlist_id)
    return tracks

@app.post("/playlist/{playlist_id}/tracks")
async def add_tracks_to_playlist(playlist_id: str, track_titles: TrackTitles, spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)]): 
    spotify_client.add_tracks_to_playlist(playlist_id, track_titles)
    return PlainTextResponse(status_code=200)

@app.delete("/playlist/{playlist_id}/tracks")
async def remove_tracks_from_playlist(playlist_id: str, track_uris: TrackURIs, spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)]):
    spotify_client.remove_tracks_from_playlist(playlist_id, track_uris)
    return PlainTextResponse(status_code=200)