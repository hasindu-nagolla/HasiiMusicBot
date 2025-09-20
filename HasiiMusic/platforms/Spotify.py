# import re
# import asyncio

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from youtubesearchpython.__future__ import VideosSearch

# # Adjust as needed for your config management
# import config

# class SpotifyAPI:
#     def __init__(self):
#         self.regex = r"^(https:\/\/open.spotify.com\/)(.*)$"
#         self.client_id = config.SPOTIFY_CLIENT_ID
#         self.client_secret = config.SPOTIFY_CLIENT_SECRET
#         if self.client_id and self.client_secret:
#             self.client_credentials_manager = SpotifyClientCredentials(
#                 client_id=self.client_id,
#                 client_secret=self.client_secret,
#             )
#             self.spotify = spotipy.Spotify(
#                 client_credentials_manager=self.client_credentials_manager
#             )
#         else:
#             self.spotify = None

#     async def valid(self, link: str) -> bool:
#         return bool(re.search(self.regex, link))

#     async def track(self, link: str):
#         # Run synchronous Spotipy call in thread pool to avoid blocking event loop
#         loop = asyncio.get_event_loop()
#         track = await loop.run_in_executor(None, self.spotify.track, link)
#         info = track["name"]
#         for artist in track["artists"]:
#             fetched = f' {artist["name"]}'
#             if "Various Artists" not in fetched:
#                 info += fetched
#         # Search YouTube for the song
#         results = VideosSearch(info, limit=1)
#         yt_results = await results.next()
#         first_result = yt_results["result"][0] if yt_results["result"] else None
#         if not first_result:
#             return None, None
#         ytlink = first_result["link"]
#         title = first_result["title"]
#         vidid = first_result["id"]
#         duration_min = first_result["duration"]
#         thumbnail = first_result["thumbnails"][0]["url"].split("?")[0]
#         track_details = {
#             "title": title,
#             "link": ytlink,
#             "vidid": vidid,
#             "duration_min": duration_min,
#             "thumb": thumbnail,
#         }
#         return track_details, vidid

#     async def playlist(self, url):
#         loop = asyncio.get_event_loop()
#         playlist = await loop.run_in_executor(None, self.spotify.playlist, url)
#         playlist_id = playlist["id"]
#         results = []
#         for item in playlist["tracks"]["items"]:
#             music_track = item["track"]
#             info = music_track["name"]
#             for artist in music_track["artists"]:
#                 fetched = f' {artist["name"]}'
#                 if "Various Artists" not in fetched:
#                     info += fetched
#             results.append(info)
#         return results, playlist_id

#     async def album(self, url):
#         loop = asyncio.get_event_loop()
#         album = await loop.run_in_executor(None, self.spotify.album, url)
#         album_id = album["id"]
#         results = []
#         for item in album["tracks"]["items"]:
#             info = item["name"]
#             for artist in item["artists"]:
#                 fetched = f' {artist["name"]}'
#                 if "Various Artists" not in fetched:
#                     info += fetched
#             results.append(info)
#         return results, album_id

#     async def artist(self, url):
#         loop = asyncio.get_event_loop()
#         artistinfo = await loop.run_in_executor(None, self.spotify.artist, url)
#         artist_id = artistinfo["id"]
#         artisttoptracks = await loop.run_in_executor(None, self.spotify.artist_top_tracks, url)
#         results = []
#         for item in artisttoptracks["tracks"]:
#             info = item["name"]
#             for artist in item["artists"]:
#                 fetched = f' {artist["name"]}'
#                 if "Various Artists" not in fetched:
#                     info += fetched
#             results.append(info)
#         return results, artist_id

# # Usage example (in an async function):
# # spotify_api = SpotifyAPI()
# # if await spotify_api.valid(spotify_url):
# #     track_info, vidid = await spotify_api.track(spotify_url)
# #     # play track_info["link"] with your bot logic


import re
import asyncio

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython.__future__ import VideosSearch

# Adjust as needed for your config management
import config

class SpotifyAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/open.spotify.com\/)(.*)$"
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = config.SPOTIFY_REDIRECT_URI  # add this to your config.py
        if self.client_id and self.client_secret and self.redirect_uri:
            # Use user-level OAuth with cache for refresh tokens!
            self.auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope="user-read-private user-library-read playlist-read-private",
                cache_path="HasiiMusic/assets/.spotify_token"
            )
            self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
        else:
            self.spotify = None

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.regex, link))

    async def track(self, link: str):
        # Run synchronous Spotipy call in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        track = await loop.run_in_executor(None, self.spotify.track, link)
        info = track["name"]
        for artist in track["artists"]:
            fetched = f' {artist["name"]}'
            if "Various Artists" not in fetched:
                info += fetched
        # Search YouTube for the song
        results = VideosSearch(info, limit=1)
        yt_results = await results.next()
        first_result = yt_results["result"][0] if yt_results["result"] else None
        if not first_result:
            return None, None
        ytlink = first_result["link"]
        title = first_result["title"]
        vidid = first_result["id"]
        duration_min = first_result["duration"]
        thumbnail = first_result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": ytlink,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def playlist(self, url):
        loop = asyncio.get_event_loop()
        playlist = await loop.run_in_executor(None, self.spotify.playlist, url)
        playlist_id = playlist["id"]
        results = []
        for item in playlist["tracks"]["items"]:
            music_track = item["track"]
            info = music_track["name"]
            for artist in music_track["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, playlist_id

    async def album(self, url):
        loop = asyncio.get_event_loop()
        album = await loop.run_in_executor(None, self.spotify.album, url)
        album_id = album["id"]
        results = []
        for item in album["tracks"]["items"]:
            info = item["name"]
            for artist in item["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, album_id

    async def artist(self, url):
        loop = asyncio.get_event_loop()
        artistinfo = await loop.run_in_executor(None, self.spotify.artist, url)
        artist_id = artistinfo["id"]
        artisttoptracks = await loop.run_in_executor(None, self.spotify.artist_top_tracks, url)
        results = []
        for item in artisttoptracks["tracks"]:
            info = item["name"]
            for artist in item["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, artist_id

# Usage example (in an async function):
# spotify_api = SpotifyAPI()
# if await spotify_api.valid(spotify_url):
#     track_info, vidid = await spotify_api.track(spotify_url)
#     # play track_info["link"] with your bot logic
