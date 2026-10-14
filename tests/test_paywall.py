import base64, json, threading, unittest, urllib.request, urllib.error
from http.server import HTTPServer
from paywall import server as s

def fake_tx(delta, nonce, err=None):
    return lambda m, p: {"meta": {"err": err, "preBalances": [5_000_000, 0], "postBalances": [0, delta],
            "logMessages": [f"Program log: Memo: {nonce}"]},
            "transaction": {"message": {"accountKeys": [{"pubkey": "payer"}, {"pubkey": s.PAY_TO}]}}}

class T(unittest.TestCase):
    def test_verify(self):
        n = s.requirements()["nonce"]
        self.assertEqual(s.verify_payment("sig1", n, fake_tx(10, n))[1], "insufficient amount")
        self.assertTrue(s.verify_payment("sig1", n, fake_tx(s.PRICE, n))[0])
        self.assertEqual(s.verify_payment("sig1", n, fake_tx(s.PRICE, n))[1], "signature already used")
    def test_http_flow(self):
        srv = HTTPServer(("127.0.0.1", 0), s.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{srv.server_port}/quote?symbol=SOL"
        with self.assertRaises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(url)
        self.assertEqual(e.exception.code, 402)
        nonce = json.loads(e.exception.read())["nonce"]
        s.H.fetch = staticmethod(fake_tx(s.PRICE, nonce))
        hdr = base64.b64encode(json.dumps({"signature": "sig2", "nonce": nonce}).encode()).decode()
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"X-PAYMENT": hdr}))
        self.assertEqual(json.loads(r.read())["paid"], True); srv.shutdown()
if __name__ == "__main__":
    unittest.main()
