# 🔑 Provide Your API Keys Here

**When you're ready, paste your API keys below in this format:**

---

## ✅ Format to Share Your Keys

Copy this template and fill in your actual values:

```bash
# TRADING DATA APIs
BIRDEYE_API_KEY=paste_your_birdeye_key_here
RPC_ENDPOINT=paste_your_helius_rpc_url_here
COINGECKO_API_KEY=paste_your_coingecko_key_here

# BLOCKCHAIN KEYS (⚠️ Use a TEST wallet for initial setup!)
SOLANA_PRIVATE_KEY=paste_your_base58_private_key_here
HYPER_LIQUID_ETH_PRIVATE_KEY=paste_your_hyperliquid_key_here

# AI SERVICE KEYS
ANTHROPIC_KEY=paste_your_claude_key_here
OPENAI_KEY=paste_your_openai_key_here
DEEPSEEK_KEY=paste_your_deepseek_key_here
GROQ_API_KEY=paste_your_groq_key_here
GEMINI_KEY=paste_your_gemini_key_here
GROK_API_KEY=paste_your_grok_key_here
```

---

## 📝 What Each Key Should Look Like

### BirdEye API Key
- Format: Usually starts with a UUID or alphanumeric string
- Example: `abc123-def456-ghi789` (your actual key will be different)
- Get it at: https://birdeye.so → Sign up → API Keys

### Helius RPC Endpoint
- Format: Full URL with your API key embedded
- Example: `https://mainnet.helius-rpc.com/?api-key=YOUR-KEY-HERE`
- Get it at: https://helius.dev → Dashboard → RPC URLs

### CoinGecko API Key
- Format: Starts with `CG-` or similar
- Example: `CG-YourKeyHere123456789`
- Get it at: https://www.coingecko.com/en/api → Sign up → API Key

### Anthropic Claude API Key
- Format: Starts with `sk-ant-`
- Example: `sk-ant-api03-xxxxx...`
- Get it at: https://console.anthropic.com → API Keys

### OpenAI API Key
- Format: Starts with `sk-`
- Example: `sk-xxxxx...`
- Get it at: https://platform.openai.com → API Keys

### DeepSeek API Key
- Format: Starts with `sk-`
- Example: `sk-xxxxx...`
- Get it at: https://platform.deepseek.com → API Keys

### Groq API Key
- Format: Starts with `gsk_`
- Example: `gsk_xxxxx...`
- Get it at: https://console.groq.com → API Keys

### Gemini API Key
- Format: Starts with `AIzaSy`
- Example: `AIzaSyxxxxx...`
- Get it at: https://makersuite.google.com/app/apikey

### Grok (xAI) API Key
- Format: Starts with `xai-`
- Example: `xai-xxxxx...`
- Get it at: https://console.x.ai → API Keys

### Solana Private Key
- Format: Base58 encoded string (from Phantom/Solflare wallet)
- Example: `5Kbb37EAqQgZ9vWUHoPiC2uXYhyGSN...` (long string, 87-88 chars)
- ⚠️ **CRITICAL**: Use a TEST wallet with small amounts for initial setup!
- Export from: Phantom → Settings → Export Private Key

### HyperLiquid Private Key
- Format: Ethereum private key (starts with `0x`)
- Example: `0x1234567890abcdef...` (64 hex characters after 0x)
- ⚠️ **CRITICAL**: Use a TEST wallet!
- Get from: Your Ethereum wallet (MetaMask, etc.)

---

## 🔒 Security Guidelines

### DO:
- ✅ Use a TEST wallet for initial setup
- ✅ Start with small amounts ($10-50)
- ✅ Verify each key works before adding to .env
- ✅ Keep this document secure (delete after adding keys)
- ✅ Use separate wallets for testing vs production

### DON'T:
- ❌ Share your private keys in public channels
- ❌ Use your main wallet for testing
- ❌ Commit .env file to git (it's in .gitignore)
- ❌ Screenshot this file with your actual keys
- ❌ Store private keys in plaintext long-term

---

## 🚀 After You Provide Keys

I will:
1. ✅ Validate each key format
2. ✅ Insert them into your .env file
3. ✅ Test the setup with the compatibility checker
4. ✅ Run a safe test (coingecko_agent - read-only)
5. ✅ Confirm everything works before trading

---

## 📋 Quick Checklist

Before sharing your keys, verify you have:

- [ ] BirdEye account created (free tier is fine)
- [ ] Helius RPC endpoint (free tier is fine)
- [ ] Anthropic API key (you have Pro plan ✓)
- [ ] Other AI API keys (OpenAI, DeepSeek, Groq, Gemini, Grok)
- [ ] CoinGecko account (free tier is fine)
- [ ] TEST Solana wallet with small amount (not your main wallet!)
- [ ] TEST HyperLiquid account (optional - only if you want HL trading)

---

## 💡 What If I Don't Have All Keys Yet?

**No problem!** You can provide what you have now, and I'll:
- Set up the .env with placeholder values for missing keys
- Show you which agents will work with current setup
- Guide you on getting the remaining keys (if needed)

**Minimum to start:**
- Anthropic Key (you have ✓)
- BirdEye Key (you have ✓)
- Helius RPC (you have ✓)
- Solana Private Key (you have ✓)

Everything else is optional or has free alternatives!

---

## 🎯 Ready to Go?

**Option 1: Share All Keys Now**
Just paste your filled-in template above, and I'll set everything up!

**Option 2: Share Some Keys Now, Rest Later**
Tell me which keys you want to add first, and we'll do it in phases.

**Option 3: Test Without Real Keys First**
I can set up dummy values so you can see the system structure before committing real API keys.

---

**Just say**: "Here are my keys" and paste the template, or "Let's do Option X"! 🚀
