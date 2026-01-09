import requests

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2/events?limit=200"


def _fetch_markets(session, limit=1000, max_pages=20):
    markets = []
    cursor = None
    pages = 0
    while pages < max_pages:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = session.get(f"{KALSHI_API}/markets", params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        markets.extend(payload.get("markets", []))
        cursor = payload.get("cursor")
        if not cursor:
            break
        pages += 1
    return markets


def _market_volume(market):
    return (
        market.get("volume")
        or market.get("volume_24h")
        or market.get("volume_usd")
        or 0
    )


def run():
    session = requests.Session()
    markets = _fetch_markets(session)
    if not markets:
        print("No markets returned from Kalshi.")
        return

    top_markets = sorted(markets, key=_market_volume, reverse=True)[:100]
    for idx, market in enumerate(top_markets, start=1):
        volume = _market_volume(market)
        ticker = market.get("ticker") or market.get("market_ticker")
        title = market.get("title")
        subtitle = market.get("subtitle")
        close_time = market.get("close_time")
        print(
            f"{idx:03d}. {ticker} | {title}"
            f"{' - ' + subtitle if subtitle else ''}"
            f" | volume={volume} | close_time={close_time}"
        )


if __name__ == "__main__":
    run()
