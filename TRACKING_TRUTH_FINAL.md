# AssetTrack 360 Tracking Truth Final

Tracking History and Trips now use one shared authoritative GPS truth model. A stationary phone inside one accuracy-aware cluster returns zero distance, zero validated speed and zero movement time. Stationary observations are counted as STATIONARY_DRIFT and elapsed time remains stopped time. Explicit Start/Stop trip identities remain authoritative. Possible addresses and exact coordinates remain display-only and never influence movement calculations.
