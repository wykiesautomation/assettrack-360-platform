AssetTrack 360 LILYGO T-SIM7600E V1.3 correction

Corrected the uploaded T-SIM7000G placeholder to the photographed LILYGO T-SIM7600E V1.3 / PCB 20200310 / SIM7600E board.
Added canonical profile AT360_LILYGO_T_SIM7600E_V13 and UID prefix AT360-TSIM7600E-.
Preserved a profile alias and legacy device-type map so an unpublished T-SIM7000G selection can resolve safely to the corrected profile.
Added Arduino firmware under firmware/AT360_LILYGO_T_SIM7600E_V13.
No existing ESP32D, ESP32-WROOM-32 or SIM808 profile was replaced.
No customer GPIO outputs are exposed.
