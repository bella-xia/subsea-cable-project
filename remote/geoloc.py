import requests, argparse

IPINFO_API = '1c6343782ce34e'
IPINFO_URL = 'https://api.ipinfo.io/lite'


if __name__ == '__main__':

    parser= argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default='8.8.8.8')

    args = parser.parse_args()

    print()
    response = requests.get(f"{IPINFO_URL}/{args.query}?token={IPINFO_API}")
    print(response.status_code)
    print(response.text)

