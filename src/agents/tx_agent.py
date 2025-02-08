'''
doesnt work yet

🌙 Moon Dev's Transaction Scanner - Built with love by Moon Dev 🚀
Watches for new Solana transactions and displays them with fun animations!
'''

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

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
from agents.api import MoonDevAPI  # Import our API handler

# Load environment variables for API key
load_dotenv()

# Suppress INFO logs
logging.getLogger().setLevel(logging.WARNING)

# Initialize Rich console
console = Console()

# Constants
PAST_TRANSACTIONS_TO_SHOW = 20  # Number of past transactions to display
CHECK_INTERVAL = 10  # Seconds between each check
DISPLAY_DELAY = 0.5  # Seconds between displaying each transaction
ANIMATION_DURATION = 10  # Seconds to show attention-grabbing animation
BASE_URL = "http://api.moondev.com:8000"
SOUND_ENABLED = True  # Set to True to enable sound effects, False to disable them

# Animation sequences
ATTENTION_EMOJIS = [
    "🚨", "💫", "⚡", "🔥", "✨", "💥",  # Attention-grabbing
    "🎯", "🎪", "🎢", "🎡", "🎠",       # Fun & festive
    "🌈", "🦄", "🌟", "💎", "🚀"        # Moon Dev specials
]

# Background colors for transaction announcements
BACKGROUND_COLORS = [
    'on_blue', 'on_magenta', 'on_cyan', 'on_red', 'on_green', 
    'on_yellow', 'on_grey', 'on_white'
]

TRANSACTION_EMOJIS = [
    "💰", "💎", "🌙", "⭐", "🔥", "💫", "✨", "🌟", "💸", "🎯",  # Money & crypto
    "🏦", "🏧", "💱", "💲", "🤑", "💹", "📈", "🏆", "🎮", "🎲",  # Finance & fun
    "🦁", "🐉", "🦊", "🦄", "🐋", "🦈", "🦅", "🦚", "🦜", "🦋",  # Cool animals
    "🌍", "🌎", "🌏", "🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓",  # Space theme
]

# Sound effects paths
SOUND_EFFECTS = [
    "/Users/md/Dropbox/dev/github/Untitled/sounds/pownew.MP3",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/Shining.wav",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/final_fant1.MP3",
    "/Users/md/Dropbox/dev/github/Untitled/sounds/final_fant2.MP3"
]

class TxScanner:
    def __init__(self):
        """🌙 Moon Dev's Transaction Scanner - Built with love by Moon Dev 🚀"""
        self.base_dir = Path(__file__).parent / "api_data"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.seen_transactions = set()
        self.last_check_time = None
        self.sound_enabled = SOUND_ENABLED
        self.api = MoonDevAPI()  # Initialize our API handler
        
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
            
    def get_recent_transactions(self):
        """Fetch recent transactions data silently"""
        try:
            # Use our API handler instead of direct requests
            return self.api.get_copybot_recent_transactions()
        except Exception as e:
            print(f"💥 Error fetching transactions: {str(e)}")
            return None
            
    def display_past_transaction(self, row):
        """Display a past transaction without animation"""
        try:
            time_obj = pd.to_datetime(row['blockTime'], unit='s')
            time_str = time_obj.strftime("%m-%d %H:%M")
        except:
            time_str = "Unknown Time"
            
        random_emoji = random.choice(TRANSACTION_EMOJIS)
        random_bg = random.choice(BACKGROUND_COLORS)
        
        # Format amounts nicely
        bought_amount = f"{float(row['bought_amount']):,.2f}" if row['bought_amount'] else "0"
        sold_amount = f"{float(row['sold_amount']):,.2f}" if row['sold_amount'] else "0"
        
        print(f"\n{colored(f'{random_emoji} NEW TRANSACTION', 'white', random_bg)} {time_str}")
        print(f"👤 Wallet: {row['owner']}")
        print(f"💰 Bought: {bought_amount} {row['token_bought']}")
        print(f"💸 Sold: {sold_amount} {row['token_sold']}")
        print(f"🔍 {row['birdeye_link']}")
        time.sleep(DISPLAY_DELAY)
        
    def show_past_transactions(self):
        """Display past transactions"""
        df = self.get_recent_transactions()
        if df is None or df.empty:
            return
            
        # Get the most recent transactions
        recent_txs = df.tail(PAST_TRANSACTIONS_TO_SHOW)
        
        # Store seen transactions and last check time
        self.seen_transactions = set(recent_txs['contract_address'])
        self.last_check_time = pd.to_datetime(recent_txs.iloc[-1]['blockTime'], unit='s')
        
        print("\n🔍 Recent Transactions:")
        for _, row in recent_txs.iterrows():
            self.display_past_transaction(row)
            
    def play_sound(self):
        """Play a random sound effect safely"""
        if not self.sound_enabled:
            return
            
        try:
            sound_file = random.choice(SOUND_EFFECTS)
            playsound(sound_file, block=False)
        except Exception:
            pass
            
    def display_transaction(self, row):
        """Display a new transaction with animation"""
        try:
            time_obj = pd.to_datetime(row['blockTime'], unit='s')
            time_str = time_obj.strftime("%m-%d %H:%M")
        except:
            time_str = "Unknown Time"
            
        random_emoji = random.choice(TRANSACTION_EMOJIS)
        random_bg = random.choice(BACKGROUND_COLORS)
        
        # Format amounts nicely
        bought_amount = f"{float(row['bought_amount']):,.2f}" if row['bought_amount'] else "0"
        sold_amount = f"{float(row['sold_amount']):,.2f}" if row['sold_amount'] else "0"
        
        print(f"\n{colored(f'{random_emoji} NEW TRANSACTION', 'white', random_bg)} {time_str}")
        print(f"👤 Wallet: {row['owner']}")
        print(f"💰 Bought: {bought_amount} {row['token_bought']}")
        print(f"💸 Sold: {sold_amount} {row['token_sold']}")
        print(f"🔍 {row['birdeye_link']}")
        
        # Play sound first, then do animation
        self.play_sound()
        self.attention_animation()
        
    def monitor_transactions(self):
        """Monitor for new transactions silently"""
        while True:
            try:
                df = self.get_recent_transactions()
                if df is None or df.empty:
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Get the newest transaction's time
                current_time = pd.to_datetime(df.iloc[-1]['blockTime'], unit='s')
                
                if self.last_check_time and current_time > self.last_check_time:
                    # Get only transactions newer than our last check
                    new_df = df[pd.to_datetime(df['blockTime'], unit='s') > self.last_check_time]
                    new_txs = set(new_df['contract_address']) - self.seen_transactions
                    
                    if new_txs:
                        # Display new transactions in chronological order
                        for _, row in new_df[new_df['contract_address'].isin(new_txs)].iterrows():
                            try:
                                self.display_transaction(row)
                                self.seen_transactions.add(row['contract_address'])
                            except Exception:
                                pass
                        
                        self.last_check_time = current_time
                
            except Exception:
                pass
                
            time.sleep(CHECK_INTERVAL)

def main():
    """Main entry point"""
    scanner = TxScanner()
    scanner.show_past_transactions()
    scanner.monitor_transactions()

if __name__ == "__main__":
    main() 