# AssetTrack 360 Stationary Drift Final Fix

- Explicit Start/Stop trip identity remains authoritative.
- A phone remaining inside one accuracy-aware stationary cluster records zero distance and zero validated speed.
- Isolated Android speed spikes are not accepted as movement.
- Movement requires accuracy-cleared displacement plus adjacent confirmation, or decisive displacement beyond the uncertainty envelope.
- Stationary duration is retained as stopped time.
- A stationary trip remains visible without drawing a tangled route.
- Legacy tracking without explicit trip identity remains conservatively supported.
