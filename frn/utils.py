import re
import random


def parse_dict(line):
    args = {}
    for (key, value) in re.findall(r'<([A-Za-z]+)>(.*?)</\1>', line):
        args[key] = value.strip()
    return args


def serialize_dict(data):
    result = ''
    for key, value in data:
        result += '<%s>%s</%s>' % (key, value, key)
    return result


def generate_challenge():
    return '%08d' % random.randint(0, 99999999)


def solve_challenge(challenge):
    if len(challenge) != 8 or not challenge.isdigit():
        return None
    a = int(challenge[6] + challenge[4]) + int(challenge[0] + challenge[7]) + 5
    b = int(challenge[2] + challenge[1]) + int(challenge[5] + challenge[3]) + 11
    c = '%05d' % (a * b)
    return (c[3] + c[0] + c[2] + c[4] + c[1])
