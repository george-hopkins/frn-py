import pytest
from frn.utils import *


def test_parse_dict():
    expected = {'OM': '', 'A': 'foo'}
    actual = parse_dict('<OM></OM><A>test</A><A>foo</A>')
    assert(expected == actual)


def test_serialize_dict():
    expected = '<A>first</A><BB>second</BB>'
    actual = serialize_dict([
        ('A', 'first'),
        ('BB', 'second'),
    ])
    assert(expected == actual)
