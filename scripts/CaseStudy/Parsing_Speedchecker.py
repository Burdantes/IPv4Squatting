import json
import dns.resolver as dnsres
import dns.reversename as dnsrever

# Opening JSON file
f = open('speedcheckerToSquatters.json', )

# returns JSON object as
# a dictionary
data = json.load(f)
# print(len(data))
set_of_internal_looking_ASes = []
set_of_external_looking_ASes = []
set_of_unresponsive = []
dic_val = {}

ind = 0
for t in data:
    to_keep = []
    rtt_list = []
    list_of_dns = []
    as_mapping = []
    ind +=1
    at_least_one_responsive = False
    # print(t['ASN'],t['Tracert'])
    for s in t['Tracert']:
        # print(s)
        to_keep.append(s['IP'])
        rtt_list.append(s['PingTime'])
        as_mapping.append(s['ASN'])
        # try:
        #     domain_address = dnsrever.from_address(s['IP'])
        #     dns = str(dnsres.query(domain_address, 'PTR')[0])
        #     print(dns)
        # except:
        dns = ''
        list_of_dns.append(dns)

        # list_of_dns.append(s['HostName'])
        if s['IP'] != '*':
            # print(t['ASN'],s)
            at_least_one_responsive = True
            if t['ASN'] != s['ASN']:
                # set_of_external_looking_ASes.append(t['ASN'])
                outside = True
                at_least_one_responsive = False
    if outside:
        set_of_internal_looking_ASes.append(t['ASN'])
        # dic_val[ind] = [to_keep, rtt_list, as_mapping, list_of_dns]
    elif at_least_one_responsive:
        set_of_external_looking_ASes.append(t['ASN'])
        dic_val[ind] = [to_keep, rtt_list, as_mapping,as_mapping, list_of_dns]
    else:
        set_of_unresponsive.append(t['ASN'])
    outside = False
# [to_keep, rtt_list,new_mapping,as_mapping,list_of_dns]
print(len(set(set_of_internal_looking_ASes)))
print(len(set(set_of_external_looking_ASes)))
# print(data)
print(list(set(set_of_unresponsive)))
# print(dic_val)
with open("example_of_external_speedchecker.json", 'w') as fout:
    json_dumps_str = json.dumps(dic_val)
    print(json_dumps_str, file=fout)
