from frn.utils import *

def test_parse_arguments():
    expected = {'OM': '', 'A': 'foo'}
    actual = parse_arguments('<OM></OM><A>test</A><A>foo</A>')
    assert(expected == actual)
