'''
🌙 Moon Dev's Token Scanner - Built with love by Moon Dev 🚀
Watches for new Solana token launches and displays them with fun animations!
'''

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

import time
import random
import requests
from termcolor import colored
import pandas as pd
from pathlib import Path
import logging
from rich.console import Console
from rich import print as rprint
from playsound import playsound

# Suppress INFO logs
logging.getLogger().setLevel(logging.WARNING)

# Initialize Rich console
console = Console()

# Constants
PAST_TOKENS_TO_SHOW = 20  # Number of past token launches to display
CHECK_INTERVAL = 10  # Seconds between each check for new launches
DISPLAY_DELAY = 0.5  # Seconds between displaying each token
ANIMATION_DURATION = 10  # Seconds to show attention-grabbing animation
EXCLUDE_PATTERNS = ['So11111111111111111111111111111111111111112']  # Exclude the SOLE token pattern
BASE_URL = "http://api.moondev.com:8000"
SOUND_ENABLED = True  # Set to True to enable sound effects, False to disable them

# Animation sequences
ATTENTION_EMOJIS = [
    "🚨", "💫", "⚡", "🔥", "✨", "💥",  # Attention-grabbing
    "🎯", "🎪", "🎢", "🎡", "🎠",       # Fun & festive
    "🌈", "🦄", "🌟", "💎", "🚀"        # Moon Dev specials
]

# Background colors for token announcements
BACKGROUND_COLORS = [
    'on_blue', 'on_magenta', 'on_cyan', 'on_red', 'on_green', 
    'on_yellow', 'on_grey', 'on_white'
]

LAUNCH_EMOJIS = [
    "🚀", "💎", "🌙", "⭐", "🔥", "💫", "✨", "🌟", "💰", "🎯",  # Classic crypto
    "🎆", "🌠", "⚡", "🌈", "🎨", "🎪", "🎭", "🎡", "🎢", "🎠",  # Fun & festive
    "🦁", "🐉", "🦊", "🦄", "🐋", "🦈", "🦅", "🦚", "🦜", "🦋",  # Cool animals
    "🏆", "🎮", "🎲", "🎱", "🎳", "🎪", "🎨", "🎭", "🎪", "🎢",  # Games & fun
    "🌍", "🌎", "🌏", "🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓",  # Space & moon phases
    "💥", "🌪️", "⚡", "☄️", "🌠", "🎇", "🎆", "✨", "💫", "⭐",  # Energy & explosions
]

# Sound effects paths
SOUND_EFFECTS = [
    "/Users/md/Dropbox/dev/github/Untitled/sounds/pownew.MP3",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/Shining.wav",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/final_fant1.MP3",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/final_fant2.MP3"
]

class TokenScanner:
    def __init__(self):
        """🌙 Moon Dev's Token Scanner - Built with love by Moon Dev 🚀"""
        self.base_dir = Path(__file__).parent / "api_data"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.seen_tokens = set()
        self.last_check_time = None
        self.sound_enabled = SOUND_ENABLED
        
        # Only check sound files if sound is enabled
        if self.sound_enabled:
            for sound_file in SOUND_EFFECTS:
                if not os.path.exists(sound_file):
                    print(f"⚠️ Warning: Sound file not found: {sound_file}")
                    self.sound_enabled = False
                    break
                    
    def attention_animation(self):
        """Run an attention-grabbing animation"""
        start_time = time.time()
        position = 0
        direction = 1
        width = 40  # Animation width
        
        try:
            # Start on current line
            while time.time() - start_time < ANIMATION_DURATION:
                # Create animation frame
                emojis = random.sample(ATTENTION_EMOJIS, 3)  # Pick 3 random emojis
                spaces = ' ' * position
                color = random.choice(BACKGROUND_COLORS)
                
                # Print the animation frame with random colors
                print(f'\r{spaces}{colored("".join(emojis), "white", color)}' + ' ' * (width - position), end='', flush=True)
                
                # Update position for bouncing effect
                position += direction
                if position >= width or position <= 0:
                    direction *= -1
                
                time.sleep(0.1)
            
            # Clear the animation line completely
            print('\r' + ' ' * (width + 20), end='\r', flush=True)
            
        except KeyboardInterrupt:
            # Clear line if interrupted
            print('\r' + ' ' * (width + 20), end='\r', flush=True)
            
    def get_token_addresses(self):
        """Fetch token data silently"""
        try:
            url = f'{BASE_URL}/files/new_token_addresses.csv'
            response = requests.get(url)
            response.raise_for_status()
            
            # Save to cache
            save_path = self.base_dir / "new_token_addresses.csv"
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return pd.read_csv(save_path)
                
        except Exception:
            return None
        
    def filter_tokens(self, df):
        """Filter out unwanted tokens and sort by timestamp"""
        if df is None or df.empty:
            return pd.DataFrame()
            
        # Filter out tokens containing excluded patterns
        for pattern in EXCLUDE_PATTERNS:
            df = df[~df['Token Address'].str.contains(pattern, case=True)]
            
        # Sort by time found, oldest first
        return df.sort_values('Epoch Time', ascending=True)
        
    def display_past_token(self, address, time_found, birdeye_link):
        """Display a past token without animation"""
        try:
            time_obj = pd.to_datetime(time_found)
            time_str = time_obj.strftime("%m-%d %H:%M")
        except:
            time_str = time_found
            
        random_emoji = random.choice(LAUNCH_EMOJIS)
        random_bg = random.choice(BACKGROUND_COLORS)
            
        print(f"\n{colored(f'{random_emoji} NEW TOKEN FOUND', 'white', random_bg)} {time_str}")
        print(f"{birdeye_link}")
        time.sleep(DISPLAY_DELAY)
        
    def show_past_tokens(self):
        """Display past token launches"""
        df = self.get_token_addresses()
        df = self.filter_tokens(df)
        
        if df.empty:
            return
            
        # Get the most recent tokens (from the end since we're sorted ascending)
        recent_tokens = df.tail(PAST_TOKENS_TO_SHOW)
        
        # Store seen tokens and last check time
        self.seen_tokens = set(recent_tokens['Token Address'])
        self.last_check_time = pd.to_datetime(recent_tokens.iloc[-1]['Time Found'])
        
        print("\n🔍 Recent Token Launches:")
        for _, row in recent_tokens.iterrows():
            self.display_past_token(
                row['Token Address'],
                row['Time Found'],
                row['Birdeye Link']
            )
            
    def play_sound(self):
        """Play a random sound effect safely"""
        if not self.sound_enabled:
            return
            
        try:
            sound_file = random.choice(SOUND_EFFECTS)
            playsound(sound_file, block=False)
        except Exception:
            pass
            
    def display_token(self, address, time_found, birdeye_link, count=None):
        """Display a new token with animation"""
        try:
            time_obj = pd.to_datetime(time_found)
            time_str = time_obj.strftime("%m-%d %H:%M")
        except:
            time_str = time_found
            
        random_emoji = random.choice(LAUNCH_EMOJIS)
        random_bg = random.choice(BACKGROUND_COLORS)
            
        print(f"\n{colored(f'{random_emoji} NEW TOKEN FOUND', 'white', random_bg)} {time_str}")
        print(f"{birdeye_link}")
        
        # Play sound first, then do animation
        self.play_sound()
        self.attention_animation()
        
    def monitor_new_launches(self):
        """Monitor for new token launches silently"""
        while True:
            try:
                df = self.get_token_addresses()
                if df is None:
                    time.sleep(CHECK_INTERVAL)
                    continue
                    
                df = self.filter_tokens(df)
                
                if df.empty:
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Get the newest token's time
                current_time = pd.to_datetime(df.iloc[-1]['Time Found'])
                
                if self.last_check_time and current_time > self.last_check_time:
                    # Get only tokens newer than our last check
                    new_df = df[pd.to_datetime(df['Time Found']) > self.last_check_time]
                    new_tokens = set(new_df['Token Address']) - self.seen_tokens
                    
                    if new_tokens:
                        # Display new tokens in chronological order
                        for _, row in new_df[new_df['Token Address'].isin(new_tokens)].iterrows():
                            try:
                                self.display_token(
                                    row['Token Address'],
                                    row['Time Found'],
                                    row['Birdeye Link']
                                )
                                self.seen_tokens.add(row['Token Address'])
                            except Exception:
                                pass
                        
                        self.last_check_time = current_time
                
            except Exception:
                pass
                
            time.sleep(CHECK_INTERVAL)

def main():
    """Main entry point"""
    scanner = TokenScanner()
    scanner.show_past_tokens()
    scanner.monitor_new_launches()

if __name__ == "__main__":
    main() 