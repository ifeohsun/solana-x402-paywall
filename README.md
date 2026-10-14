# x402 Paywall on Solana — pay-per-request API with devnet settlement

Challenge: **Best Use of x402 on Solana** (Encode Solana Hackathon 2026)

A tiny HTTP API that charges per request using the x402 pattern:
1. `GET /quote` → **HTTP 402** with payment requirements (payTo, lamports, one-time memo nonce).
2. Client (human wallet or AI agent) sends a Solana devnet transfer with the nonce in a Memo.
3. Client retries with `X-PAYMENT: base64({"signature","nonce"})`.
4. Server verifies on-chain via `getTransaction` (success, recipient balance delta ≥ price,
   nonce in memo, signature not replayed) and returns the resource.

Failed payments are handled explicitly: unknown nonce, tx not found, failed tx, wrong recipient,
underpayment, missing memo and replayed signatures all return 402 with a fresh quote.

## Run
```bash
PAY_TO=<devnet address> PRICE_LAMPORTS=100000 python3 -m paywall.server   # :8402
curl -i localhost:8402/quote          # -> 402 + requirements
python3 -m unittest discover -s tests -t .   # offline tests with mocked RPC
```
Pay on devnet e.g. `solana transfer <PAY_TO> 0.0001 --with-memo <nonce> --url devnet`.

## How Solana powers it
Sub-second finality and sub-cent fees make per-request micropayments viable; settlement is
verified directly from Solana RPC, no payment processor or subscription.

Built October 2026, AI-assisted. Stdlib Python only. License: MIT.
