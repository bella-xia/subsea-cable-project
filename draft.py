from ipwhois.net import Net
from ipwhois.asn import IPASN
from pprint import pprint


net = Net('195.66.236.146')
obj = IPASN(net)
results = obj.lookup()
print(results)
