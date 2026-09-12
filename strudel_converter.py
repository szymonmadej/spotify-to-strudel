import os
from datetime import datetime


class StrudelConverter:
    """Convert audio features to Strudel music code"""
    
    def __init__(self, track_info: dict, audio_features: dict):
        self.track_info = track_info
        self.audio_features = audio_features
        self.code = None
    
    def generate(self) -> str:
        """
        Generate Strudel code based on audio features
        
        Returns:
            Strudel code as string
        """
        if self.code:
            return self.code
        
        # Extract features
        tempo = int(self.audio_features.get('tempo', 120))
        energy = self.audio_features.get('energy', 0.5)
        brightness = self.audio_features.get('brightness', 0.5)
        danceability = self.audio_features.get('danceability', 0.5)
        valence = self.audio_features.get('valence', 0.5)
        acousticness = self.audio_features.get('acousticness', 0.3)
        
        # Generate header
        code = self._generate_header()
        
        # Generate drum pattern
        code += self._generate_drums(energy, danceability)
        
        # Generate bass pattern
        code += self._generate_bass(energy, danceability, valence)
        
        # Generate melody
        code += self._generate_melody(brightness, valence, energy)
        
        # Generate chords
        code += self._generate_chords(valence, acousticness)
        
        # Generate effects
        code += self._generate_effects(energy, brightness)
        
        # Generate outro
        code += self._generate_outro()
        
        self.code = code
        return code
    
    def _generate_header(self) -> str:
        """Generate Strudel header with metadata"""
        artist = self.track_info.get('artist', 'Unknown')
        track = self.track_info.get('name', 'Unknown')
        tempo = int(self.audio_features.get('tempo', 120))
        
        header = f"""// Generated from: {artist} - {track}
// Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Tempo: {tempo} BPM

setcps({tempo / 60 / 4})

"""
        return header
    
    def _generate_drums(self, energy: float, danceability: float) -> str:
        """
        Generate drum pattern based on energy and danceability
        
        High energy + high danceability → fast, complex drums
        Low energy → simple, slow drums
        """
        code = "// DRUMS\n"
        
        # Kick pattern based on danceability
        if danceability > 0.7:
            # Fast, regular kick
            kick_pattern = "[1 0 0.5 0]"
            kick_density = 1
        elif danceability > 0.5:
            # Medium kick
            kick_pattern = "[1 0 0 0]"
            kick_density = 1
        else:
            # Slow kick
            kick_pattern = "[1 0 0 0]"
            kick_density = 0.5
        
        code += f"""d1
  .sound("kick")
  .speed({kick_density * 2})
  .n(
    "{kick_pattern}".slow(2)
  )
  .gain(0.9)
"""
        
        # Snare pattern based on energy
        if energy > 0.7:
            snare_pattern = "[0 1 0.5 1]"
        elif energy > 0.4:
            snare_pattern = "[0 1 0 1]"
        else:
            snare_pattern = "[0 1]"
        
        code += f"""d2
  .sound("snare")
  .n("{snare_pattern}".slow(1))
  .gain(0.8)
"""
        
        # Hat pattern based on energy
        if energy > 0.8:
            hat_pattern = "[1 0.5 1 0.5 1 0.5 1 0.5]"
            hat_speed = 0.5
        elif energy > 0.6:
            hat_pattern = "[1 0 1 0 1 0 1 0]"
            hat_speed = 0.75
        else:
            hat_pattern = "[1 0 1 0]"
            hat_speed = 1
        
        code += f"""d3
  .sound("hat")
  .n("{hat_pattern}".slow(2))
  .gain({0.5 + energy * 0.3})
  .speed({hat_speed})
"""
        
        return code
    
    def _generate_bass(self, energy: float, danceability: float, valence: float) -> str:
        """
        Generate bass pattern based on energy, danceability, and valence
        """
        code = "// BASS\n"
        
        # Determine bass character
        if energy > 0.7 and danceability > 0.7:
            # Punchy synth bass
            bass_type = "sine"
            bass_notes = "[0 5 3 7]"
            bass_speed = 0.5
        elif energy > 0.5:
            # Medium bass
            bass_type = "triangle"
            bass_notes = "[0 3 0 5]"
            bass_speed = 1
        else:
            # Deep, slow bass
            bass_type = "sine"
            bass_notes = "[0 0]"
            bass_speed = 2
        
        # Adjust for valence (minor vs major feel)
        if valence < 0.4:
            # Minor key feeling
            scale_offset = -2
        else:
            # Major key feeling
            scale_offset = 0
        
        code += f"""d4
  .sound("sine")
  .n(
    "{bass_notes}".scale("c:minor".repeat(4)).add({scale_offset})
  )
  .gain({0.6 + energy * 0.2})
  .lpf({400 + danceability * 400})
  .attack(0.05)
  .release(0.5)
  .slow({bass_speed})
"""
        
        return code
    
    def _generate_melody(self, brightness: float, valence: float, energy: float) -> str:
        """
        Generate melody based on brightness, valence, and energy
        """
        code = "// MELODY\n"
        
        # Melody density based on brightness
        if brightness > 0.7:
            # Bright, complex melody
            melody_pattern = "[0 2 4 5 7 5 4 2]"
            melody_speed = 0.25
        elif brightness > 0.4:
            # Medium melody
            melody_pattern = "[0 3 5 7 5 3]"
            melody_speed = 0.5
        else:
            # Dark, simple melody
            melody_pattern = "[0 2 0 5]"
            melody_speed = 1
        
        # Scale based on valence
        if valence > 0.6:
            scale = "c:major"
        else:
            scale = "c:minor"
        
        code += f"""d5
  .sound("triangle")
  .n(
    "{melody_pattern}".scale("{scale}".repeat(4)).add(12)
  )
  .gain({0.3 + brightness * 0.3})
  .lpf({2000 + brightness * 2000})
  .attack(0.1)
  .release(0.2)
  .slow({melody_speed})
"""
        
        return code
    
    def _generate_chords(self, valence: float, acousticness: float) -> str:
        """
        Generate chord progression based on valence and acousticness
        """
        code = "// CHORDS\n"
        
        # Chord type based on acousticness
        if acousticness > 0.6:
            synth_type = "triangle"
            attack = 0.05
            release = 0.3
        else:
            synth_type = "square"
            attack = 0.01
            release = 0.1
        
        # Chord progression based on valence
        if valence > 0.6:
            # Happy progression
            chords = "[0 4 7]"  # C major
        elif valence > 0.3:
            # Neutral progression
            chords = "[0 3 7]"  # C minor
        else:
            # Sad progression
            chords = "[0 3 6]"  # C diminished
        
        code += f"""d6
  .sound("{synth_type}")
  .n("{chords}".scale("c:minor".repeat(2)))
  .gain({0.2 + acousticness * 0.2})
  .lpf(1500)
  .attack({attack})
  .release({release})
  .slow(2)
  .pan(perlin(now().div(4)).range(-0.3, 0.3))
"""
        
        return code
    
    def _generate_effects(self, energy: float, brightness: float) -> str:
        """
        Generate effects based on energy and brightness
        """
        code = "// EFFECTS\n"
        
        # Reverb based on brightness
        reverb_amount = 1 - brightness
        
        code += f"""// Master effects
all
  .lpf({{
    const freq = 5000 + perlin(now().div(8)).range(-1000, 1000);
    return freq;
  }})
  .gain(0.8)
"""
        
        return code
    
    def _generate_outro(self) -> str:
        """Generate outro/footer"""
        code = "\n// Uncomment to add more patterns below:\n"
        code += "// d7...\n"
        code += "// d8...\n"
        return code
    
    def save_to_file(self, filename: str = None) -> str:
        """
        Save generated code to file
        
        Args:
            filename: Output filename (default: artist_track.strudel)
            
        Returns:
            Path to saved file
        """
        if not self.code:
            self.generate()
        
        if filename is None:
            artist = self.track_info.get('artist', 'Unknown').replace(' ', '_')
            track = self.track_info.get('name', 'Unknown').replace(' ', '_')
            filename = f"{artist}_{track}.strudel"
        
        # Ensure .strudel extension
        if not filename.endswith('.strudel'):
            filename += '.strudel'
        
        with open(filename, 'w') as f:
            f.write(self.code)
        
        return os.path.abspath(filename)
