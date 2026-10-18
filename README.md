# receipt-dog
A herding dog that works a conveyor of paper parcels: sniffs each one, stamps what passes, nudges what fails onto a reroute spur.
- Animal behavior: border collie herding - eye, stalk, flank, shed (separate one animal from the group without panic).
- Fleet mechanism: receipt-driven triage. Every unit of work arrives as a receipt; the harness checks it against the last known-good, stamps it, and routes failures to a retry lane instead of losing them.
- Proof of life: Prompt Poetry ep1 (Count, Compare, Change) - the dog is the loop made visible: https://youtube.com/shorts/D6pVWMMc4Ag

## Run it
```
python3 receipt_dog.py demo
```

## The loop
1. Sniff - each receipt is validated: required fields, payload shape, seal hash.
2. Stamp - a pass goes to the passed lane and into the ledger (JSONL).
3. Reroute - a fail goes to the spur with its reason. Nothing is dropped, nothing is retried blind.

## Facts
- One file, 3,074 bytes, Python standard library only.
- Status: v0.1, public.

Part of the HERDR animal-harness series: https://github.com/drewbeyersdorf/herd-mind
