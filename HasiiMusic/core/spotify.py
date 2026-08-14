# ==============================================================================
# spotify.py - Spotify Integration
# ==============================================================================
# Fetches metadata from Spotify tracks, albums, and playlists using anonymous tokens.
# ==============================================================================

import re
import aiohttp
from typing import List, Union
from HasiiMusic import logger

class SpotifyAPI:
    def __init__(self):
        self.regex = re.compile(
            r"^(https:\/\/open\.spotify\.com\/(track|album|playlist)\/[a-zA-Z0-9]+)"
        )

    def valid(self, url: str) -> bool:
        """Check if URL is a valid Spotify link."""
        return bool(re.match(self.regex, url))

    async def _get_token(self) -> str:
        """Gets an anonymous access token from Spotify Web Player."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                }
                async with session.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("accessToken")
        except Exception as e:
            logger.error(f"Failed to get Spotify anonymous token: {e}")
        return None

    async def _fetch(self, endpoint: str) -> dict:
        token = await self._get_token()
        if not token:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "Mozilla/5.0",
                }
                async with session.get(f"https://api.spotify.com/v1/{endpoint}", headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Spotify API fetch failed for {endpoint}: {e}")
        return None

    async def get_track(self, url: str) -> Union[str, None]:
        track_id = url.split("track/")[1].split("?")[0]
        data = await self._fetch(f"tracks/{track_id}")
        if data:
            artists = ", ".join([artist["name"] for artist in data.get("artists", [])])
            name = data.get("name", "")
            return f"{name} - {artists}"
        return None

    async def get_playlist(self, url: str) -> List[str]:
        playlist_id = url.split("playlist/")[1].split("?")[0]
        tracks = []
        data = await self._fetch(f"playlists/{playlist_id}/tracks")
        
        while data:
            for item in data.get('items', []):
                track = item.get('track')
                if track:
                    artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                    name = track.get("name", "")
                    tracks.append(f"{name} - {artists}")
            
            # We will only fetch the first page (up to 100 tracks) to avoid rate limits on anonymous token
            break
            
        return tracks

    async def get_album(self, url: str) -> List[str]:
        album_id = url.split("album/")[1].split("?")[0]
        tracks = []
        data = await self._fetch(f"albums/{album_id}/tracks")
        
        if data:
            for track in data.get('items', []):
                if track:
                    artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                    name = track.get("name", "")
                    tracks.append(f"{name} - {artists}")
                    
        return tracks
