import sys
import radix

if __name__ == '__main__':

    if len(sys.argv) != 3:
        sys.stderr.write('usage: <whois> <ip>\n')
        sys.exit(1)

    whois_file = sys.argv[1]
    ip = sys.argv[2].strip()

    trie = radix.Radix()

    with open(whois_file) as f:
        for line in f:
            line = line.strip()

            chunks = line.split('\t')
            prefix = chunks[1]
            org = chunks[4]

            node = trie.add(prefix)

            if "lines" not in node.data:
                node.data["lines"] = []
            
            node.data["lines"].append(line)

    node = trie.search_best(ip)
    if node:
        for line in node.data['lines']:
            print(line)
    else:
        print('no match')

    