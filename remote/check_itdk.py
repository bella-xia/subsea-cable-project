import maxminddb as mmdb

with mmdb.open_database('data/itdk_formatted.mmdb') as reader:
    print(reader.get('151.2.211.121'))
    print(reader.get('1.1.1.1'))
