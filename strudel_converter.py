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
    
    def _get_scale_name(self, mode: int) -> str:
        """Get scale name from mode"""
        return MODE_NAMES.get(mode, 'major')
    
    def _calculate_cps(self, tempo: float) -> float:
        """Calculate cycles per second from BPM"""
        # BPM to cycles per second
        # At 120 BPM and 4/4 time: 1 cycle = 1 bar = 4 beats
        return tempo / 120 / 4
    
    def _generate_bass_pattern(self) -> str:
        """Generate a bass pattern based on audio features"""
        root = self._get_note_name(self.audio_features['key'], octave=1)
        energy = self.audio_features['energy']
        
        # More energetic = faster bass pattern
        if energy > 0.7:
            # Energetic: fast, repeated notes
            pattern = f'"{root}2 ~ {root}4 ~ {root}4"'
        elif energy > 0.4:
            # Medium: moderate pattern
            pattern = f'"{root}2 ~ ~ {root}4"'
        else:
            # Low energy: sparse pattern
            pattern = f'"{root} ~ ~ ~"'
        
        return f"bass = s('sine').note({pattern}).gain(0.3)"
    
    def _generate_chord_pattern(self) -> str:
        """Generate chord pattern based on key and mode"""
        key = self.audio_features['key']
        mode = self.audio_features['mode']
        root_note = self._get_note_name(key)
        mode_name = self._get_scale_name(mode)
        danceability = self.audio_features['danceability']
        
        # Generate chord intervals based on danceability
        if danceability > 0.7:
            # Very danceable: complex chords
            chords = '"[0,2,4]2 [2,4,6]2 [4,6,8]2 [2,4,6]2"'
        elif danceability > 0.4:
            # Moderately danceable
            chords = '"[0,2,4]2 ~ ~ [2,4,6]2"'
        else:
            # Less danceable: simpler chords
            chords = '"[0,2,4]2 ~ ~ ~"'
        
        return f"chords = s('sine').scale('[{root_note}] {mode_name}').note({chords}).gain(0.4)"
    
    def _generate_melody_pattern(self) -> str:
        """Generate melody pattern based on valence and energy"""
        valence = self.audio_features['valence']
        energy = self.audio_features['energy']
        key = self.audio_features['key']
        root_note = self._get_note_name(key)
        mode_name = self._get_scale_name(self.audio_features['mode'])
        
        # Happy/positive = higher notes, energetic = faster
        if valence > 0.6 and energy > 0.6:
            # Happy and energetic: fast, high notes
            melody = '"[0,4]4 [2,5]4 [4,7]4 [5,9]4"'
        elif valence > 0.4:
            # Moderately happy
            melody = '"0 2 4 5 4 2"'
        else:
            # Sad or melancholic: slower, lower
            melody = '"0 ~ 2 ~ 4 ~"'
        
        return f"melody = s('sine').scale('[{root_note}] {mode_name}').note({melody}).gain(0.3)"
    
    def generate(self) -> str:
        """Generate complete Strudel code"""
        self.code = []
        
        # Header comment
        self.code.append("// Generated Strudel code from Spotify")
        self.code.append(f"// Track: {self.track_info['name']} by {self.track_info['artist']}")
        self.code.append(f"// Tempo: {self.audio_features['tempo']} BPM")
        self.code.append(f"// Key: {self._get_note_name(self.audio_features['key'])} {self._get_scale_name(self.audio_features['mode'])}")
        self.code.append("")
        
        # Tempo setting
        cps = self._calculate_cps(self.audio_features['tempo'])
        self.code.append(f"setcps({cps:.4f}) // {self.audio_features['tempo']} BPM")
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
        self.code.append("stack(bass, chords, melody)")
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
