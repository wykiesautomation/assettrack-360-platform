REV04: SIM7000G active profile decommissioned for this backend.
Removed SIM7000G profile module, active registry entry, public card registration,
alias and legacy runtime profile lookup. SIM800L module remains unchanged.
Existing database records are NOT renamed, deleted or converted automatically.
Explicit admin repair remains available and now recognizes historical SIM7000G
records without loading a removed profile. UID/token/history remain unchanged.
Old SIM7000G codes no longer resolve to an active profile; generate a new SIM800L
code for unregistered boards, or use explicit repair for existing records.
This is NOT a simple name replacement: SIM800L capabilities/pins stay separate.
Historical references in docs, template branches, UID-prefix maps and repair
code remain. Board Builder and firmware are NOT changed by this backend pack.
Therefore complete removal from ALL software is NOT finished in this release.
Deploy to assettrack-360-platform/main. Overlay uploader does not delete absent
files remotely; the removed module may remain on disk but is no longer imported.
Static Python checks only; no full startup, database, browser or hardware tests.
