# ==============================================================================
# spotify.py - Spotify Integration
# ==============================================================================
# Fetches metadata from Spotify tracks, albums, and playlists.
# ==============================================================================

import re
import asyncio
from typing import List, Tuple, Union

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from HasiiMusic import config, logger

class SpotifyAPI:
    def __init__(self):
        self.regex = re.compile(
            r"^(https:\/\/open\.spotify\.com\/(track|album|playlist)\/[a-zA-Z0-9]+)"
        )
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        
        self.spotify = None
        if self.client_id and self.client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
                self.spotify = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
            except Exception as e:
                logger.error(f"❌ Spotify initialization failed: {e}")
        else:
            logger.warning("⚠️ Spotify API credentials not found. Spotify links will not work.")

    def valid(self, url: str) -> bool:
        """Check if URL is a valid Spotify link."""
        return bool(re.match(self.regex, url))

    async def get_track(self, url: str) -> Union[str, None]:
        """Returns 'Track Name - Artist' for a single track."""
        if not self.spotify:
            return None
        
        try:
            track = await asyncio.to_thread(self.spotify.track, url)
            if track:
                artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                name = track.get("name", "")
                return f"{name} - {artists}"
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch Spotify track: {e}")
            return None
        return None

    async def get_playlist(self, url: str) -> List[str]:
        """Returns a list of 'Track Name - Artist' for all tracks in a playlist."""
        if not self.spotify:
            return []
            
        tracks = []
        try:
            results = await asyncio.to_thread(self.spotify.playlist_tracks, url)
            while results:
                for item in results['items']:
                    track = item.get('track')
                    if track:
                        artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                        name = track.get("name", "")
                        tracks.append(f"{name} - {artists}")
                
                # Handle pagination if playlist is large
                if results['next']:
                    results = await asyncio.to_thread(self.spotify.next, results)
                else:
                    break
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch Spotify playlist: {e}")
        return tracks

    async def get_album(self, url: str) -> List[str]:
        """Returns a list of 'Track Name - Artist' for all tracks in an album."""
        if not self.spotify:
            return []
            
        tracks = []
        try:
            results = await asyncio.to_thread(self.spotify.album_tracks, url)
            while results:
                for track in results['items']:
                    if track:
                        artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                        name = track.get("name", "")
                        tracks.append(f"{name} - {artists}")
                
                if results['next']:
                    results = await asyncio.to_thread(self.spotify.next, results)
                else:
                    break
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch Spotify album: {e}")
        return tracks
