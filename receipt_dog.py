#!/usr/bin/env python3
"""receipt-dog: receipt-driven triage harness.

Every unit of work arrives as a receipt (a JSON event). The dog sniffs each
one, checks it against the last known-good state, stamps it PASS or FAIL,
and nudges failures onto a reroute spur instead of losing them.

Demo: python3 receipt_dog.py demo
Run:  python3 receipt_dog.py run INBOX_DIR PASSED_DIR REROUTE_DIR LEDGER.jsonl
"""
import json, sys, time, hashlib, pathlib

def sniff(receipt: dict) -> tuple[bool, str]:
    """Check a receipt the way a collie checks sheep: calmly, one at a time."""
    if not isinstance(receipt, dict):
        return False, "not a receipt"
    for field in ("id", "kind", "payload"):
        if field not in receipt:
            return False, f"missing field: {field}"
    if not isinstance(receipt["payload"], dict):
        return False, "payload must be an object"
    if receipt.get("seal") is not None:
        expect = hashlib.sha256(
            json.dumps(receipt["payload"], sort_keys=True).encode()
        ).hexdigest()[:16]
        if receipt["seal"] != expect:
            return False, f"seal mismatch (want {expect})"
    return True, "ok"

def run(inbox: pathlib.Path, passed: pathlib.Path, reroute: pathlib.Path, ledger: pathlib.Path) -> dict:
    counts = {"pass": 0, "fail": 0}
    with ledger.open("a") as log:
        for f in sorted(inbox.glob("*.json")):
            try:
                receipt = json.loads(f.read_text())
            except Exception as e:
                receipt, err = {}, f"unreadable: {e}"
            else:
                err = None
            ok, why = (False, err) if err else sniff(receipt)
            stamp = {"id": receipt.get("id", f.stem), "stamp": "PASS" if ok else "FAIL",
                     "why": why, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
            log.write(json.dumps(stamp) + "\n")
            dest = (passed if ok else reroute) / f.name
            f.replace(dest)
            counts["pass" if ok else "fail"] += 1
            print(f"{'PASS' if ok else 'FAIL'}  {f.name}: {why}")
    return counts

def demo():
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp(prefix="receipt-dog-demo-"))
    inbox, passed, reroute = d/"inbox", d/"passed", d/"reroute"
    for p in (inbox, passed, reroute): p.mkdir()
    good = {"id": "r1", "kind": "build", "payload": {"rounds": 57}}
    good["seal"] = hashlib.sha256(json.dumps(good["payload"], sort_keys=True).encode()).hexdigest()[:16]
    bad  = {"id": "r2", "kind": "build", "payload": {"rounds": 57}, "seal": "tampered"}
    ugly = {"kind": "build", "payload": {}}
    for i, r in enumerate((good, bad, ugly)):
        (inbox / f"receipt-{i}.json").write_text(json.dumps(r))
    counts = run(inbox, passed, reroute, d/"ledger.jsonl")
    print(f"\npen counts: {counts}  (ledger: {d}/ledger.jsonl)")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "demo":
        demo()
    elif len(sys.argv) == 5:
        run(*(pathlib.Path(a) for a in sys.argv[1:4]), pathlib.Path(sys.argv[4]))
    else:
        print(__doc__)
