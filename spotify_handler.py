import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import os
from dotenv import load_dotenv

load_dotenv()


class SpotifyHandler:
    """Handle Spotify API interactions"""
    
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file")
        
        auth_manager = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def get_track_info(self, track_id):
        """
        Get track information from Spotify
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            dict with track info (name, artist, duration, etc.)
        """
        try:
            track = self.sp.track(track_id)
            return {
                'name': track.get('name', 'Unknown'),
                'artist': track['artists'][0]['name'] if track.get('artists') else 'Unknown',
                'duration_ms': track.get('duration_ms', 0),
                'popularity': track.get('popularity', 0),
                'external_urls': track.get('external_urls', {}).get('spotify', '')
            }
        except Exception as e:
            print(f"Error fetching track info: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_audio_features(self, track_id):
        """
        Get audio features from Spotify (tempo, key, mode, etc.)
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            dict with audio features, or None if not available (triggers Last.fm fallback)
        """
        try:
            features = self.sp.audio_features(track_id)[0]
            if not features:
                print("⚠️  No audio features found")
                return None
            
            return {
                'tempo': features.get('tempo', 120),
                'key': features.get('key', 0),
                'mode': features.get('mode', 1),  # 0 = minor, 1 = major
                'time_signature': features.get('time_signature', 4),
                'energy': features.get('energy', 0.5),
                'danceability': features.get('danceability', 0.5),
                'valence': features.get('valence', 0.5),  # musical positiveness
                'acousticness': features.get('acousticness', 0.5),
                'instrumentalness': features.get('instrumentalness', 0.0),
                'liveness': features.get('liveness', 0.5),
                'loudness': features.get('loudness', 0.0),
                'speechiness': features.get('speechiness', 0.0)
            }
        except SpotifyException as e:
            if e.http_status == 403:
                print("⚠️  Access to audio features denied (403)")
                print("    Falling back to Last.fm analysis...")
                return None
            else:
                print(f"⚠️  Spotify API error: {e}")
                return None
        except Exception as e:
            print(f"⚠️  Could not fetch audio features ({type(e).__name__})")
            return None
    
    def get_track_by_url(self, url):
        """
        Extract track ID from Spotify URL and get info
        
        Args:
            url: Spotify track URL
            
        Returns:
            track_id if valid, None otherwise
        """
        try:
            track_id = url.split('/')[-1].split('?')[0]
            return track_id
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return None
