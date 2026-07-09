class ProxyService:
    def tor_proxy(self):
        return "socks5://127.0.0.1:9050"

    def custom_proxy(self, host: str, port: str, scheme: str = "http"):
        return f"{scheme}://{host}:{port}"

    def is_enabled(self, proxy_url: str) -> bool:
        return bool((proxy_url or "").strip())
