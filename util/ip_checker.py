import argparse, ipaddress
import maxminddb as mmdb

def check_homogeneous_geolocation(network, geolite_reader, ipinfo_reader, sample_ratio = 0.01):
    total_ips = network.num_addresses
    num_samples = total_ips * sample_ratio
    step = max(total_ips // num_samples, 1)
    city_counts = set()
    country_counts = set()
    geoloc_counts = set()
    for i, ip in enumerate(network):
        if i % step == 0 or i == total_ips - 1:
        
            city_data = geolite_reader.get(args.ip)
            country_data = ipinfo_reader.get(args.ip)
            if not city_data:
                continue
            city_name = city_data['city']['names']['en'] if city_data.get('city', None) else 'unknown'
            country_name = city_data['country']['names']['en'] if city_data.get('country', None) else 'unknown'
            ipinfo_country_name = country_data.get('country', 'unknown')
            latitude = city_data['location']['latitude'] if city_data.get('location', None) else 'unknown'
            longitude = city_data['location']['longitude'] if city_data.get('location', None) else 'unknown'
            city_counts.add(f'{city_name}, {country_name}')
            country_counts.add(f'{ipinfo_country_name}')
            geoloc_counts.add(f'({latitude:.2f},{longitude:.2f})')
    print(city_counts)
    print(country_counts)
    print(geoloc_counts)
    return (len(city_counts) == 1), (len(geoloc_counts) == 1), (len(country_counts) == 1)


if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-q', '--query', type=str, default=None)
    parser.add_argument('--ip', type=str, required=True)
    parser.add_argument('--geolite_geo_db', type=str, default='data/GeoLite2-City.mmdb')
    parser.add_argument('--geolite_asn_db', type=str, default='data/GeoLite2-ASN.mmdb')
    parser.add_argument('--ipinfo_db', type=str, default='data/ipinfo_lite.mmdb')
    args = parser.parse_args()
    
    with mmdb.open_database(args.geolite_asn_db) as reader:
        asn_data, prefix = reader.get_with_prefix_len(args.ip)
        geolite_asn_number = asn_data['autonomous_system_number'] if asn_data.get('autonomous_system_number', None) else 'unknown'
        geolite_asn_name = asn_data['autonomous_system_organization'] if asn_data.get('autonomous_system_organization', None) else 'unknown'
        geolite_network = ipaddress.ip_network(f'{args.ip}/{prefix}', strict=False)

    with mmdb.open_database(args.geolite_geo_db) as reader:
        city_data = reader.get(args.ip)
        geolite_city_name = city_data['city']['names']['en'] if city_data.get('city', None) else 'unknown'
        geolite_country_name = city_data['country']['names']['en'] if city_data.get('country', None) else 'unknown'
        geolite_continent_name = city_data['continent']['names']['en'] if city_data.get('continent', None) else 'unknown'
        geolite_subdivision_name = ', '.join(inst['names']['en'] for inst in city_data['subdivisions']) if city_data.get('subdivisions', None) else 'unknown'
        geolite_latitude = city_data['location']['latitude'] if city_data.get('location', None) else 'unknown'
        geolite_longitude = city_data['location']['longitude'] if city_data.get('location', None) else 'unknown'

    with mmdb.open_database(args.ipinfo_db) as reader:
        ipinfo_data = reader.get(args.ip)
        ipinfo_asn_domain = ipinfo_data['as_domain'] if ipinfo_data.get('as_domain', None) else 'unknown'
        ipinfo_asn_name = ipinfo_data['as_name'] if ipinfo_data.get('as_name', None) else 'unknown'
        ipinfo_asn_number = ipinfo_data['asn'] if ipinfo_data.get('asn', None) else 'unknown'
        ipinfo_continent_name = ipinfo_data['continent'] if ipinfo_data.get('continent', None) else 'unknown'
        ipinfo_country_name = ipinfo_data['country'] if ipinfo_data.get('country', None) else 'unknown'

    with mmdb.open_database(args.geolite_geo_db) as geolite_reader:
        with mmdb.open_database(args.ipinfo_db) as ipinfo_reader:

            geolite_homocity, geolite_homoloc, ipinfo_homocountry = check_homogeneous_geolocation(geolite_network, geolite_reader, ipinfo_reader)
            
    if args.query:
        queries = set([args.query])
    else:
        queries = set(['who-is', 'where-is'])
    print('')
    if 'who-is' in queries:
        try:
            print('WHO IS', args.ip)
            print('CIDR:', geolite_network, '(MaxMind)')
            print('min ip:', geolite_network.network_address, ' max ip:', geolite_network.broadcast_address, '(MaxMind)')
            print('homogeneous city:', geolite_homocity, 'homogeneous location:', geolite_homoloc, '(MaxMind)')
            print('homogeneous country:', ipinfo_homocountry, '(IPInfo)')
            print('asn:', geolite_asn_number, '(MaxMind),', ipinfo_asn_number, '(IpInfo)')
            print('asn name:', geolite_asn_name, '(MaxMind),', ipinfo_asn_name, '(IpInfo)')
            print('asn domain:', ipinfo_asn_domain, '(IpInfo)')
            print('')
        except Exception as e:
            print(f'received exception during query: {str(e)}')

    if 'where-is' in queries:
        try:
                print('WHERE IS' , args.ip)
                print('continent:', geolite_continent_name, '(MaxMind),', ipinfo_continent_name, '(IpInfo)')
                print('country:', geolite_country_name, '(MaxMind),', ipinfo_country_name, '(IpInfo)')
                print('city:', geolite_city_name, '(MaxMind)')
                print('subdivisions:', geolite_subdivision_name, '(MaxMind)')
                print('(latitude, longitude):', geolite_latitude, geolite_longitude, '(MaxMind)')
                print('')
        except Exception as e:
            print(f'received exception during query: {str(e)}')
      
