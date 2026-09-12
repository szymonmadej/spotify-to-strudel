#!/usr/bin/env python3
"""
Spotify to Strudel - Convert Spotify tracks to Strudel music programming language
Uses audio analysis from preview MP3 or Last.fm API for audio features
"""

import sys
import argparse
from spotify_handler import SpotifyHandler
from lastfm_handler import LastFMHandler
from audio_analyzer import AudioAnalyzer
from strudel_converter import StrudelConverter


def main():
    parser = argparse.ArgumentParser(
        description='Convert Spotify tracks to Strudel music code'
    )
    
    parser.add_argument(
        'track_id',
        help='Spotify track ID/URL or Last.fm URL'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output filename (default: artist_track.strudel)',
        default=None
    )
    parser.add_argument(
        '--print',
        action='store_true',
        help='Print generated code to stdout'
    )
    parser.add_argument(
        '--skip-audio',
        action='store_true',
        help='Skip audio analysis, use metadata only'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine if input is Last.fm or Spotify URL
        input_url = args.track_id
        is_lastfm = 'last.fm' in input_url.lower()
        
        # ==================== LAST.FM FLOW ====================
        if is_lastfm:
            print("🎵 Using Last.fm data source...")
            lastfm = LastFMHandler()
            
            # Parse Last.fm URL
            print("📎 Parsing Last.fm URL...")
            parsed = lastfm.parse_lastfm_url(input_url)
            if not parsed:
                print("❌ Invalid Last.fm URL")
                return 1
            
            artist, track = parsed
            print(f"🔍 Found: {track} by {artist}")
            
            # Get track tags from Last.fm
            print("📊 Analyzing audio features from Last.fm...")
            tags = lastfm.get_track_tags(artist, track)
            
            if tags:
                print(f"✅ Found genres: {', '.join(tags)}")
            else:
                print("⚠️  No genres found on Last.fm, using defaults")
            
            # Infer audio features from tags
            audio_features = lastfm.infer_audio_features_from_tags(tags)
            
            # Create track info dict for converter
            track_info = {
                'name': track,
                'artist': artist,
                'duration_ms': 0,
                'popularity': 0,
                'external_urls': {}
            }
            
            print(f"✅ Tempo: {audio_features['tempo']} BPM")
            print(f"✅ Energy: {audio_features['energy']:.2f}")
        
        # ==================== SPOTIFY FLOW ====================
        else:
            print("🎵 Using Spotify data source...")
            
            # Initialize Spotify handler
            print("🎵 Connecting to Spotify API...")
            spotify = SpotifyHandler()
            
            # Get track ID from URL if needed
            track_id = input_url
            if track_id.startswith('http'):
                print("📎 Parsing Spotify URL...")
                track_id = spotify.get_track_by_url(track_id)
                if not track_id:
                    print("❌ Invalid Spotify URL")
                    return 1
            
            # Fetch track info
            print(f"🔍 Fetching track information...")
            track_info = spotify.get_track_info(track_id)
            if not track_info:
                print("❌ Could not fetch track information")
                return 1
            
            print(f"✅ Found: {track_info['name']} by {track_info['artist']}")
            
            # Try to analyze from audio preview first
            audio_features = None
            if track_info.get('preview_url') and not args.skip_audio:
                print(f"📥 Downloading audio preview...")
                analyzer = AudioAnalyzer()
                analyzed_features = analyzer.download_and_analyze(track_info['preview_url'])
                
                if analyzed_features:
                    print(f"✅ Audio analysis complete!")
                    print(f"   Tempo: {analyzed_features['tempo']:.0f} BPM")
                    print(f"   Energy: {analyzed_features['energy']:.2f}")
                    print(f"   Brightness: {analyzed_features['brightness']:.2f}")
                    print(f"   Danceability: {analyzed_features['danceability']:.2f}")
                    print(f"   Valence: {analyzed_features['valence']:.2f}")
                    audio_features = analyzed_features
                else:
                    print("⚠️  Audio analysis failed, trying Spotify features...")
            
            # Fallback to Spotify audio-features if audio analysis failed
            if not audio_features:
                print(f"📊 Fetching Spotify audio features...")
                spotify_features = spotify.get_audio_features(track_id)
                
                if spotify_features:
                    print(f"✅ Spotify features available")
                    print(f"   Tempo: {spotify_features['tempo']} BPM")
                    print(f"   Energy: {spotify_features['energy']:.2f}")
                    audio_features = spotify_features
                else:
                    # Use Last.fm as final fallback
                    print("⚠️  Spotify features unavailable, using Last.fm analysis...")
                    try:
                        lastfm = LastFMHandler()
                        tags = lastfm.get_track_tags(track_info['artist'], track_info['name'])
                        
                        if tags:
                            print(f"✅ Found genres from Last.fm: {', '.join(tags[:3])}")
                            audio_features = lastfm.infer_audio_features_from_tags(tags)
                        else:
                            print("⚠️  No tags found on Last.fm, using defaults")
                            audio_features = lastfm.infer_audio_features_from_tags([])
                        
                    except ValueError as e:
                        print(f"⚠️  Last.fm error: {e}")
                        print("⚠️  Using default audio features")
                        audio_features = {
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
                    except Exception as e:
                        print(f"⚠️  Error connecting to Last.fm: {e}")
                        print("⚠️  Using default audio features")
                        audio_features = {
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
        
        # ==================== COMMON FLOW ====================
        # Convert to Strudel
        print(f"🎼 Generating Strudel code...")
        converter = StrudelConverter(track_info, audio_features)
        
        # Save to file
        output_file = converter.save_to_file(args.output)
        print(f"✅ Code saved to: {output_file}")
        
        # Print if requested
        if args.print:
            print("\n" + "="*60)
            print("GENERATED STRUDEL CODE:")
            print("="*60 + "\n")
            print(converter.generate())
            print("\n" + "="*60 + "\n")
        
        return 0
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with required API credentials:")
        print("  1. Create .env file from .env.example")
        print("  2. Get Spotify credentials from https://developer.spotify.com/dashboard")
        print("  3. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        print("  4. Get Last.fm API key from https://www.last.fm/api/account/create")
        print("  5. Add LASTFM_API_KEY to .env")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
