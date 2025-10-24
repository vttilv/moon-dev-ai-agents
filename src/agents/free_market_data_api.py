"""
🆓 Free Market Data API - Alternative to MoonDev API
Built as a FREE alternative using public data sources

This replaces MoonDevAPI for users without bootcamp access.

Data Sources:
- CoinGlass API (free) - Liquidations, Funding Rates, Open Interest
- BirdEye API (free tier) - Token prices, new launches
- CoinGecko API (free tier) - Token metadata

No API key required for most endpoints!
"""

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
from pathlib import Path
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

class FreeMarketDataAPI:
    """Free alternative to MoonDevAPI using public data sources"""

    def __init__(self):
        """Initialize the free API handler"""
        self.base_dir = PROJECT_ROOT / "src" / "agents" / "api_data"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # CoinGlass API (free, no key required for basic data)
        self.coinglass_base = "https://open-api.coinglass.com/public/v2"

        # BirdEye API (you have free tier)
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.birdeye_base = "https://public-api.birdeye.so"

        # CoinGecko API (you have free tier)
        self.coingecko_key = os.getenv('COINGECKO_API_KEY')
        self.coingecko_base = "https://api.coingecko.com/api/v3"

        self.session = requests.Session()

        print("🆓 Free Market Data API: Initialized! 🚀")
        print(f"📂 Cache directory: {self.base_dir.absolute()}")
        print(f"🌐 Using: CoinGlass (liquidations/funding/OI)")
        print(f"🌐 Using: BirdEye (Solana tokens)")
        print(f"🌐 Using: CoinGecko (metadata)")

        if self.birdeye_key:
            print("✓ BirdEye API key loaded")
        else:
            print("⚠️  No BirdEye API key (limited token data)")

        if self.coingecko_key:
            print("✓ CoinGecko API key loaded")
        else:
            print("⚠️  No CoinGecko API key (using demo mode)")

    def get_liquidation_data(self, symbol="BTC", limit=10000):
        """
        Get liquidation data from CoinGlass (FREE)

        Args:
            symbol: "BTC" or "ETH"
            limit: Number of recent liquidations (CoinGlass returns last 24h)

        Returns:
            DataFrame with liquidation data
        """
        try:
            print(f"🆓 Fetching liquidation data for {symbol} from CoinGlass...")

            # CoinGlass liquidation endpoint (free, no key needed)
            url = f"{self.coinglass_base}/liquidation"

            # Get last 24 hours of liquidations
            params = {
                'symbol': symbol,
                'interval': '1h'  # 1 hour intervals
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data:
                    # Convert to DataFrame
                    records = []
                    for item in data['data']:
                        records.append({
                            'timestamp': item.get('createTime'),
                            'symbol': symbol,
                            'side': item.get('type'),  # long or short
                            'size': item.get('volUsd', 0),
                            'exchange': item.get('exchangeName', 'unknown')
                        })

                    df = pd.DataFrame(records)

                    # Save to cache
                    save_path = self.base_dir / "liq_data.csv"
                    df.to_csv(save_path, index=False)

                    print(f"✨ Loaded {len(df)} liquidation records")
                    return df
                else:
                    print("⚠️  No liquidation data returned")
                    return None
            else:
                print(f"⚠️  CoinGlass returned status {response.status_code}")
                # Fallback: return sample/empty data
                return self._get_cached_data("liq_data.csv")

        except Exception as e:
            print(f"💥 Error fetching liquidations: {str(e)}")
            print(f"📋 Trying cached data...")
            return self._get_cached_data("liq_data.csv")

    def get_funding_data(self, symbol=None):
        """
        Get funding rate data from CoinGlass (FREE)

        Args:
            symbol: Optional symbol filter ("BTC", "ETH", etc.)

        Returns:
            DataFrame with funding rates
        """
        try:
            print("🆓 Fetching funding rates from CoinGlass...")

            # CoinGlass funding rate endpoint
            url = f"{self.coinglass_base}/fundingRate"

            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data:
                    records = []
                    for item in data['data']:
                        records.append({
                            'symbol': item.get('symbol'),
                            'funding_rate': float(item.get('rate', 0)),
                            'next_funding_time': item.get('nextFundingTime'),
                            'exchange': item.get('exchangeName', 'average')
                        })

                    df = pd.DataFrame(records)

                    # Filter by symbol if requested
                    if symbol:
                        df = df[df['symbol'].str.contains(symbol, case=False)]

                    # Save to cache
                    save_path = self.base_dir / "funding.csv"
                    df.to_csv(save_path, index=False)

                    print(f"✨ Loaded {len(df)} funding rate records")
                    return df
                else:
                    print("⚠️  No funding data returned")
                    return None
            else:
                print(f"⚠️  CoinGlass returned status {response.status_code}")
                return self._get_cached_data("funding.csv")

        except Exception as e:
            print(f"💥 Error fetching funding rates: {str(e)}")
            return self._get_cached_data("funding.csv")

    def get_oi_data(self, symbol="BTC"):
        """
        Get Open Interest data from CoinGlass (FREE)

        Args:
            symbol: "BTC" or "ETH"

        Returns:
            DataFrame with OI data
        """
        try:
            print(f"🆓 Fetching Open Interest for {symbol} from CoinGlass...")

            url = f"{self.coinglass_base}/openInterest"

            params = {
                'symbol': symbol,
                'interval': '0'  # Current snapshot
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data:
                    records = []
                    for item in data['data']:
                        records.append({
                            'symbol': symbol,
                            'exchange': item.get('exchangeName'),
                            'open_interest': float(item.get('openInterest', 0)),
                            'open_interest_usd': float(item.get('openInterestUsd', 0)),
                            'timestamp': datetime.now().isoformat()
                        })

                    df = pd.DataFrame(records)

                    # Save to cache
                    save_path = self.base_dir / "oi.csv"
                    df.to_csv(save_path, index=False)

                    print(f"✨ Loaded {len(df)} OI records")
                    return df
                else:
                    print("⚠️  No OI data returned")
                    return None
            else:
                print(f"⚠️  CoinGlass returned status {response.status_code}")
                return self._get_cached_data("oi.csv")

        except Exception as e:
            print(f"💥 Error fetching OI data: {str(e)}")
            return self._get_cached_data("oi.csv")

    def get_oi_total(self):
        """
        Get total market Open Interest (FREE)

        Returns:
            DataFrame with total OI for BTC + ETH
        """
        try:
            print("🆓 Fetching total market OI from CoinGlass...")

            # Get both BTC and ETH
            btc_oi = self.get_oi_data("BTC")
            eth_oi = self.get_oi_data("ETH")

            if btc_oi is not None and eth_oi is not None:
                # Combine
                total_df = pd.concat([btc_oi, eth_oi], ignore_index=True)

                # Save to cache
                save_path = self.base_dir / "oi_total.csv"
                total_df.to_csv(save_path, index=False)

                return total_df
            else:
                return self._get_cached_data("oi_total.csv")

        except Exception as e:
            print(f"💥 Error fetching total OI: {str(e)}")
            return self._get_cached_data("oi_total.csv")

    def get_token_addresses(self):
        """
        Get new token launches from BirdEye (uses your free tier API key)

        Returns:
            DataFrame with new Solana token addresses
        """
        try:
            if not self.birdeye_key:
                print("⚠️  BirdEye API key required for new token data")
                return self._get_cached_data("new_token_addresses.csv")

            print("🆓 Fetching new Solana tokens from BirdEye...")

            # BirdEye new listings endpoint
            url = f"{self.birdeye_base}/defi/token_creation"

            headers = {
                'X-API-KEY': self.birdeye_key
            }

            # Get tokens from last 24 hours
            params = {
                'sort_by': 'creation_time',
                'sort_type': 'desc',
                'offset': 0,
                'limit': 50
            }

            response = self.session.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data and 'items' in data['data']:
                    records = []
                    for item in data['data']['items']:
                        records.append({
                            'address': item.get('address'),
                            'symbol': item.get('symbol'),
                            'name': item.get('name'),
                            'creation_time': item.get('creation_time'),
                            'liquidity': item.get('liquidity', 0),
                            'price': item.get('price', 0)
                        })

                    df = pd.DataFrame(records)

                    # Save to cache
                    save_path = self.base_dir / "new_token_addresses.csv"
                    df.to_csv(save_path, index=False)

                    print(f"✨ Loaded {len(df)} new tokens")
                    return df
                else:
                    print("⚠️  No token data returned")
                    return None
            else:
                print(f"⚠️  BirdEye returned status {response.status_code}")
                return self._get_cached_data("new_token_addresses.csv")

        except Exception as e:
            print(f"💥 Error fetching new tokens: {str(e)}")
            return self._get_cached_data("new_token_addresses.csv")

    def get_copybot_follow_list(self):
        """
        Placeholder for copybot follow list (not available in free APIs)

        NOTE: You can manually create this file with your own followed wallets!
        Format: CSV with columns: wallet_address, label, reason
        """
        print("⚠️  CopyBot follow list not available in free tier")
        print("💡 You can create your own at: src/agents/api_data/follow_list.csv")

        return self._get_cached_data("follow_list.csv")

    def get_copybot_recent_transactions(self):
        """
        Placeholder for copybot transactions (not available in free APIs)

        NOTE: You can use Helius webhooks or Solana transaction monitoring
        """
        print("⚠️  CopyBot transactions not available in free tier")
        print("💡 Consider using Helius webhooks for wallet monitoring")

        return self._get_cached_data("recent_txs.csv")

    def _get_cached_data(self, filename):
        """
        Fallback: try to load cached data if API fails
        """
        try:
            cache_path = self.base_dir / filename
            if cache_path.exists():
                df = pd.read_csv(cache_path)
                print(f"📦 Loaded {len(df)} rows from cache: {filename}")
                return df
            else:
                print(f"❌ No cached data available for {filename}")
                return None
        except Exception as e:
            print(f"💥 Error loading cache: {str(e)}")
            return None

if __name__ == "__main__":
    print("🆓 Free Market Data API Test Suite 🚀")
    print("=" * 50)

    # Initialize API
    api = FreeMarketDataAPI()

    print("\n📊 Testing Free Data Sources...")

    # Test Liquidation Data
    print("\n💥 Testing Liquidation Data (CoinGlass)...")
    liq_data = api.get_liquidation_data(symbol="BTC", limit=1000)
    if liq_data is not None:
        print(f"✨ Liquidation Preview:\n{liq_data.head()}")

    # Test Funding Rate Data
    print("\n💰 Testing Funding Data (CoinGlass)...")
    funding_data = api.get_funding_data()
    if funding_data is not None:
        print(f"✨ Funding Preview:\n{funding_data.head()}")

    # Test Open Interest
    print("\n📈 Testing Open Interest (CoinGlass)...")
    oi_data = api.get_oi_data(symbol="BTC")
    if oi_data is not None:
        print(f"✨ OI Preview:\n{oi_data.head()}")

    # Test Total OI
    print("\n📊 Testing Total OI (CoinGlass)...")
    oi_total = api.get_oi_total()
    if oi_total is not None:
        print(f"✨ Total OI Preview:\n{oi_total.head()}")

    # Test New Tokens
    print("\n🔑 Testing New Tokens (BirdEye)...")
    token_data = api.get_token_addresses()
    if token_data is not None:
        print(f"✨ New Tokens Preview:\n{token_data.head()}")

    print("\n✨ Free API Test Complete! ✨")
    print("\n💡 All data cached to: src/agents/api_data/")
    print("💡 This is 100% FREE - no MoonDev API needed!")
