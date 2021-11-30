# 1. Remove loops
# 2. Replace empty ASNs between 2 of the same ASN
import unittest
#import np # possibly needed for jupyter notebook

class ASPathSanitizer(object):

    def __init__(self, missing_ip_char = ''):
        self.missing_ip_char = missing_ip_char

    def fix(self, src_asn, dst_asn, path_hops, delim=','):
        if not src_asn or not dst_asn or not path_hops:# or np.isnan(src_asn) or np.isnan(dst_asn): sometimes needed in jupyter notebook
            return ''

        fixed_list = self.fix_aslist(src_asn, dst_asn, path_hops)

        return delim.join(fixed_list)

    def fix_aslist(self, src_asn, dst_asn, path_hops):
        if not src_asn or not dst_asn or not path_hops:
            return []

        noloops = self.fix_loops(src_asn, dst_asn, path_hops)
        noempty = self.fix_empty(src_asn, dst_asn, noloops)

        return noempty

    def fix_empty(self, source_asn, dest_asn, path_hops):

        path_len = len(path_hops)

        if path_hops[0] == self.missing_ip_char:
            path_hops[0] = source_asn
        if path_hops[-1] == self.missing_ip_char:
            path_hops[-1] = dest_asn

        i = 1
        last_asn = path_hops[0]

        while i < path_len:

            if path_hops[i] != self.missing_ip_char:
                last_asn = path_hops[i]
                i += 1
                continue

            # Found empty ASN
            # Scan until we find a non empty ASN or run off the end of the array
            j = i + 1
            while j < path_len and path_hops[j] == self.missing_ip_char:
                j += 1

            if j == path_len: # Hit end of the array so exit
                break

            next_asn = path_hops[j]
            if next_asn == last_asn:
                for k in range(i, j+1): # set ASN from i to j
                    path_hops[k] = last_asn

            i = j

        return path_hops

    def fix_loops(self, source_asn, dest_asn, path_hops):

        path_len = len(path_hops)

        if path_hops[0] == self.missing_ip_char:
            path_hops[0] = source_asn
        if path_hops[-1] == self.missing_ip_char:
            path_hops[-1] = dest_asn

        last_indexes = {}

        previous_asn = path_hops[0]
        last_indexes[previous_asn] = 0

        for i in range(1, path_len):
            asn = path_hops[i]

            if asn == self.missing_ip_char:
                continue

            last_indexes[asn] = i

        for i in range(1, path_len):
            asn = path_hops[i]

            if asn == self.missing_ip_char:
                continue

            if asn != previous_asn and i < last_indexes[previous_asn]: # loop detected
                path_hops[i] = previous_asn
            else:
                previous_asn = asn

        return path_hops

class ASPathSanitizerTest(unittest.TestCase):

    def test_fixempty_good(self):
        path = ["15776","","","15776","8220","","8220","","","8075"]

        expected_path = ["15776","15776","15776","15776","8220","8220","8220","","","8075"]

        path_fixer = ASPathSanitizer("")
        new_path = path_fixer.fix_empty("15776", "8075", path)

        self.assertEqual(expected_path, new_path)

    def test_fixempty_good2(self):
        asn_str = "97809|197809|3257|3257|6453|6453|6453|6453|6453|6453|6453|6453|6453|*|45102|*|*|*|*|*|*|*|45102"
        asn_path = asn_str.split('|')

        path_fixer = ASPathSanitizer("*")
        new_path = path_fixer.fix_empty("197809", "45102", asn_path)
        
        expected_path = ["97809","197809","3257","3257","6453","6453","6453","6453","6453","6453","6453","6453","6453","*","45102","45102","45102","45102","45102","45102","45102","45102","45102"]

        self.assertEqual(expected_path, new_path)

    def test_fixempty_lastempty(self):

        path = ["15776","","","15776","8220","","8220","",""]

        expected_path = ["15776","15776","15776","15776","8220","8220","8220","","8075"]

        path_fixer = ASPathSanitizer("")
        new_path = path_fixer.fix_empty("15776", "8075", path)

        self.assertEqual(expected_path, new_path)

    def test_fixempty_allempty(self):
        path = ["", "", "", ""]
        expected_path = ["15776", "", "", "8075"]

        path_fixer = ASPathSanitizer()
        new_path = path_fixer.fix_empty("15776", "8075", path)

        self.assertEqual(expected_path, new_path)

    def test_fixloops_good(self):
        path = ["15776","","1234","15776",""]

        expected_path = ["15776","","15776","15776","8075"]

        path_fixer = ASPathSanitizer()
        new_path = path_fixer.fix_loops("15776", "8075", path)

        self.assertEqual(expected_path, new_path)

    def test_fixloops_noloop(self):
        path = ["15776","1234","12345","",""]
        expected_path = ["15776","1234","12345","","8075"]

        path_fixer = ASPathSanitizer()
        new_path = path_fixer.fix_loops("15776", "8075", path)

        self.assertEqual(expected_path, new_path)

    def test_fix_withstar(self):
        path = ["15776","*","15777","15776","8220","*","8220","*","*","8076"]

        expected_path = ["15776","15776","15776","15776","8220","8220","8220","*","*","8076"]

        path_fixer = ASPathSanitizer("*")
        new_path = path_fixer.fix("15776", "8075", path)

        self.assertEqual(",".join(expected_path), new_path)

if __name__ == '__main__':
    unittest.main()