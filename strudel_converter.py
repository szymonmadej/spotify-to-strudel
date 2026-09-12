from typing import Dict, List

# Note mappings
NOTE_NAMES = {
    0: 'c', 1: 'cs', 2: 'd', 3: 'ds', 4: 'e', 5: 'f',
    6: 'fs', 7: 'g', 8: 'gs', 9: 'a', 10: 'as', 11: 'b'
}

MODE_NAMES = {
    0: 'minor',
    1: 'major'
}


class StrudelConverter:
    """Convert Spotify audio features to Strudel music code"""
    
    def __init__(self, track_info: Dict, audio_features: Dict):
        self.track_info = track_info
        self.audio_features = audio_features
        self.code = []
    
    def _get_note_name(self, key: int, octave: int = 3) -> str:
        """Convert MIDI key number to note name"""
        note = NOTE_NAMES.get(key % 12, 'c')
        return f"{note}{octave}"
    
    def _get_scale_pattern(self, key: int, mode: int) -> str:
        """Generate a scale pattern based on key and mode"""
        root_note = self._get_note_name(key)
        mode_name = MODE_NAMES.get(mode, 'major')
        return f"scale('[{root_note}] {mode_name}')"
    
    def _calculate_note_duration(self, tempo: float) -> str:
        """Calculate note durations based on tempo"""
        # Assuming 4/4 time signature
        # At 120 BPM, a quarter note = 0.5 seconds
        beat_duration = 60 / tempo
        return f"// Beat duration at {tempo} BPM: ~{beat_duration:.2f}s"
    
    def _generate_bass_pattern(self) -> str:
        """Generate a bass pattern based on audio features"""
        root = self._get_note_name(self.audio_features['key'], octave=1)
        energy = self.audio_features['energy']
        
        # More energetic = faster bass pattern
        if energy > 0.7:
            pattern = f'"{root} . {root}:0.5 . {root}:0.5"'
        elif energy > 0.4:
            pattern = f'"{root} . . {root}:0.5"'
        else:
            pattern = f'"{root} . . ."'
        
        return f"bass = s('sine').note({pattern}.fast(2)).gain(0.3)"
    
    def _generate_chord_pattern(self) -> str:
        """Generate chord pattern based on key and mode"""
        key = self.audio_features['key']
        mode = self.audio_features['mode']
        root_note = self._get_note_name(key)
        mode_name = MODE_NAMES.get(mode, 'major')
        danceability = self.audio_features['danceability']
        
        # Generate chords based on danceability
        if danceability > 0.7:
            chords = '"[0,2,4] [1,3,5] [2,4,6] [1,3,5]"'
        elif danceability > 0.4:
            chords = '"[0,2,4] . . [1,3,5]"'
        else:
            chords = '"[0,2,4] . . ."'
        
        return f"chords = s('sine').scale('[{root_note}] {mode_name}').note({chords}.fast(1)).gain(0.4)"
    
    def _generate_melody_pattern(self) -> str:
        """Generate melody pattern based on valence and energy"""
        valence = self.audio_features['valence']
        energy = self.audio_features['energy']
        key = self.audio_features['key']
        root_note = self._get_note_name(key)
        mode_name = MODE_NAMES.get(self.audio_features['mode'], 'major')
        
        # Happy/positive = higher notes, energetic = faster
        if valence > 0.6 and energy > 0.6:
            melody = '"[0,4] [2,5] [4,7] [5,9]"'
            speed = ".fast(2)"
        elif valence > 0.4:
            melody = '"0 2 4 5 4 2"'
            speed = ".fast(1.5)"
        else:
            melody = '"0 . 2 . 4 ."'
            speed = ".fast(1)"
        
        return f"melody = s('sine').scale('[{root_note}] {mode_name}').note({melody}{speed}).gain(0.3)"
    
    def generate(self) -> str:
        """Generate complete Strudel code"""
        self.code = []
        
        # Header comment
        self.code.append("// Generated Strudel code from Spotify")
        self.code.append(f"// Track: {self.track_info['name']} by {self.track_info['artist']}")
        self.code.append(f"// Tempo: {self.audio_features['tempo']} BPM")
        self.code.append(f"// Key: {self._get_note_name(self.audio_features['key'])} {MODE_NAMES.get(self.audio_features['mode'], 'major')}")
        self.code.append("")
        
        # Tempo setting
        self.code.append(f"setcps({self.audio_features['tempo'] / 120 / 4}) // {self.audio_features['tempo']} BPM")
        self.code.append("")
        
        # Duration info
        self.code.append(self._calculate_note_duration(self.audio_features['tempo']))
        self.code.append("")
        
        # Bass pattern
        self.code.append("// Bass pattern")
        self.code.append(self._generate_bass_pattern())
        self.code.append("")
        
        # Chord pattern
        self.code.append("// Chord progression")
        self.code.append(self._generate_chord_pattern())
        self.code.append("")
        
        # Melody pattern
        self.code.append("// Melody")
        self.code.append(self._generate_melody_pattern())
        self.code.append("")
        
        # Combined pattern
        self.code.append("// Combined arrangement")
        self.code.append("stack(")
        self.code.append("  bass,")
        self.code.append("  chords,")
        self.code.append("  melody")
        self.code.append(")")
        self.code.append("")
        
        # Audio features as comments
        self.code.append("// Audio Features Analysis:")
        self.code.append(f"// Energy: {self.audio_features['energy']:.2f} (0-1)")
        self.code.append(f"// Danceability: {self.audio_features['danceability']:.2f} (0-1)")
        self.code.append(f"// Valence: {self.audio_features['valence']:.2f} (0-1, happiness)")
        self.code.append(f"// Acousticness: {self.audio_features['acousticness']:.2f} (0-1)")
        self.code.append(f"// Instrumentalness: {self.audio_features['instrumentalness']:.2f} (0-1)")
        self.code.append(f"// Liveness: {self.audio_features['liveness']:.2f} (0-1)")
        self.code.append(f"// Loudness: {self.audio_features['loudness']:.2f} dB")
        
        return "\n".join(self.code)
    
    def save_to_file(self, filename: str = None) -> str:
        """Save generated code to file"""
        if not filename:
            artist = self.track_info['artist'].replace(" ", "_").lower()
            track = self.track_info['name'].replace(" ", "_").lower()
            filename = f"{artist}_{track}.strudel"
        
        code = self.generate()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return filename
