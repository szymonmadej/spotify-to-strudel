import requests
import librosa
import numpy as np
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()


class AudioAnalyzer:
    """Analyze audio files to extract musical characteristics"""
    
    def __init__(self):
        pass
    
    def download_and_analyze(self, preview_url: str) -> dict:
        """
        Download audio preview and analyze it
        
        Args:
            preview_url: URL to MP3 preview file
            
        Returns:
            dict with analyzed audio features
        """
        try:
            if not preview_url:
                print("⚠️  No preview URL available")
                return None
            
            print("📥 Downloading audio preview...")
            response = requests.get(preview_url, timeout=10)
            response.raise_for_status()
            
            # Load audio from bytes
            print("🔍 Analyzing audio...")
            audio_data = BytesIO(response.content)
            y, sr = librosa.load(audio_data, sr=None)
            
            # Extract features
            features = self._extract_features(y, sr)
            return features
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error downloading preview: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Error analyzing audio: {e}")
            return None
    
    def _extract_features(self, y: np.ndarray, sr: int) -> dict:
        """
        Extract musical features from audio
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            dict with features
        """
        try:
            # Estimate tempo (BPM)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
            tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
            
            # Energy (RMS)
            S = librosa.feature.melspectrogram(y=y, sr=sr)
            energy = librosa.power_to_db(S, ref=np.max).mean()
            energy_normalized = np.clip((energy + 80) / 80, 0, 1)  # Normalize to 0-1
            
            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            brightness = spectral_centroids.mean() / sr * 2  # Normalize
            brightness_normalized = np.clip(brightness, 0, 1)
            
            # Zero crossing rate (percussiveness)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            percussiveness = zcr.mean()
            
            # MFCC (timbre characteristics)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = mfcc.mean(axis=1)
            
            # RMS energy for dynamics
            S = np.abs(librosa.stft(y))
            rms = librosa.feature.rms(S=S)[0]
            dynamics = rms.std() / (rms.mean() + 1e-10)
            dynamics_normalized = np.clip(dynamics, 0, 1)
            
            # Spectral rolloff (high frequency content)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            high_freq_content = rolloff.mean() / sr
            high_freq_normalized = np.clip(high_freq_content, 0, 1)
            
            # Chroma features (harmonic content)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_energy = chroma.mean()
            
            return {
                'tempo': max(60, min(tempo, 200)),  # Clamp tempo to reasonable range
                'energy': np.clip(energy_normalized, 0, 1),
                'brightness': np.clip(brightness_normalized, 0, 1),
                'percussiveness': np.clip(percussiveness, 0, 1),
                'dynamics': dynamics_normalized,
                'high_freq_content': high_freq_normalized,
                'harmonic_content': np.clip(chroma_energy, 0, 1),
                'danceability': self._estimate_danceability(onset_env, sr),
                'valence': self._estimate_valence(brightness_normalized, chroma_energy),
                'mfcc': mfcc_mean.tolist()
            }
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def _estimate_danceability(self, onset_env: np.ndarray, sr: int) -> float:
        """
        Estimate danceability from onset strength
        
        Args:
            onset_env: Onset strength envelope
            sr: Sample rate
            
        Returns:
            danceability score 0-1
        """
        try:
            # Danceability is related to beat regularity
            onset_strength = onset_env.mean()
            # Normalize and scale
            danceability = np.clip(onset_strength * 2, 0, 1)
            return danceability
        except:
            return 0.5
    
    def _estimate_valence(self, brightness: float, harmonic_content: float) -> float:
        """
        Estimate valence (happiness) from brightness and harmonic content
        
        Args:
            brightness: Spectral centroid normalized 0-1
            harmonic_content: Chroma energy 0-1
            
        Returns:
            valence score 0-1
        """
        try:
            # Bright and harmonic = happy (high valence)
            # Dark and inharmonic = sad (low valence)
            valence = (brightness * 0.6 + harmonic_content * 0.4)
            return np.clip(valence, 0, 1)
        except:
            return 0.5
    
    def analyze_from_file(self, file_path: str) -> dict:
        """
        Analyze audio from local file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            dict with analyzed features
        """
        try:
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                return None
            
            print(f"🔍 Analyzing audio file: {file_path}")
            y, sr = librosa.load(file_path, sr=None)
            features = self._extract_features(y, sr)
            return features
            
        except Exception as e:
            print(f"⚠️  Error analyzing file: {e}")
            return None
