class ProxyService:
    def get_proxy(self, settings: dict):
        proxy = settings.get("proxy", "") or ""
        if proxy:
            return proxy
        if settings.get("prefer_tor"):
            return "socks5://127.0.0.1:9050"
        return ""

    def label(self, proxy: str):
        return f"🛡 Proxy: {proxy}" if proxy else "⚪ No Proxy"
