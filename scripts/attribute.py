import unittest
import util

squatspace_trie = util.load_squatspace_default()


def find_hops_around(path, squat_index):
    '''
    This function returns the closest hops around squat_index that are not *.
    If none is found, return *.
    '''
    before_hop = '*'  # the closest hop before the squat hop
    after_hop = '*'  # the closest hop after the squat hop
    for i in range(1, len(path)):
        before_idx = squat_index - i
        after_idx = squat_index + i
        if before_idx < 0 and after_idx >= len(path):
            # this means we go through all nearby hops
            break
        if before_idx >= 0 and path[before_idx] != '*' and before_hop == '*':
            before_hop = path[before_idx]
        if after_idx < len(path) and path[after_idx] != '*' and after_hop == '*':
            after_hop = path[after_idx]
    return before_hop, after_hop


def attribute_squatter(before_hop, after_hop, known_squatters,
                       ip_occurrence_count_second_pass, ip_set_second_pass, ip,
                       at_least_one, tr_count_second_pass):
    '''
    This function attribute the ip to before/after hop if one of them has been observed using this squat prefix (not both), and update counters.
    The squatter to which the ip is attributed is returned (* if it cannot be attributed)
    '''
    squatter = '*'
    trie_search = squatspace_trie.search_best(ip)
    if trie_search is None:
        # this should not happen if the same squat prefixes are used 
        # in tr_pathfix.py and here.
        # Look at line 18 in utils.py and see which unannounced.txt is used.
        raise AssertionError()
    squat_prefix = trie_search.prefix
    if squat_prefix in known_squatters:
        known_squatters_for_this_prefix = known_squatters[squat_prefix]
    else:
        # empty, no one has been observed squatting this prefix
        known_squatters_for_this_prefix = set()
    if (before_hop in known_squatters_for_this_prefix) != (after_hop in known_squatters_for_this_prefix):
        squatter = before_hop if before_hop in known_squatters_for_this_prefix else after_hop
        ip_occurrence_count_second_pass += 1
        ip_set_second_pass.add(ip)
        if not at_least_one:
            tr_count_second_pass += 1
            at_least_one = True
    return squatter, ip_occurrence_count_second_pass, ip_set_second_pass, \
        at_least_one, tr_count_second_pass


class AttributeTest(unittest.TestCase):
    def test_find_hops_around(self):
        path = ['*', 'org1', '*', '*', '*', 'org2', '*']
        squat_index = 2
        bh, ah = find_hops_around(path, squat_index)
        self.assertEqual(bh, 'org1')
        self.assertEqual(ah, 'org2')

    def test_find_hops_around2(self):
        path = ['org0', 'org1', '*', '*', '*', '*', '*']
        squat_index = 2
        bh, ah = find_hops_around(path, squat_index)
        self.assertEqual(bh, 'org1')
        self.assertEqual(ah, '*')

    def test_attribute_squatter(self):
        # attributable
        known_squatters = {'6.0.0.0/15': {'org1'}, '7.0.0.0/8': {'org2'}}
        before_hop = 'org1'
        after_hop = 'org3'
        ip_occurrence_count_second_pass = 0
        ip_set_second_pass = set()
        ip = '6.0.0.1'
        at_least_one = False
        tr_count_second_pass = 0
        squatter, ip_occurrence_count_second_pass, ip_set_second_pass, \
            at_least_one, tr_count_second_pass = attribute_squatter(
                before_hop, after_hop, known_squatters,
                ip_occurrence_count_second_pass, ip_set_second_pass,
                ip, at_least_one, tr_count_second_pass
            )
        self.assertEqual(squatter, 'org1')
        self.assertEqual(ip_occurrence_count_second_pass, 1)
        self.assertEqual(tr_count_second_pass, 1)
        self.assertEqual(ip in ip_set_second_pass, True)

    def test_attribute_squatter2(self):
        # attributable
        known_squatters = {'6.0.0.0/15': {'org1'}, '7.0.0.0/8': {'org2'}}
        before_hop = 'org1'
        after_hop = 'org3'
        ip_occurrence_count_second_pass = 0
        ip_set_second_pass = set()
        ip = '9.0.0.1'
        at_least_one = False
        tr_count_second_pass = 0
        squatter, ip_occurrence_count_second_pass, ip_set_second_pass, \
            at_least_one, tr_count_second_pass = attribute_squatter(
                before_hop, after_hop, known_squatters,
                ip_occurrence_count_second_pass, ip_set_second_pass,
                ip, at_least_one, tr_count_second_pass
            )
        self.assertEqual(squatter, '*')
        self.assertEqual(ip_occurrence_count_second_pass, 0)
        self.assertEqual(tr_count_second_pass, 0)
        self.assertEqual(ip in ip_set_second_pass, False)


if __name__ == '__main__':
    unittest.main()
