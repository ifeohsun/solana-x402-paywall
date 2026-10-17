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

## Live devnet demo
```bash
pip install solders
python3 -m paywall.server &        # terminal 1
python3 examples/pay_devnet.py     # 402 -> devnet transfer + memo -> X-PAYMENT retry -> 200, then replay -> 402
```
Verified on devnet 2026-10-17:
- [4MA5AksNHJy33wDS…](https://explorer.solana.com/tx/4MA5AksNHJy33wDSYGhwv7qHchVWSL1mvTnuQSQpUsBNYktP2hDZB88Q9u5x8YVnfujUANSEEfmm95i2F7Bvhter?cluster=devnet)
- [xuFer13etHE26ysT…](https://explorer.solana.com/tx/xuFer13etHE26ysT6fTXVBXSkPcKexUySv773hgybwaPr2mVkB8F3ekWquSWktnLDid3RjprdaksWNd6wejBmoQ?cluster=devnet)

Details in [DEPLOYMENTS.md](DEPLOYMENTS.md). Demo video: [demo-v1 release](https://github.com/ifeohsun/solana-x402-paywall/releases/tag/demo-v1).

## How Solana powers it
Sub-second finality and sub-cent fees make per-request micropayments viable; settlement is
verified directly from Solana RPC, no payment processor or subscription.

Built October 2026, AI-assisted. Stdlib Python only. License: MIT.
