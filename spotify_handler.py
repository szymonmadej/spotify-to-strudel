import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
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
            dict with track info (name, artist, tempo, key, etc.)
        """
        try:
            track = self.sp.track(track_id)
            return {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'external_urls': track['external_urls']['spotify']
            }
        except Exception as e:
            print(f"Error fetching track info: {e}")
            return None
    
    def get_audio_features(self, track_id):
        """
        Get audio features from Spotify (tempo, key, mode, etc.)
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            dict with audio features
        """
        try:
            features = self.sp.audio_features(track_id)[0]
            return {
                'tempo': features['tempo'],
                'key': features['key'],
                'mode': features['mode'],  # 0 = minor, 1 = major
                'time_signature': features['time_signature'],
                'energy': features['energy'],
                'danceability': features['danceability'],
                'valence': features['valence'],  # musical positiveness
                'acousticness': features['acousticness'],
                'instrumentalness': features['instrumentalness'],
                'liveness': features['liveness'],
                'loudness': features['loudness'],
                'speechiness': features['speechiness']
            }
        except Exception as e:
            print(f"Error fetching audio features: {e}")
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
