"""End-to-end devnet demo client: get 402, pay with a throwaway devnet keypair (+memo nonce), retry.
Requires: pip install solders. Keypair stored in .devnet-keypair.json (git-ignored, devnet only)."""
import base64, json, os, sys, time, urllib.request, urllib.error
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import Transaction
from solders.hash import Hash

RPC = os.environ.get("SOLANA_RPC", "https://api.devnet.solana.com")
API = os.environ.get("API", "http://127.0.0.1:8402/quote?symbol=SOL")
MEMO = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")

def rpc(m, p):
    r = urllib.request.Request(RPC, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(),
                               {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())

def keypair():
    f = ".devnet-keypair.json"
    if os.path.exists(f):
        return Keypair.from_bytes(bytes(json.load(open(f))))
    k = Keypair(); json.dump(list(bytes(k)), open(f, "w")); os.chmod(f, 0o600); return k

def main():
    kp = keypair(); print("payer", kp.pubkey())
    bal = rpc("getBalance", [str(kp.pubkey())])["result"]["value"]
    if bal < 5_000_000:
        print("airdrop", rpc("requestAirdrop", [str(kp.pubkey()), 1_000_000_000]))
        for _ in range(30):
            time.sleep(2)
            bal = rpc("getBalance", [str(kp.pubkey())])["result"]["value"]
            if bal: break
    print("balance", bal)
    try:
        urllib.request.urlopen(API); sys.exit("expected 402")
    except urllib.error.HTTPError as e:
        assert e.code == 402; req = json.loads(e.read())
    acc = req["accepts"][0]; nonce = req["nonce"]; print("402 requirements", acc)
    ixs = [transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=Pubkey.from_string(acc["payTo"]),
                                   lamports=int(acc["maxAmountRequired"]))),
           Instruction(MEMO, nonce.encode(), [])]
    bh = Hash.from_string(rpc("getLatestBlockhash", [])["result"]["value"]["blockhash"])
    tx = Transaction([kp], Message(ixs, kp.pubkey()), bh)
    sig = rpc("sendTransaction", [base64.b64encode(bytes(tx)).decode(), {"encoding": "base64"}])
    if "result" not in sig:
        sys.exit(f"send failed: {sig.get('error', {}).get('message')} "
                 "(note: a fresh devnet payTo account needs >= rent-exempt minimum, ~0.00089 SOL, before small payments)")
    sig = sig["result"]; print("paid, signature", sig)
    for _ in range(30):
        time.sleep(2)
        st = rpc("getSignatureStatuses", [[sig]])["result"]["value"][0]
        if st and st.get("confirmationStatus") in ("confirmed", "finalized"): break
    hdr = base64.b64encode(json.dumps({"signature": sig, "nonce": nonce}).encode()).decode()
    r = urllib.request.urlopen(urllib.request.Request(API, headers={"X-PAYMENT": hdr}))
    print(r.status, r.read().decode())
    print(f"https://explorer.solana.com/tx/{sig}?cluster=devnet")
    try:  # replay the same payment: must be rejected
        urllib.request.urlopen(urllib.request.Request(API, headers={"X-PAYMENT": hdr})); print("replay ACCEPTED (bug)")
    except urllib.error.HTTPError as e:
        print("replay ->", e.code, json.loads(e.read())["error"])

if __name__ == "__main__":
    main()
