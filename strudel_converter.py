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

# Strudel drum bank
DRUM_BANK = "RolandTR909"


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
    
    def _calculate_cpm(self, tempo: float) -> float:
        """Calculate cycles per minute from BPM"""
        # In Strudel, 1 cycle = 1 bar (typically 4 beats)
        # So CPM = BPM / 4
        return tempo / 4
    
    def _generate_kick_pattern(self) -> str:
        """Generate kick pattern based on energy"""
        energy = self.audio_features['energy']
        
        if energy > 0.7:
            # Energetic: steady kick
            return 's("bd*4").bank("RolandTR909").gain(0.85)'
        elif energy > 0.4:
            # Medium: kick with some variation
            return 's("bd*4, ~ bd").bank("RolandTR909").gain(0.85)'
        else:
            # Low energy: sparse kick
            return 's("bd ~ bd ~").bank("RolandTR909").gain(0.85)'
    
    def _generate_hihat_pattern(self) -> str:
        """Generate hi-hat pattern based on energy"""
        energy = self.audio_features['energy']
        danceability = self.audio_features['danceability']
        
        if energy > 0.7 and danceability > 0.7:
            # Very energetic and danceable
            return 's("hh*16").bank("RolandTR909").gain(0.4).hpf(6000)'
        elif energy > 0.5:
            # Moderate
            return 's("hh*8").bank("RolandTR909").gain(0.35).hpf(6000)'
        else:
            # Sparse
            return 's("hh*4").bank("RolandTR909").gain(0.3).hpf(6000)'
    
    def _generate_bass_pattern(self) -> str:
        """Generate bass pattern based on audio features"""
        root = self._get_note_name(self.audio_features['key'], octave=2)
        energy = self.audio_features['energy']
        
        # More energetic = faster bass pattern
        if energy > 0.7:
            # Fast repeating
            pattern = f'"{root} ~ {root} ~"'
        elif energy > 0.4:
            # Medium
            pattern = f'"{root} ~ ~ ~"'
        else:
            # Sparse
            pattern = f'"{root}"'
        
        return f'note({pattern}).s("sawtooth").lpf(350).decay(0.2).gain(0.55)'
    
    def _generate_chord_pattern(self) -> str:
        """Generate chord pattern based on key and mode"""
        key = self.audio_features['key']
        mode = self.audio_features['mode']
        root_note = self._get_note_name(key)
        mode_name = self._get_scale_name(mode)
        danceability = self.audio_features['danceability']
        
        # Generate chord intervals based on danceability
        if danceability > 0.7:
            # Very danceable: active chords
            chords = '"[0,2,4] [2,4,6]"'
        elif danceability > 0.4:
            # Moderately danceable
            chords = '"[0,2,4] ~ ~ [1,3,5]"'
        else:
            # Less danceable: simpler chords
            chords = '"[0,2,4] ~"'
        
        return f'note({chords}).scale("[{root_note}] {mode_name}").s("sawtooth").lpf(1200).lpq(2).attack(0.3).release(0.8).gain(0.3).room(0.4)'
    
    def _generate_melody_pattern(self) -> str:
        """Generate melody pattern based on valence and energy"""
        valence = self.audio_features['valence']
        energy = self.audio_features['energy']
        key = self.audio_features['key']
        root_note = self._get_note_name(key, octave=4)
        mode_name = self._get_scale_name(self.audio_features['mode'])
        
        # Happy/positive = higher notes, energetic = faster
        if valence > 0.6 and energy > 0.6:
            # Happy and energetic: active melody
            melody = '"0 2 4 5"'
        elif valence > 0.4:
            # Moderately happy
            melody = '"0 ~ 2 ~ 4"'
        else:
            # Sad or melancholic
            melody = '"0 ~ ~ ~"'
        
        return f'note({melody}).scale("[{root_note}] {mode_name}").s("triangle").decay(0.15).gain(0.25).delay(0.3).delaytime(0.1875).delayfeedback(0.4)'
    
    def generate(self) -> str:
        """Generate complete Strudel code"""
        self.code = []
        
        # Header comment
        self.code.append("// Generated Strudel code from Spotify")
        self.code.append(f"// Track: {self.track_info['name']} by {self.track_info['artist']}")
        self.code.append(f"// Tempo: {self.audio_features['tempo']} BPM")
        self.code.append(f"// Key: {self._get_note_name(self.audio_features['key'])} {self._get_scale_name(self.audio_features['mode'])}")
        self.code.append("")
        
        # Tempo setting - use setcpm (cycles per minute)
        cpm = self._calculate_cpm(self.audio_features['tempo'])
        self.code.append(f"setcpm({cpm:.1f}) // {self.audio_features['tempo']} BPM")
        self.code.append("")
        
        # Kick pattern
        self.code.append("// Kick drum")
        self.code.append(f"$: {self._generate_kick_pattern()}")
        self.code.append("")
        
        # Hi-hat pattern
        self.code.append("// Hi-hats")
        self.code.append(f"$: {self._generate_hihat_pattern()}")
        self.code.append("")
        
        # Bass pattern
        self.code.append("// Bass line")
        self.code.append(f"$: {self._generate_bass_pattern()}")
        self.code.append("")
        
        # Chord pattern
        self.code.append("// Chord progression")
        self.code.append(f"$: {self._generate_chord_pattern()}")
        self.code.append("")
        
        # Melody pattern
        self.code.append("// Melody")
        self.code.append(f"$: {self._generate_melody_pattern()}")
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
