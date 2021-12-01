import fileinput
new_link_bdrmapIT = []
total_link_bdrmapIT = []
for line in fileinput.input("output_res_bdrmapIT.txt"):
    line = line.strip()
    print(line)

    src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str = line.split(
        '	')
    print(line)
    squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
    hop_ips = [ip for ip in hop_ips_str.split('|')]
    fixed_asn_path = [asn for asn in fixed_asn_path_str.split('|')]
    fixed_org_path = [org for org in fixed_org_path_str.split('|')]
    better_org_path = [org for org in better_org_path_str.split('|')]
    rir_org_path = [org for org in rir_org_path_str.split('|')]
    for i in range(0,len(fixed_asn_path)-1):
        if fixed_asn_path[i] != fixed_asn_path[i+1]:
            total_link_bdrmapIT.append((fixed_asn_path[i],fixed_asn_path[i+1]))
    for index in squat_indexes:
        print(fixed_asn_path[index])
        if fixed_org_path[index] != rir_org_path[index]:
            continue
        if index > 0:
            if fixed_asn_path[index] != fixed_asn_path[index-1]:
                if fixed_asn_path[index] != '*' and fixed_asn_path[index-1] != '*':
                    new_link_bdrmapIT.append((fixed_asn_path[index-1],fixed_asn_path[index]))
        if index < len(fixed_asn_path)-1:
            if fixed_asn_path[index] != fixed_asn_path[index+1]:
                if fixed_asn_path[index] != '*' and fixed_asn_path[index+1] != '*':
                    new_link_bdrmapIT.append((fixed_asn_path[index],fixed_asn_path[index+1]))
print(len(set(new_link_bdrmapIT)))
print(len(set(total_link_bdrmapIT)))