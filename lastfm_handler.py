import requests
import os
from dotenv import load_dotenv

load_dotenv()


class LastFMHandler:
    """Handle Last.fm API interactions for audio analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('LASTFM_API_KEY')
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        
        if not self.api_key:
            raise ValueError("LASTFM_API_KEY must be set in .env file")
    
    def search_track(self, artist: str, track: str):
        """
        Search for a track on Last.fm
        
        Args:
            artist: Artist name
            track: Track name
            
        Returns:
            dict with track info or None if not found
        """
        try:
            params = {
                'method': 'track.search',
                'track': track,
                'artist': artist,
                'api_key': self.api_key,
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results', {}).get('trackmatches', {}).get('track'):
                return data['results']['trackmatches']['track'][0]
            return None
            
        except Exception as e:
            print(f"Error searching Last.fm: {e}")
            return None
    
    def get_track_tags(self, artist: str, track: str):
        """
        Get tags/genres for a track from Last.fm
        
        Args:
            artist: Artist name
            track: Track name
            
        Returns:
            list of tags/genres
        """
        try:
            params = {
                'method': 'track.getTopTags',
                'artist': artist,
                'track': track,
                'api_key': self.api_key,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            tags = data.get('toptags', {}).get('tag', [])
            return [tag['name'] for tag in tags[:5]] if tags else []
            
        except Exception as e:
            print(f"Debug: Error fetching tags from Last.fm: {e}")
            return []
    
    def get_artist_info(self, artist: str):
        """
        Get artist information from Last.fm
        
        Args:
            artist: Artist name
            
        Returns:
            dict with artist info
        """
        try:
            params = {
                'method': 'artist.getInfo',
                'artist': artist,
                'api_key': self.api_key,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'artist' in data:
                artist_info = data['artist']
                return {
                    'name': artist_info.get('name', artist),
                    'listeners': artist_info.get('stats', {}).get('listeners', 'N/A'),
                    'playcount': artist_info.get('stats', {}).get('playcount', 'N/A'),
                    'tags': [tag['name'] for tag in artist_info.get('tags', {}).get('tag', [])[:5]]
                }
            return None
            
        except Exception as e:
            print(f"Debug: Error fetching artist info from Last.fm: {e}")
            return None
    
    def infer_audio_features_from_tags(self, tags: list) -> dict:
        """
        Infer audio characteristics from Last.fm tags/genres
        
        Args:
            tags: List of genre tags
            
        Returns:
            dict with estimated audio features (energy, danceability, valence, etc.)
        """
        # Map genres to estimated audio characteristics
        genre_mapping = {
            'electronic': {'energy': 0.7, 'danceability': 0.8, 'valence': 0.6, 'tempo': 120},
            'techno': {'energy': 0.8, 'danceability': 0.9, 'valence': 0.5, 'tempo': 128},
            'house': {'energy': 0.75, 'danceability': 0.85, 'valence': 0.7, 'tempo': 120},
            'edm': {'energy': 0.85, 'danceability': 0.85, 'valence': 0.7, 'tempo': 128},
            'deep house': {'energy': 0.6, 'danceability': 0.75, 'valence': 0.6, 'tempo': 115},
            'dnb': {'energy': 0.9, 'danceability': 0.8, 'valence': 0.5, 'tempo': 175},
            'drum and bass': {'energy': 0.9, 'danceability': 0.8, 'valence': 0.5, 'tempo': 175},
            'ambient': {'energy': 0.3, 'danceability': 0.2, 'valence': 0.5, 'tempo': 80},
            'experimental': {'energy': 0.6, 'danceability': 0.4, 'valence': 0.4, 'tempo': 110},
            'indie': {'energy': 0.6, 'danceability': 0.5, 'valence': 0.6, 'tempo': 110},
            'pop': {'energy': 0.7, 'danceability': 0.7, 'valence': 0.8, 'tempo': 120},
            'rock': {'energy': 0.8, 'danceability': 0.5, 'valence': 0.6, 'tempo': 115},
            'hip-hop': {'energy': 0.8, 'danceability': 0.75, 'valence': 0.5, 'tempo': 100},
            'rap': {'energy': 0.8, 'danceability': 0.75, 'valence': 0.5, 'tempo': 100},
            'jazz': {'energy': 0.6, 'danceability': 0.6, 'valence': 0.7, 'tempo': 110},
            'classical': {'energy': 0.5, 'danceability': 0.2, 'valence': 0.6, 'tempo': 90},
            'metal': {'energy': 0.9, 'danceability': 0.4, 'valence': 0.3, 'tempo': 130},
            'punk': {'energy': 0.9, 'danceability': 0.6, 'valence': 0.4, 'tempo': 140},
            'folk': {'energy': 0.4, 'danceability': 0.3, 'valence': 0.6, 'tempo': 95},
            'indie pop': {'energy': 0.65, 'danceability': 0.6, 'valence': 0.7, 'tempo': 115},
            'synth': {'energy': 0.75, 'danceability': 0.75, 'valence': 0.6, 'tempo': 125},
            'synthwave': {'energy': 0.7, 'danceability': 0.7, 'valence': 0.6, 'tempo': 120},
            'lo-fi': {'energy': 0.3, 'danceability': 0.4, 'valence': 0.6, 'tempo': 85},
            'chill': {'energy': 0.4, 'danceability': 0.4, 'valence': 0.6, 'tempo': 90},
            'dark': {'energy': 0.7, 'danceability': 0.6, 'valence': 0.3, 'tempo': 120},
            'industrial': {'energy': 0.85, 'danceability': 0.7, 'valence': 0.3, 'tempo': 125},
        }
        
        # Default values
        features = {
            'tempo': 120,
            'key': 0,
            'mode': 1,
            'energy': 0.5,
            'danceability': 0.5,
            'valence': 0.5,
            'acousticness': 0.3,
            'instrumentalness': 0.0,
            'liveness': 0.2,
            'loudness': -5.0
        }
        
        # Aggregate features from all tags
        if tags:
            tag_features = {
                'energy': [], 
                'danceability': [], 
                'valence': [],
                'tempo': []
            }
            
            for tag in tags:
                tag_lower = tag.lower()
                for genre, props in genre_mapping.items():
                    if genre in tag_lower or tag_lower in genre:
                        tag_features['energy'].append(props.get('energy', 0.5))
                        tag_features['danceability'].append(props.get('danceability', 0.5))
                        tag_features['valence'].append(props.get('valence', 0.5))
                        tag_features['tempo'].append(props.get('tempo', 120))
            
            # Average the values from all matching tags
            if tag_features['energy']:
                features['energy'] = sum(tag_features['energy']) / len(tag_features['energy'])
            if tag_features['danceability']:
                features['danceability'] = sum(tag_features['danceability']) / len(tag_features['danceability'])
            if tag_features['valence']:
                features['valence'] = sum(tag_features['valence']) / len(tag_features['valence'])
            if tag_features['tempo']:
                features['tempo'] = int(sum(tag_features['tempo']) / len(tag_features['tempo']))
        
        return features
