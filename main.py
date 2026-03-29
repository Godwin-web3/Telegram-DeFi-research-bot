import os
import requests
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_flask).start()

BOT_TOKEN = os.environ["BOT_TOKEN"]

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_COIN_URL = "https://api.coingecko.com/api/v3/coins"
DEFILLAMA_URL = "https://api.llama.fi/protocols"
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi/pools"
DEFILLAMA_HACKS_URL = "https://api.llama.fi/hacks"
DEFILLAMA_STABLES_URL = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
DEFILLAMA_CHAINS_URL = "https://api.llama.fi/v2/chains"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000

COIN_ID_ALIASES = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "dot": "polkadot",
    "matic": "matic-network",
    "ltc": "litecoin",
    "avax": "avalanche-2",
    "link": "chainlink",
    "uni": "uniswap",
    "atom": "cosmos",
    "etc": "ethereum-classic",
}

BLOCKCHAIR_CHAINS = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "ltc": "litecoin",
    "litecoin": "litecoin",
    "bch": "bitcoin-cash",
    "bitcoin-cash": "bitcoin-cash",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "dash": "dash",
    "xrp": "ripple",
    "ripple": "ripple",
    "xlm": "stellar",
    "stellar": "stellar",
    "ada": "cardano",
    "cardano": "cardano",
    "xmr": "monero",
    "monero": "monero",
    "zec": "zcash",
    "zcash": "zcash",
    "bsv": "bitcoin-sv",
}

# Known exchange/contract addresses.
# ETH/BTC keys stored lowercase (case-insensitive lookup).
# Solana keys stored exact-case (base58 is case-sensitive).
KNOWN_ADDRESSES = {
    # ── Bitcoin ──────────────────────────────────────────────
    "1ndyjtntjmwk5xpnhjgamu4hdhigtobu1s": "Binance",
    "3lyjfcfhpxyjremsask2jkn69lweyKzexb".lower(): "Binance",
    "34xp4vrocgjym3xr7ycvpfhocnxv4twseo": "Binance",
    "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h": "Binance",
    "3cbq7at1ty8kmxwlh3haxwateyff5ra2hn": "Binance",
    "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97": "Binance",
    "3qjmv3qfvl9suyo34yihaf3srcw3qsinyc": "Coinbase",
    "3bpendnlobk64nxkfltbhqbpaqoqnwqtta": "Coinbase",
    "1grizzq4x7ujvhqpeuizlhe8t2pvxsqvwm": "Coinbase",
    "3m8xgfbkwkkf7mibzpku4fczygsfecebbmen": "Kraken",
    "3fu7zpbzbnblwgf2vd6wkfgeqszcfi8j9p": "Kraken",
    "bc1qazcm763858nkj2dj986etajv6wquslv8uxjyod": "Bitfinex",
    "1kr6qsydw9bfqg1mxipnnu6wpjgmua9i1g": "Bitfinex",
    "3jzq4atuahhuaxrlhxllmhhto133j9rq8dw": "Bitfinex",
    "1fezgm8ywuhrpegpchfcexlmvhjtmq4cnjf": "OKX",
    "3lqnpbcmjsimth4b2mxr3txqn17mvmpsb": "OKX",
    "14crbfkuvzxqhm3thbzjuv76yecm7uymnx": "Bybit",
    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh": "Gemini",
    "1garzww7whd5mrrs1arqc3ixkzwwkjyzxz": "Huobi",
    "1kaz2dg9vn4t50h1gy5ywm6gn7yopkdxgt": "Huobi",
    # ── Ethereum ─────────────────────────────────────────────
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance",
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance",
    "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance",
    "0x56eddb7aa87536c09ccc2793473599fd21a8b17f": "Binance",
    "0x4976a4a02f38326660d17bf34b431dc6e2eb2327": "Binance",
    "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase",
    "0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43": "Coinbase",
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase",
    "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken",
    "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13": "Kraken",
    "0xe853c56864a2ebe4576a807d26fdc4a0ada51919": "Kraken",
    "0x1151314c646ce4e0efd76d1af4760ae66a9fe30": "Bitfinex",
    "0x742d35cc6634c0532925a3b844bc454e4438f44e": "Bitfinex",
    "0x876eabf441b2ee5b5b0554fd502a8e0600950cfa": "Bitfinex",
    "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKX",
    "0x98ec059dc3adfbdd63429454aeb0c990fba4a128": "OKX",
    "0xf89d7b9c864f589bbf53a82105107622b35eaa40": "Bybit",
    "0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4": "Bybit",
    "0xd24400ae8bfebb18ca49be86258a3c749cf46853": "Gemini",
    "0xab5c66752a9e8167967685f1450532fb96d25d38": "Huobi",
    "0x6748f50f686bfbca6fe8ad62b22228b87f31ff2b": "Huobi",
    "0x5c985e89dde482efe97ea9f1950ad149eb73829b": "Huobi",
    "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13": "Uniswap V3 Router",
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
    "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch",
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "0x Exchange",
    "0x00000000219ab540356cbb839cbe05303d7705fa": "ETH2 Deposit Contract",
    # ── Solana (exact case — base58 is case-sensitive) ────────
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance",
    "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvh5zL": "Binance",
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": "Coinbase",
    "FWznbcNXWQuHTawe9RxvQ2LdCENssh12dsznf4RiouN5": "Kraken",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BrmF38rclF3i": "Bybit",
    "5VCTMy4MpNQJjfV86MgJbsBzLj4KDEFoVt7ePLJBxpPK": "OKX",
    "HzcDjG9HoqnPpkBGqyNzSAHJVbwrHmMWkrA2kBdFbJV6": "OKX",
    "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm": "Huobi",
    "4bfCGDCTCpEFHXRTx5EaaCEGJbHuJJd8ydKAojGQnF9N": "Raydium",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium Program",
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter Aggregator",
}

EXCHANGE_LABELS = {
    "Binance", "Coinbase", "Kraken", "Bitfinex", "OKX",
    "Bybit", "Gemini", "Huobi",
}

EXPLORER_URLS = {
    "bitcoin": "https://blockchair.com/bitcoin/transaction/",
    "ethereum": "https://etherscan.io/tx/",
    "litecoin": "https://blockchair.com/litecoin/transaction/",
    "bitcoin-cash": "https://blockchair.com/bitcoin-cash/transaction/",
    "dogecoin": "https://blockchair.com/dogecoin/transaction/",
    "dash": "https://blockchair.com/dash/transaction/",
    "ripple": "https://blockchair.com/ripple/transaction/",
    "stellar": "https://blockchair.com/stellar/transaction/",
    "cardano": "https://blockchair.com/cardano/transaction/",
    "monero": "https://blockchair.com/monero/transaction/",
    "zcash": "https://blockchair.com/zcash/transaction/",
    "bitcoin-sv": "https://blockchair.com/bitcoin-sv/transaction/",
    "solana": "https://solscan.io/tx/",
}

WHALE_THRESHOLD_USD = 1_000_000


# ─── Helpers ──────────────────────────────────────────────────────────────────

def resolve_coin_id(symbol: str) -> str:
    return COIN_ID_ALIASES.get(symbol.lower(), symbol.lower())


def label_address(address: str) -> str:
    if not address:
        return "Unknown wallet"
    # Try exact match first (Solana is case-sensitive), then lowercase (ETH/BTC)
    name = KNOWN_ADDRESSES.get(address) or KNOWN_ADDRESSES.get(address.lower())
    if name:
        return name
    short = address[:8] + "..." + address[-6:]
    return f"Unknown ({short})"


def classify_flow(sender_addr: str, receiver_addr: str) -> str:
    sender_name = KNOWN_ADDRESSES.get(sender_addr) or KNOWN_ADDRESSES.get(sender_addr.lower()) if sender_addr else None
    receiver_name = KNOWN_ADDRESSES.get(receiver_addr) or KNOWN_ADDRESSES.get(receiver_addr.lower()) if receiver_addr else None

    if receiver_name and receiver_name in EXCHANGE_LABELS:
        return f"🔴 Likely Sell → {receiver_name}"
    if sender_name and sender_name in EXCHANGE_LABELS:
        return f"🔵 Exchange Withdrawal ← {sender_name}"
    if receiver_name:
        return f"🟡 DEX / Contract → {receiver_name}"
    if sender_name:
        return f"🟡 DEX / Contract ← {sender_name}"
    return "⚪ Wallet Transfer"


def format_usd(amount: float) -> str:
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    return f"${amount:,.0f}"


def time_ago(time_str: str) -> str:
    if not time_str:
        return "unknown time"
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"
    except ValueError:
        return time_str


# ─── CoinGecko ────────────────────────────────────────────────────────────────

def fetch_price(coin_id: str) -> dict | None:
    try:
        r = requests.get(COINGECKO_URL, params={
            "vs_currency": "usd",
            "ids": coin_id,
            "price_change_percentage": "24h",
        }, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None
    except requests.RequestException:
        return None


def fetch_sol_price_usd() -> float:
    coin = fetch_price("solana")
    return coin.get("current_price", 0) if coin else 0


def fetch_multiple_prices(coin_ids: list[str]) -> list[dict] | None:
    try:
        r = requests.get(COINGECKO_URL, params={
            "vs_currency": "usd",
            "ids": ",".join(coin_ids),
            "price_change_percentage": "24h",
        }, timeout=10)
        r.raise_for_status()
        return r.json() or None
    except requests.RequestException:
        return None


def fetch_coin_detail(coin_id: str) -> dict | None:
    try:
        r = requests.get(
            f"{COINGECKO_COIN_URL}/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
            },
            timeout=12,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


def fetch_top_movers() -> list[dict] | None:
    try:
        r = requests.get(COINGECKO_URL, params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "price_change_percentage": "24h",
        }, timeout=15)
        r.raise_for_status()
        return r.json() or None
    except requests.RequestException:
        return None


# ─── DeFiLlama ────────────────────────────────────────────────────────────────

def fetch_tvl(query: str) -> dict | None:
    try:
        r = requests.get(DEFILLAMA_URL, timeout=15)
        r.raise_for_status()
        protocols = r.json()
    except requests.RequestException:
        return None

    q = query.lower().strip()

    # 1. Exact slug match
    for p in protocols:
        if p.get("slug", "").lower() == q:
            return p

    # 2. Exact name match (case-insensitive)
    for p in protocols:
        if p.get("name", "").lower() == q:
            return p

    # 3. Partial match — return highest-TVL result
    matches = [
        p for p in protocols
        if q in p.get("name", "").lower() or q in p.get("slug", "").lower()
    ]
    if matches:
        return max(matches, key=lambda x: x.get("tvl") or 0)

    return None


def fetch_yields_pools() -> list[dict] | None:
    try:
        r = requests.get(DEFILLAMA_YIELDS_URL, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])
    except requests.RequestException:
        return None


def fetch_hacks() -> list[dict] | None:
    try:
        r = requests.get(DEFILLAMA_HACKS_URL, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


def fetch_stables() -> list[dict] | None:
    try:
        r = requests.get(DEFILLAMA_STABLES_URL, timeout=15)
        r.raise_for_status()
        return r.json().get("peggedAssets", [])
    except requests.RequestException:
        return None


def fetch_chains() -> list[dict] | None:
    try:
        r = requests.get(DEFILLAMA_CHAINS_URL, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


# ─── Blockchair (all non-Solana chains) ───────────────────────────────────────

def fetch_whale_transactions(blockchain: str) -> list[dict] | None:
    is_ethereum = blockchain == "ethereum"
    value_field = "value_usd" if is_ethereum else "output_total_usd"
    filter_param = f"{value_field}({WHALE_THRESHOLD_USD}..)"

    try:
        r = requests.get(
            f"https://api.blockchair.com/{blockchain}/transactions",
            params={"q": filter_param, "limit": 3, "s": "time(desc)"},
            timeout=15,
        )
        r.raise_for_status()
        txns = r.json().get("data", [])
        return [
            {
                "hash": tx.get("hash", "N/A"),
                "time": tx.get("time", ""),
                "value_usd": tx.get(value_field, 0) or 0,
            }
            for tx in txns
        ]
    except requests.RequestException:
        return None


def fetch_transaction_detail(blockchain: str, tx_hash: str) -> dict | None:
    try:
        r = requests.get(
            f"https://api.blockchair.com/{blockchain}/dashboards/transaction/{tx_hash}",
            timeout=12,
        )
        r.raise_for_status()
        tx_data = r.json().get("data", {}).get(tx_hash, {})

        if blockchain == "ethereum":
            tx = tx_data.get("transaction", {})
            return {"sender": tx.get("sender", ""), "receiver": tx.get("recipient", "")}

        inputs = tx_data.get("inputs", [])
        outputs = tx_data.get("outputs", [])
        top_in = max(inputs, key=lambda x: x.get("value", 0), default={})
        top_out = max(outputs, key=lambda x: x.get("value", 0), default={})
        return {"sender": top_in.get("recipient", ""), "receiver": top_out.get("recipient", "")}
    except (requests.RequestException, KeyError):
        return None


# ─── Solana RPC ───────────────────────────────────────────────────────────────

def _solana_rpc(method: str, params: list, timeout: int = 15) -> dict | None:
    try:
        r = requests.post(SOLANA_RPC, json={
            "jsonrpc": "2.0", "id": 1, "method": method, "params": params,
        }, timeout=timeout)
        r.raise_for_status()
        result = r.json()
        if "error" in result:
            return None
        return result.get("result")
    except requests.RequestException:
        return None


def fetch_solana_whale_transactions() -> list[dict] | None:
    sol_price = fetch_sol_price_usd()
    if sol_price <= 0:
        return None

    threshold_lamports = int((WHALE_THRESHOLD_USD / sol_price) * LAMPORTS_PER_SOL)

    slot = _solana_rpc("getSlot", [], timeout=8)
    if not slot:
        return None

    results = []
    seen_sigs = set()

    for offset in range(40):
        if len(results) >= 3:
            break

        block = _solana_rpc("getBlock", [
            slot - offset,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0,
                "transactionDetails": "accounts",
                "rewards": False,
            },
        ], timeout=18)

        if not block:
            continue

        block_time = block.get("blockTime")
        time_str = (
            datetime.utcfromtimestamp(block_time).strftime("%Y-%m-%d %H:%M:%S")
            if block_time else ""
        )

        for tx in block.get("transactions", []):
            if len(results) >= 3:
                break
            if tx.get("meta", {}).get("err"):
                continue

            meta = tx.get("meta", {})
            pre_bal = meta.get("preBalances", [])
            post_bal = meta.get("postBalances", [])
            keys_raw = tx.get("transaction", {}).get("accountKeys", [])
            sigs = tx.get("transaction", {}).get("signatures", [])
            sig = sigs[0] if sigs else ""

            if not sig or sig in seen_sigs:
                continue

            def get_pubkey(k):
                return k.get("pubkey", "") if isinstance(k, dict) else str(k)

            # Find the account with the largest SOL decrease (sender)
            sender_idx, max_decrease = -1, threshold_lamports
            for i, (pre, post) in enumerate(zip(pre_bal, post_bal)):
                diff = pre - post
                if diff > max_decrease:
                    max_decrease, sender_idx = diff, i

            if sender_idx == -1:
                continue

            # Find the account with the largest SOL increase (receiver)
            receiver_idx, max_increase = -1, 0
            for i, (pre, post) in enumerate(zip(pre_bal, post_bal)):
                diff = post - pre
                if diff > max_increase:
                    max_increase, receiver_idx = diff, i

            sol_amount = max_decrease / LAMPORTS_PER_SOL
            value_usd = sol_amount * sol_price

            sender_addr = get_pubkey(keys_raw[sender_idx]) if sender_idx < len(keys_raw) else ""
            receiver_addr = get_pubkey(keys_raw[receiver_idx]) if 0 <= receiver_idx < len(keys_raw) else ""

            seen_sigs.add(sig)
            results.append({
                "hash": sig,
                "time": time_str,
                "value_usd": value_usd,
                "sol_amount": sol_amount,
                "sender": sender_addr,
                "receiver": receiver_addr,
            })

    return results


# ─── Bot command handlers ─────────────────────────────────────────────────────

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /price <coin symbol or name>\nExamples: /price BTC  |  /price ethereum"
        )
        return

    symbol = context.args[0]
    await update.message.reply_text(f"Fetching price for {symbol.upper()}...")

    coin = fetch_price(resolve_coin_id(symbol))
    if coin is None:
        await update.message.reply_text(
            f"Could not find data for '{symbol}'. "
            "Try the full CoinGecko ID (e.g., bitcoin, ethereum, solana)."
        )
        return

    name = coin.get("name", symbol.upper())
    ticker = coin.get("symbol", "").upper()
    price = coin.get("current_price") or 0
    market_cap = coin.get("market_cap")
    change_24h = coin.get("price_change_percentage_24h")

    price_str = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"
    market_cap_str = f"${market_cap:,.0f}" if market_cap else "N/A"
    change_str = f"{change_24h:+.2f}%" if change_24h is not None else "N/A"
    change_emoji = "📈" if (change_24h or 0) >= 0 else "📉"

    await update.message.reply_text(
        f"*{name} ({ticker})*\n\n"
        f"💰 Price: `{price_str}`\n"
        f"📊 Market Cap: `{market_cap_str}`\n"
        f"{change_emoji} 24h Change: `{change_str}`",
        parse_mode="Markdown",
    )


async def whale_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    supported = "BTC, ETH, LTC, BCH, DOGE, DASH, XRP, XLM, ADA, XMR, ZEC, *SOL*"
    if not context.args:
        await update.message.reply_text(
            f"Usage: /whale <coin>\nExamples: /whale BTC  |  /whale SOL\n\nSupported: {supported}",
            parse_mode="Markdown",
        )
        return

    symbol = context.args[0].lower()
    is_solana = symbol in ("sol", "solana")

    if not is_solana and symbol not in BLOCKCHAIR_CHAINS:
        await update.message.reply_text(
            f"'{symbol.upper()}' is not supported for whale tracking.\nSupported: {supported}",
            parse_mode="Markdown",
        )
        return

    chain_label = "Solana" if is_solana else BLOCKCHAIR_CHAINS[symbol].title()
    await update.message.reply_text(f"🔍 Scanning whale transactions on {chain_label}...")

    # ── Fetch transactions ─────────────────────────────────────────────────────
    if is_solana:
        txns = fetch_solana_whale_transactions()
        blockchain = "solana"
        pre_fetched_detail = True  # Solana already includes sender/receiver
    else:
        blockchain = BLOCKCHAIR_CHAINS[symbol]
        txns = fetch_whale_transactions(blockchain)
        pre_fetched_detail = False

    if txns is None:
        await update.message.reply_text(
            "Failed to fetch whale data. The provider may be temporarily unavailable."
        )
        return

    if not txns:
        await update.message.reply_text(
            f"No transactions ≥ $1M found in recent {chain_label} blocks."
        )
        return

    # ── Format output ──────────────────────────────────────────────────────────
    explorer_base = EXPLORER_URLS.get(blockchain, "")
    lines = [f"🐋 *Whale Transactions — {chain_label}* _(≥ $1M)_\n"]

    for i, tx in enumerate(txns, 1):
        tx_hash = tx["hash"]
        value = format_usd(tx["value_usd"])
        when = time_ago(tx["time"])

        if is_solana:
            sol_amt = tx.get("sol_amount", 0)
            value_line = f"*{i}. {value}* ({sol_amt:,.0f} SOL)  •  🕐 {when}"
            sender_addr = tx.get("sender", "")
            receiver_addr = tx.get("receiver", "")
        else:
            value_line = f"*{i}. {value}*  •  🕐 {when}"
            detail = fetch_transaction_detail(blockchain, tx_hash)
            sender_addr = detail.get("sender", "") if detail else ""
            receiver_addr = detail.get("receiver", "") if detail else ""

        sender_label = label_address(sender_addr)
        receiver_label = label_address(receiver_addr)
        signal = classify_flow(sender_addr, receiver_addr)

        explorer_link = f"{explorer_base}{tx_hash}" if explorer_base else ""
        link_line = (
            f"  🔗 [View tx]({explorer_link})"
            if explorer_link
            else f"  `{tx_hash[:10]}...{tx_hash[-6:]}`"
        )

        lines.append(
            f"{value_line}\n"
            f"  📤 From: {sender_label}\n"
            f"  📥 To:   {receiver_label}\n"
            f"  {signal}\n"
            f"{link_line}"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def yield_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /yield <token symbol>\n"
            "Examples: /yield ETH  |  /yield USDC  |  /yield BTC  |  /yield SOL"
        )
        return

    query = context.args[0].upper()
    await update.message.reply_text(f"Searching best yields for {query}...")

    pools = fetch_yields_pools()
    if pools is None:
        await update.message.reply_text("Failed to fetch yield data. Try again later.")
        return

    matches = [
        p for p in pools
        if query in (p.get("symbol") or "").upper()
        and (p.get("apy") or 0) > 0
        and (p.get("tvlUsd") or 0) >= 100_000
    ]

    if not matches:
        await update.message.reply_text(
            f"No yield opportunities found for '{query}'.\n"
            "Try the base token symbol, e.g.:\n"
            "  /yield ETH\n  /yield USDC\n  /yield BTC"
        )
        return

    matches.sort(key=lambda p: p.get("apy") or 0, reverse=True)
    top = matches[:6]

    lines = [f"🌾 *Best Yields for {query}* _(min $100K TVL)_\n"]

    for i, p in enumerate(top, 1):
        protocol = (p.get("project") or "Unknown").title()
        chain = p.get("chain") or "?"
        symbol = p.get("symbol") or query
        apy = p.get("apy") or 0
        apy_base = p.get("apyBase") or 0
        apy_reward = p.get("apyReward") or 0
        tvl = p.get("tvlUsd") or 0
        pool_meta = p.get("poolMeta")

        label = f"{symbol}" + (f" ({pool_meta})" if pool_meta else "")
        reward_str = f" _{apy_base:.1f}% base + {apy_reward:.1f}% rewards_" if apy_reward > 0 else ""

        lines.append(
            f"*{i}. {protocol}* — {chain}\n"
            f"   Pool: `{label}`\n"
            f"   💹 APY: `{apy:.2f}%`{reward_str}\n"
            f"   💰 TVL: `{format_usd(tvl)}`"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def pools_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /pools <protocol name>\n"
            "Examples: /pools uniswap  |  /pools aave  |  /pools curve  |  /pools lido"
        )
        return

    query = " ".join(context.args).lower().strip()
    await update.message.reply_text(f"Fetching pools for {query}...")

    pools = fetch_yields_pools()
    if pools is None:
        await update.message.reply_text("Failed to fetch pool data. Try again later.")
        return

    matches = [
        p for p in pools
        if query in (p.get("project") or "").lower()
        and (p.get("tvlUsd") or 0) > 0
    ]

    if not matches:
        await update.message.reply_text(
            f"No pools found for '{query}'.\n"
            "Try the protocol slug used on DeFiLlama, e.g.:\n"
            "  /pools uniswap-v3\n  /pools aave-v3\n  /pools curve-dex"
        )
        return

    matches.sort(key=lambda p: p.get("tvlUsd") or 0, reverse=True)
    top = matches[:6]

    protocol_display = (top[0].get("project") or query).title()
    total_tvl = sum(p.get("tvlUsd") or 0 for p in matches)
    lines = [
        f"🏊 *{protocol_display} Pools*\n"
        f"_{len(matches)} pools found · Total TVL: {format_usd(total_tvl)}_\n"
    ]

    for i, p in enumerate(top, 1):
        chain = p.get("chain") or "?"
        symbol = p.get("symbol") or "?"
        apy = p.get("apy") or 0
        apy_base = p.get("apyBase") or 0
        apy_reward = p.get("apyReward") or 0
        tvl = p.get("tvlUsd") or 0
        pool_meta = p.get("poolMeta")

        label = symbol + (f" ({pool_meta})" if pool_meta else "")
        reward_str = (
            f"\n   _{apy_base:.1f}% base + {apy_reward:.1f}% rewards_"
            if apy_reward > 0 else ""
        )

        lines.append(
            f"*{i}. {label}* — {chain}\n"
            f"   💹 APY: `{apy:.2f}%`{reward_str}\n"
            f"   💰 TVL: `{format_usd(tvl)}`"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def tvl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /tvl <protocol name>\n"
            "Examples: /tvl uniswap  |  /tvl aave  |  /tvl lido  |  /tvl curve"
        )
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"Fetching TVL for {query}...")

    protocol = fetch_tvl(query)

    if protocol is None:
        await update.message.reply_text(
            f"Could not find '{query}' on DeFiLlama.\n\n"
            "Try the exact protocol name, for example:\n"
            "  /tvl uniswap\n"
            "  /tvl aave\n"
            "  /tvl curve\n"
            "  /tvl lido\n"
            "  /tvl makerdao"
        )
        return

    name = protocol.get("name", query)
    tvl = protocol.get("tvl") or 0
    change_1d = protocol.get("change_1d")
    change_7d = protocol.get("change_7d")
    chains = protocol.get("chains") or []
    category = protocol.get("category", "")

    tvl_str = format_usd(tvl)
    change_1d_str = f"{change_1d:+.2f}%" if change_1d is not None else "N/A"
    change_7d_str = f"{change_7d:+.2f}%" if change_7d is not None else "N/A"
    change_1d_emoji = "📈" if (change_1d or 0) >= 0 else "📉"
    change_7d_emoji = "📈" if (change_7d or 0) >= 0 else "📉"

    if len(chains) <= 6:
        chains_str = ", ".join(chains) if chains else "N/A"
    else:
        chains_str = ", ".join(chains[:6]) + f" +{len(chains) - 6} more"

    category_line = f"🏷 Category: `{category}`\n" if category else ""

    await update.message.reply_text(
        f"*{name}*\n"
        f"{category_line}\n"
        f"💰 TVL: `{tvl_str}`\n"
        f"{change_1d_emoji} 24h Change: `{change_1d_str}`\n"
        f"{change_7d_emoji} 7d Change: `{change_7d_str}`\n\n"
        f"⛓ Chains: {chains_str}",
        parse_mode="Markdown",
    )


async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /compare <coin1> <coin2>\n"
            "Examples: /compare BTC ETH  |  /compare SOL AVAX"
        )
        return

    sym1, sym2 = context.args[0], context.args[1]
    id1, id2 = resolve_coin_id(sym1), resolve_coin_id(sym2)
    await update.message.reply_text(f"Comparing {sym1.upper()} vs {sym2.upper()}...")

    coins = fetch_multiple_prices([id1, id2])
    if not coins or len(coins) < 2:
        found_ids = {c.get("id") for c in (coins or [])}
        missing = [s for s, i in [(sym1, id1), (sym2, id2)] if i not in found_ids]
        await update.message.reply_text(
            f"Could not find data for: {', '.join(missing)}.\n"
            "Try full CoinGecko IDs (e.g., bitcoin, ethereum, solana)."
        )
        return

    coin_map = {c["id"]: c for c in coins}
    c1 = coin_map.get(id1) or coins[0]
    c2 = coin_map.get(id2) or coins[1]

    def row(label, v1, v2):
        return f"*{label}*\n  {c1['symbol'].upper()}: `{v1}`\n  {c2['symbol'].upper()}: `{v2}`"

    def fmt_price(c):
        p = c.get("current_price") or 0
        return f"${p:,.6f}" if p < 1 else f"${p:,.2f}"

    def fmt_mcap(c):
        m = c.get("market_cap") or 0
        return format_usd(m)

    def fmt_change(c):
        ch = c.get("price_change_percentage_24h")
        return f"{ch:+.2f}%" if ch is not None else "N/A"

    def fmt_rank(c):
        r = c.get("market_cap_rank")
        return f"#{r}" if r else "N/A"

    def fmt_vol(c):
        v = c.get("total_volume") or 0
        return format_usd(v)

    lines = [
        f"⚔️ *{c1['name']} vs {c2['name']}*\n",
        row("Price", fmt_price(c1), fmt_price(c2)),
        row("Market Cap", fmt_mcap(c1), fmt_mcap(c2)),
        row("24h Change", fmt_change(c1), fmt_change(c2)),
        row("24h Volume", fmt_vol(c1), fmt_vol(c2)),
        row("MC Rank", fmt_rank(c1), fmt_rank(c2)),
    ]

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def supply_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /supply <coin>\n"
            "Examples: /supply BTC  |  /supply ETH  |  /supply SOL"
        )
        return

    symbol = context.args[0]
    coin_id = resolve_coin_id(symbol)
    await update.message.reply_text(f"Fetching supply data for {symbol.upper()}...")

    data = fetch_coin_detail(coin_id)
    if not data:
        await update.message.reply_text(
            f"Could not find '{symbol}'. Try the full CoinGecko ID (e.g., bitcoin, ethereum)."
        )
        return

    name = data.get("name", symbol.upper())
    ticker = (data.get("symbol") or "").upper()
    md = data.get("market_data", {})

    price = (md.get("current_price") or {}).get("usd") or 0
    circ = md.get("circulating_supply") or 0
    total = md.get("total_supply")
    max_s = md.get("max_supply")
    mc = (md.get("market_cap") or {}).get("usd") or 0
    ath = (md.get("ath") or {}).get("usd") or 0
    ath_change = (md.get("ath_change_percentage") or {}).get("usd")

    price_str = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"
    circ_str = f"{circ:,.0f} {ticker}"
    total_str = f"{total:,.0f} {ticker}" if total else "∞"
    max_str = f"{max_s:,.0f} {ticker}" if max_s else "∞"
    mc_str = format_usd(mc)
    ath_str = f"${ath:,.2f}"
    ath_change_str = f"{ath_change:.1f}%" if ath_change is not None else "N/A"

    pct_issued = f"{(circ / max_s * 100):.1f}%" if max_s and max_s > 0 else "N/A"

    inflation_line = ""
    if total and circ and total > circ:
        unlocked_pct = circ / total * 100
        inflation_line = f"🔓 Unlocked: `{unlocked_pct:.1f}%` of total supply\n"

    await update.message.reply_text(
        f"*{name} ({ticker}) — Tokenomics*\n\n"
        f"💰 Price: `{price_str}`\n"
        f"📊 Market Cap: `{mc_str}`\n\n"
        f"🔄 Circulating: `{circ_str}`\n"
        f"📦 Total Supply: `{total_str}`\n"
        f"🏔 Max Supply: `{max_str}`\n"
        f"📈 % Issued: `{pct_issued}`\n"
        f"{inflation_line}\n"
        f"🚀 ATH: `{ath_str}` ({ath_change_str} from ATH)",
        parse_mode="Markdown",
    )


async def gainers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fetching top gainers from the top 250 coins...")

    coins = fetch_top_movers()
    if not coins:
        await update.message.reply_text("Failed to fetch market data. Try again later.")
        return

    sorted_coins = sorted(
        [c for c in coins if c.get("price_change_percentage_24h") is not None],
        key=lambda c: c["price_change_percentage_24h"],
        reverse=True,
    )
    top = sorted_coins[:5]

    lines = ["🚀 *Top Gainers — 24h* _(from top 250 by market cap)_\n"]
    for i, c in enumerate(top, 1):
        name = c.get("name", "")
        ticker = (c.get("symbol") or "").upper()
        price = c.get("current_price") or 0
        change = c.get("price_change_percentage_24h") or 0
        mc = c.get("market_cap") or 0
        price_str = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"
        lines.append(
            f"*{i}. {name} ({ticker})*\n"
            f"   💰 `{price_str}`  📈 `{change:+.2f}%`\n"
            f"   MC: `{format_usd(mc)}`"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def losers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fetching top losers from the top 250 coins...")

    coins = fetch_top_movers()
    if not coins:
        await update.message.reply_text("Failed to fetch market data. Try again later.")
        return

    sorted_coins = sorted(
        [c for c in coins if c.get("price_change_percentage_24h") is not None],
        key=lambda c: c["price_change_percentage_24h"],
    )
    top = sorted_coins[:5]

    lines = ["📉 *Top Losers — 24h* _(from top 250 by market cap)_\n"]
    for i, c in enumerate(top, 1):
        name = c.get("name", "")
        ticker = (c.get("symbol") or "").upper()
        price = c.get("current_price") or 0
        change = c.get("price_change_percentage_24h") or 0
        mc = c.get("market_cap") or 0
        price_str = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"
        lines.append(
            f"*{i}. {name} ({ticker})*\n"
            f"   💰 `{price_str}`  📉 `{change:+.2f}%`\n"
            f"   MC: `{format_usd(mc)}`"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def hacks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fetching latest DeFi hacks & exploits...")

    hacks = fetch_hacks()
    if hacks is None:
        await update.message.reply_text("Failed to fetch hack data. Try again later.")
        return

    hacks_sorted = sorted(
        [h for h in hacks if h.get("date")],
        key=lambda h: h["date"],
        reverse=True,
    )[:8]

    if not hacks_sorted:
        await update.message.reply_text("No hack data available right now.")
        return

    lines = ["☠️ *Recent DeFi Hacks & Exploits*\n"]

    for h in hacks_sorted:
        name = h.get("name") or "Unknown Protocol"
        amount = h.get("amount") or 0
        technique = h.get("technique") or "Unknown"
        category = h.get("category") or ""
        chains = h.get("chains") or []
        ts = h.get("date") or 0
        link = h.get("link") or ""

        try:
            date_str = datetime.utcfromtimestamp(ts).strftime("%b %d, %Y")
        except Exception:
            date_str = "Unknown date"

        chain_str = ", ".join(chains[:3]) if chains else "Unknown"
        amount_str = format_usd(amount) if amount else "Unknown"
        link_line = f"  🔗 [Details]({link})" if link else ""
        category_str = f" · {category}" if category else ""

        lines.append(
            f"*{name}* — {date_str}\n"
            f"  💸 Lost: `{amount_str}`\n"
            f"  🛠 Method: `{technique}`{category_str}\n"
            f"  ⛓ Chain: {chain_str}"
            + (f"\n{link_line}" if link_line else "")
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def stables_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fetching stablecoin data...")

    stables = fetch_stables()
    if stables is None:
        await update.message.reply_text("Failed to fetch stablecoin data. Try again later.")
        return

    def get_circ(s):
        circ = s.get("circulating") or {}
        return circ.get("peggedUSD") or 0

    stables_sorted = sorted(stables, key=get_circ, reverse=True)[:10]

    PEG_TARGET = 1.0
    DEPEG_THRESHOLD = 0.005

    lines = ["💵 *Top Stablecoins by Market Cap*\n"]

    for i, s in enumerate(stables_sorted, 1):
        name = s.get("name") or "Unknown"
        symbol = (s.get("symbol") or "").upper()
        circ = get_circ(s)
        price = s.get("price")
        peg_type = s.get("pegType") or ""
        mechanism = s.get("pegMechanism") or ""

        circ_str = format_usd(circ) if circ else "N/A"
        mech_str = mechanism.replace("-", " ").title() if mechanism else "N/A"

        if price is not None:
            deviation = abs(price - PEG_TARGET)
            if deviation > DEPEG_THRESHOLD:
                status = f"⚠️ OFF-PEG `${price:.4f}`"
            else:
                status = f"✅ `${price:.4f}`"
        else:
            status = "❓ No price"

        lines.append(
            f"*{i}. {name} ({symbol})*\n"
            f"   💰 Supply: `{circ_str}`\n"
            f"   🎯 Peg: {status}\n"
            f"   ⚙️ Mechanism: `{mech_str}`"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def chains_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fetching TVL breakdown by blockchain...")

    chains = fetch_chains()
    if chains is None:
        await update.message.reply_text("Failed to fetch chain data. Try again later.")
        return

    chains_sorted = sorted(
        [c for c in chains if (c.get("tvl") or 0) > 0],
        key=lambda c: c.get("tvl") or 0,
        reverse=True,
    )[:12]

    total_tvl = sum(c.get("tvl") or 0 for c in chains_sorted)

    lines = [f"⛓ *TVL by Blockchain* _(Top 12)_\n_Total: {format_usd(total_tvl)}_\n"]

    for i, c in enumerate(chains_sorted, 1):
        name = c.get("name") or "Unknown"
        tvl = c.get("tvl") or 0
        share = (tvl / total_tvl * 100) if total_tvl > 0 else 0
        bar_filled = round(share / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        lines.append(
            f"*{i}. {name}*\n"
            f"   `{bar}` {share:.1f}%\n"
            f"   TVL: `{format_usd(tvl)}`"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to the DeFi Research Bot!\n\n"
        "📈 *Market Intelligence*\n"
        "  /price <coin> — Live price, market cap & 24h change\n"
        "  /compare <c1> <c2> — Side-by-side coin comparison\n"
        "  /supply <coin> — Tokenomics & supply breakdown\n"
        "  /gainers — Top 24h gainers (top 250 coins)\n"
        "  /losers — Top 24h losers (top 250 coins)\n\n"
        "🐋 *On-Chain*\n"
        "  /whale <coin> — Whale transactions with sell signals\n\n"
        "🏦 *DeFi*\n"
        "  /tvl <protocol> — Protocol TVL\n"
        "  /yield <token> — Best yield opportunities\n"
        "  /pools <protocol> — Top liquidity pools\n"
        "  /hacks — Latest exploits & amounts lost\n"
        "  /stables — Top stablecoins + depeg alerts\n"
        "  /chains — TVL breakdown by blockchain\n\n"
        "Examples:\n"
        "  /compare BTC ETH\n"
        "  /supply SOL\n"
        "  /gainers  |  /losers\n"
        "  /yield USDC  |  /pools aave\n"
        "  /hacks  |  /stables  |  /chains"
    )


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("whale", whale_command))
    app.add_handler(CommandHandler("tvl", tvl_command))
    app.add_handler(CommandHandler("yield", yield_command))
    app.add_handler(CommandHandler("pools", pools_command))
    app.add_handler(CommandHandler("compare", compare_command))
    app.add_handler(CommandHandler("supply", supply_command))
    app.add_handler(CommandHandler("gainers", gainers_command))
    app.add_handler(CommandHandler("losers", losers_command))
    app.add_handler(CommandHandler("hacks", hacks_command))
    app.add_handler(CommandHandler("stables", stables_command))
    app.add_handler(CommandHandler("chains", chains_command))
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
