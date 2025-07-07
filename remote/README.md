## Script spec

### remote/gen_meta.py
**dependencies**
- CAIDA ark measurement data located at '/data/topology/ark/data/team-probing/list-7.allpref24/team-1/2024/[measurement date]'
- metadata on each country code's associated continent, subregion, and intermediate region

**accepted aruments**
- `--directory` [*default='/data/topology/ark/data/team-probing/list-7.allpref24/team-1/2024'*] the directory that stores all CAIDA ARK traceroute probes
- `--meta_dir [*default='data/iso-3166-countries-with-regional-codes.csv'*] 

**outputs**
