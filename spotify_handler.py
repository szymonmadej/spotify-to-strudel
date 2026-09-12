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
            dict with audio features, or default values if not available
        """
        # Default audio features (fallback values)
        default_features = {
            'tempo': 120,
            'key': 0,
            'mode': 1,  # 0 = minor, 1 = major
            'time_signature': 4,
            'energy': 0.5,
            'danceability': 0.5,
            'valence': 0.5,  # musical positiveness
            'acousticness': 0.5,
            'instrumentalness': 0.0,
            'liveness': 0.5,
            'loudness': 0.0,
            'speechiness': 0.0
        }
        
        try:
            features = self.sp.audio_features(track_id)[0]
            if not features:
                print("⚠️  No audio features found, using defaults")
                return default_features
            
            return {
                'tempo': features.get('tempo', default_features['tempo']),
                'key': features.get('key', default_features['key']),
                'mode': features.get('mode', default_features['mode']),
                'time_signature': features.get('time_signature', default_features['time_signature']),
                'energy': features.get('energy', default_features['energy']),
                'danceability': features.get('danceability', default_features['danceability']),
                'valence': features.get('valence', default_features['valence']),
                'acousticness': features.get('acousticness', default_features['acousticness']),
                'instrumentalness': features.get('instrumentalness', default_features['instrumentalness']),
                'liveness': features.get('liveness', default_features['liveness']),
                'loudness': features.get('loudness', default_features['loudness']),
                'speechiness': features.get('speechiness', default_features['speechiness'])
            }
        except SpotifyException as e:
            if e.http_status == 403:
                print("⚠️  Access to audio features denied (403), using default values")
                print("    This might be due to API permissions or regional restrictions")
            else:
                print(f"⚠️  Spotify API error: {e}")
            return default_features
        except Exception as e:
            print(f"⚠️  Could not fetch audio features ({type(e).__name__}), using defaults")
            return default_features
    
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
