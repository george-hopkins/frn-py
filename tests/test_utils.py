import pytest
from frn.utils import *


challenge_samples = [
    ('00000011', '70160'),
    ('00000100', '00150'),
    ('10000000', '60150'),
    ('16777215', '10284'),
    ('99999999', '24472'),
]


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


def test_generate_challenge():
    challenge = generate_challenge()
    assert(re.match('^[0-9]{8}$', challenge))


@pytest.mark.parametrize("challenge, expected", challenge_samples)
def test_solve_challenge(challenge, expected):
    actual = solve_challenge(challenge)
    assert(expected == actual)
