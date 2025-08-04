import argparse, ipaddress
import maxminddb as mmdb

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
        if not asn_data:
            geolite_asn_number = 'unknown'
            geolite_asn_name = 'unknown'
            geolite_network = None
        else:
            geolite_asn_number = asn_data['autonomous_system_number'] if asn_data.get('autonomous_system_number', None) else 'unknown'
            geolite_asn_name = asn_data['autonomous_system_organization'] if asn_data.get('autonomous_system_organization', None) else 'unknown'
            geolite_network = ipaddress.ip_network(f'{args.ip}/{prefix}', strict=False)

    with mmdb.open_database(args.geolite_geo_db) as reader:
        city_data = reader.get(args.ip)
        geolite_city_name = city_data['city']['names']['en'] if city_data.get('city', None) else 'unknown'
        geolite_country_name = city_data['country']['names']['en'] if city_data.get('country', None) else 'unknown'
        print(city_data['country'])
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

    if args.query:
        queries = set([args.query])
    else:
        queries = set(['who-is', 'where-is'])
    print('')
    if 'who-is' in queries:
        try:
            print('WHO IS', args.ip)
            if geolite_network:
                print('CIDR:', geolite_network, '(MaxMind)')
                print('min ip:', geolite_network.network_address, ' max ip:', geolite_network.broadcast_address, '(MaxMind)')
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
      
