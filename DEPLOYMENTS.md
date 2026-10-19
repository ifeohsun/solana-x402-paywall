# Devnet deployments & payment evidence

Network: **Solana devnet** · runs 2026-10-17 and 2026-10-19 (UTC+8) with `examples/pay_devnet.py` against a local `paywall.server`.

| Role | Address |
|---|---|
| Server payTo (merchant) | [DAfQDqhGReo6HrNac449XNo2pZ6zzaQ5k9sBrz95gcuy](https://explorer.solana.com/address/DAfQDqhGReo6HrNac449XNo2pZ6zzaQ5k9sBrz95gcuy?cluster=devnet) |
| Demo client (payer, devnet-only key) | [CAEpdiD4u5kLQg95RoXm33bKopuMh6RR6ZQPgdsME1vi](https://explorer.solana.com/address/CAEpdiD4u5kLQg95RoXm33bKopuMh6RR6ZQPgdsME1vi?cluster=devnet) |

Price: 100 000 lamports (0.0001 SOL) per request, nonce carried in an SPL Memo.

## End-to-end x402 payments (402 → pay → verify → 200)

| # | Nonce (memo) | Signature | Result |
|---|---|---|---|
| 1 | `21823bde08ad6357` | [4MA5AksNHJy3…](https://explorer.solana.com/tx/4MA5AksNHJy33wDSYGhwv7qHchVWSL1mvTnuQSQpUsBNYktP2hDZB88Q9u5x8YVnfujUANSEEfmm95i2F7Bvhter?cluster=devnet) | 200 `{"paid": true}`; replay → 402 "signature already used" |
| 2 | `ec9d610de87d3101` | [xuFer13etHE2…](https://explorer.solana.com/tx/xuFer13etHE26ysT6fTXVBXSkPcKexUySv773hgybwaPr2mVkB8F3ekWquSWktnLDid3RjprdaksWNd6wejBmoQ?cluster=devnet) | 200 `{"paid": true}`; replay → 402 "signature already used" |
| 3 | `776a5d1c155834f7` | [58HkqR6nhbb1…](https://explorer.solana.com/tx/58HkqR6nhbb1CkYFWv2dEqbcHPwCqPqGQAizaUu7shusGQKwy2yQBAH7vcnKSLsrFyugD3NN2Mtuk3msuAX4CLsd?cluster=devnet) | 200 `{"paid": true}`; replay → 402 "signature already used" |

Full signatures:
- https://explorer.solana.com/tx/4MA5AksNHJy33wDSYGhwv7qHchVWSL1mvTnuQSQpUsBNYktP2hDZB88Q9u5x8YVnfujUANSEEfmm95i2F7Bvhter?cluster=devnet
- https://explorer.solana.com/tx/xuFer13etHE26ysT6fTXVBXSkPcKexUySv773hgybwaPr2mVkB8F3ekWquSWktnLDid3RjprdaksWNd6wejBmoQ?cluster=devnet
- https://explorer.solana.com/tx/58HkqR6nhbb1CkYFWv2dEqbcHPwCqPqGQAizaUu7shusGQKwy2yQBAH7vcnKSLsrFyugD3NN2Mtuk3msuAX4CLsd?cluster=devnet

Setup (not a paywall payment): one 0.002 SOL transfer made the brand-new payTo account rent-exempt, because a
0.0001 SOL transfer into an empty account fails with `InsufficientFundsForRent`:
https://explorer.solana.com/tx/5Unu7dSrBgt1gzY6jEC1gU9XBYVwsob86pDvAKoMKoFdFxWHVRWXouFCyyoxRz9zcREWgkhvPZyK6nV8sgNdX7s7?cluster=devnet

## Client log (run 1)
```
payer CAEpdiD4u5kLQg95RoXm33bKopuMh6RR6ZQPgdsME1vi
balance 4997995000
402 requirements {'scheme': 'exact', 'network': 'solana-devnet', 'payTo': 'DAfQDqhGReo6HrNac449XNo2pZ6zzaQ5k9sBrz95gcuy', 'asset': 'SOL', 'maxAmountRequired': '100000', 'memo': '21823bde08ad6357', 'description': 'One market quote'}
paid, signature 4MA5AksNHJy33wDSYGhwv7qHchVWSL1mvTnuQSQpUsBNYktP2hDZB88Q9u5x8YVnfujUANSEEfmm95i2F7Bvhter
200 {"symbol": "SOL", "quote": "demo-data", "paid": true}
https://explorer.solana.com/tx/4MA5AksNHJy33wDSYGhwv7qHchVWSL1mvTnuQSQpUsBNYktP2hDZB88Q9u5x8YVnfujUANSEEfmm95i2F7Bvhter?cluster=devnet
replay -> 402 signature already used
```

Demo video: `demo.mp4` (captions only), also attached to the GitHub release `demo-v1`.

## Client log (run 3 — 2026-10-19)
```
payer CAEpdiD4u5kLQg95RoXm33bKopuMh6RR6ZQPgdsME1vi
balance 4997785000
402 requirements {'scheme': 'exact', 'network': 'solana-devnet', 'payTo': 'DAfQDqhGReo6HrNac449XNo2pZ6zzaQ5k9sBrz95gcuy', 'asset': 'SOL', 'maxAmountRequired': '100000', 'memo': '776a5d1c155834f7', 'description': 'One market quote'}
paid, signature 58HkqR6nhbb1CkYFWv2dEqbcHPwCqPqGQAizaUu7shusGQKwy2yQBAH7vcnKSLsrFyugD3NN2Mtuk3msuAX4CLsd
200 {"symbol": "SOL", "quote": "demo-data", "paid": true}
https://explorer.solana.com/tx/58HkqR6nhbb1CkYFWv2dEqbcHPwCqPqGQAizaUu7shusGQKwy2yQBAH7vcnKSLsrFyugD3NN2Mtuk3msuAX4CLsd?cluster=devnet
replay -> 402 signature already used
```
