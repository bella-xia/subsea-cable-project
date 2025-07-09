## Script spec

### util/ip_checker.py
**dependencies**
- MaxMind and IpInfo IP database

**accepted arguments**
- `--query` [*default=None*] specifies what information to output. accepted input include 'who-is' (ASN info) and 'where-is'
(geolocation info). defaults None into showing both.
- `--ip` [*required*] the IP address of interest
- `--geolite_geo_db` [*default='data/GeoLite2-City.mmdb'*] file path to MaxMind Geolocation database
- `--geolite_asn_db` [*default='data/GeoLite2-ASN.mmdb'*] file path to MaxMind ASN database
- `--ipinfo_db` [*default='data/ipinfo_lite.mmdb*] file path to IpINFO database

**outputs**
- stdout aggregated info on IP address CIDR, AS-related info, geolocation-related info
