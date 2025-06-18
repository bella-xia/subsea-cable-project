import geoip2.database
import argparse



if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-q', '--query', required=True)
    parser.add_argument('--database', type=str, default='data/GeoLite2-Country.mmdb')

    args = parser.parse_args()

    try:
        with geoip2.database.Reader(args.database) as reader:
            response = reader.country(args.query)
            print('queried ip:' , args.query)
            print('country name:', response.country.name)
            print('cuntry iso code:', response.country.iso_code)
    except geoip2.errors.AddressNotFoundError:
        print(f'unable to find ip address {args.query}')
    except Exception as e:
        print(f'received exception during query: {str(e)}')
  
