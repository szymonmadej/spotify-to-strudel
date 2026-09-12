# Spotify to Strudel 🎵→🎼

Convert Spotify tracks to [Strudel](https://strudel.cycles/) music programming language code.

This tool analyzes audio features from Spotify (tempo, key, mood, energy, etc.) and generates Strudel code that captures the essence of the track through procedural patterns.

## Features

✨ **Automatic Music Generation**
- Analyzes Spotify track properties (tempo, key, mode, energy, etc.)
- Generates bass patterns based on energy levels
- Creates chord progressions from key and mode
- Builds melodies influenced by valence (positiveness) and energy
- Outputs ready-to-use Strudel code

🎵 **Audio Analysis**
- Extracts tempo, key, and time signature
- Analyzes energy, danceability, and mood
- Considers acousticness and instrumentation
- Includes all metrics in generated code comments

📝 **Flexible Output**
- Save to file with auto-generated names
- Print to stdout
- Full track metadata in comments

## Installation

### Prerequisites
- Python 3.7+
- Spotify Developer Account (free)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/szymonmadej/spotify-to-strudel.git
cd spotify-to-strudel
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Spotify API credentials**

   a. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   
   b. Create a new application and accept the terms
   
   c. Copy `Client ID` and `Client Secret`
   
   d. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```
   
   e. Add your credentials to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

## Usage

### Basic Usage - Get track ID

Find the Spotify track ID from the share URL:
```
https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
                                 ^^^^^^^^^^^^^^^^^^^
                                 This is the track ID
```

### Convert Track

```bash
python main.py 3n3Ppam7vgaVa1iaRUc9Lp
```

Or use the full URL:
```bash
python main.py "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
```

### Print Code to Terminal

```bash
python main.py 3n3Ppam7vgaVa1iaRUc9Lp --print
```

### Custom Output Filename

```bash
python main.py 3n3Ppam7vgaVa1iaRUc9Lp -o my_track.strudel
```

## Generated Code Example

The tool generates Strudel code with:
- **Bass Pattern**: Based on track energy
- **Chord Progression**: Following the track's key and mode
- **Melody**: Influenced by valence (happiness) and energy
- **Tempo**: Matched to the Spotify track tempo
- **Comments**: Full audio feature analysis

Example output structure:
```strudel
// Generated Strudel code from Spotify
// Track: Shape of You by Ed Sheeran
// Tempo: 96.0 BPM
// Key: g major

setcps(0.32)  // 96.0 BPM

bass = sound('sine')
  |> note("g . g:0.5 . g:0.5".fast(2))
  |> gain(0.3)

chords = sound('sine')
  |> scale("[g] major")
  |> note("[0,2,4] [1,3,5] [2,4,6] [1,3,5]".fast(1))
  |> gain(0.4)

melody = sound('sine')
  |> scale("[g] major")
  |> note("[0,4] [2,5] [4,7] [5,9]".fast(2))
  |> gain(0.3)

stack(
  bass,
  chords,
  melody
)

// Audio Features Analysis:
// Energy: 0.75 (0-1)
// Danceability: 0.81 (0-1)
// Valence: 0.67 (0-1, happiness)
// ... more features
```

## Audio Features Explained

The generated code uses these Spotify audio features:

| Feature | Range | Meaning |
|---------|-------|---------|
| **Energy** | 0-1 | Intensity and activity (fast = high energy) |
| **Danceability** | 0-1 | How suitable for dancing |
| **Valence** | 0-1 | Musical positiveness (happy/cheerful) |
| **Acousticness** | 0-1 | Likelihood of being acoustic |
| **Instrumentalness** | 0-1 | Lack of vocals |
| **Liveness** | 0-1 | Presence of audience/live performance |
| **Loudness** | dB | Overall loudness |

## How It Works

1. **Connects to Spotify API** with your credentials
2. **Fetches track metadata** (name, artist, duration, etc.)
3. **Analyzes audio features** (tempo, key, energy, mood)
4. **Maps features to Strudel patterns**:
   - Tempo → `setcps()` timing
   - Key + Mode → Musical scale
   - Energy → Bass pattern complexity
   - Danceability → Chord rhythm
   - Valence → Melody intervals
5. **Generates executable Strudel code**
6. **Saves to file** or prints to terminal

## Project Structure

```
spotify-to-strudel/
├── main.py                 # Main entry point
├── spotify_handler.py      # Spotify API integration
├── strudel_converter.py    # Audio feature to Strudel conversion
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Customization

You can modify the conversion logic in `strudel_converter.py`:

- **Bass Pattern**: Edit `_generate_bass_pattern()`
- **Chord Progression**: Edit `_generate_chord_pattern()`
- **Melody**: Edit `_generate_melody_pattern()`
- **Tempo Scaling**: Modify `setcps()` calculation
- **Instrument Selection**: Change `sound()` parameters

## Troubleshooting

### "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set"
- Check if `.env` file exists in the project root
- Verify credentials are correct in [Spotify Dashboard](https://developer.spotify.com/dashboard)
- Make sure `.env` is not in `.gitignore` accidentally

### "Invalid Spotify URL"
- Use full URL: `https://open.spotify.com/track/...`
- Or use just the track ID: `3n3Ppam7vgaVa1iaRUc9Lp`

### "Could not fetch track information"
- Check your internet connection
- Verify the track ID/URL is correct
- Check if track exists on Spotify

## License

MIT

## Contributing

Contributions welcome! Feel free to:
- Improve the Strudel code generation
- Add more audio feature analysis
- Optimize patterns
- Fix bugs

## Resources

- [Strudel Documentation](https://strudel.cycles/)
- [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api/)
- [Spotipy Library](https://spotipy.readthedocs.io/)

---

Happy music hacking! 🎼✨
