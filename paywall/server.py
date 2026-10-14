"""x402-style pay-per-request API on Solana devnet (stdlib only).
GET /quote?symbol=SOL -> 402 + payment requirements (recipient, lamports, memo nonce)
Client pays on devnet, retries with header X-PAYMENT: <base64 json {"signature": ...,"nonce":...}>
Server verifies the tx via Solana JSON-RPC getTransaction, then serves the resource once per nonce."""
import base64, json, os, secrets, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

RPC = os.environ.get("SOLANA_RPC", "https://api.devnet.solana.com")
PAY_TO = os.environ.get("PAY_TO", "DAfQDqhGReo6HrNac449XNo2pZ6zzaQ5k9sBrz95gcuy")
PRICE = int(os.environ.get("PRICE_LAMPORTS", "100000"))  # 0.0001 SOL

PENDING, USED = {}, set()

def rpc(method, params):
    req = urllib.request.Request(RPC, json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                                 "params": params}).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read()).get("result")

def verify_payment(sig, nonce, fetch=rpc):
    """Return (ok, reason). Checks: tx exists & succeeded, PAY_TO balance rose by >= PRICE, memo has nonce."""
    if sig in USED:
        return False, "signature already used"
    if nonce not in PENDING:
        return False, "unknown nonce"
    tx = fetch("getTransaction", [sig, {"encoding": "jsonParsed", "commitment": "confirmed",
                                        "maxSupportedTransactionVersion": 0}])
    if not tx:
        return False, "transaction not found"
    meta = tx["meta"]
    if meta.get("err"):
        return False, "transaction failed"
    keys = [k["pubkey"] if isinstance(k, dict) else k for k in tx["transaction"]["message"]["accountKeys"]]
    if PAY_TO not in keys:
        return False, "recipient not in tx"
    i = keys.index(PAY_TO)
    if meta["postBalances"][i] - meta["preBalances"][i] < PRICE:
        return False, "insufficient amount"
    if nonce not in json.dumps(meta.get("logMessages", [])):
        return False, "memo nonce missing"
    USED.add(sig); PENDING.pop(nonce, None)
    return True, "ok"

def requirements():
    nonce = secrets.token_hex(8); PENDING[nonce] = PRICE
    return {"x402Version": 1, "accepts": [{"scheme": "exact", "network": "solana-devnet",
            "payTo": PAY_TO, "asset": "SOL", "maxAmountRequired": str(PRICE),
            "memo": nonce, "description": "One market quote"}], "nonce": nonce}

class H(BaseHTTPRequestHandler):
    fetch = staticmethod(rpc)
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/quote":
            return self._send(404, {"error": "not found"})
        hdr = self.headers.get("X-PAYMENT")
        if not hdr:
            return self._send(402, requirements())
        try:
            p = json.loads(base64.b64decode(hdr))
            ok, why = verify_payment(p["signature"], p["nonce"], self.fetch)
        except Exception as e:
            ok, why = False, f"bad payment header: {e}"
        if not ok:
            return self._send(402, {"error": why, **requirements()})
        sym = parse_qs(u.query).get("symbol", ["SOL"])[0]
        self._send(200, {"symbol": sym, "quote": "demo-data", "paid": True})
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8402"))
    print(f"x402 paywall on :{port}, payTo={PAY_TO}, price={PRICE} lamports, rpc={RPC}")
    HTTPServer(("0.0.0.0", port), H).serve_forever()
