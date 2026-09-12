#!/usr/bin/env python3
"""
Spotify to Strudel - Convert Spotify tracks to Strudel music programming language
"""

import sys
import argparse
from spotify_handler import SpotifyHandler
from strudel_converter import StrudelConverter


def main():
    parser = argparse.ArgumentParser(
        description='Convert Spotify tracks to Strudel music code'
    )
    
    parser.add_argument(
        'track_id',
        help='Spotify track ID or URL'
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
    
    args = parser.parse_args()
    
    try:
        # Initialize Spotify handler
        print("🎵 Connecting to Spotify API...")
        spotify = SpotifyHandler()
        
        # Get track ID from URL if needed
        track_id = args.track_id
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
        
        # Fetch audio features
        print(f"📊 Analyzing audio features...")
        audio_features = spotify.get_audio_features(track_id)
        if not audio_features:
            print("❌ Could not fetch audio features")
            return 1
        
        print(f"✅ Tempo: {audio_features['tempo']} BPM")
        print(f"✅ Key: {audio_features['key']}")
        
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
        print("\nPlease set up your .env file with Spotify API credentials:")
        print("  1. Create .env file from .env.example")
        print("  2. Get credentials from https://developer.spotify.com/dashboard")
        print("  3. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
