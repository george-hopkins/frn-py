import re


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
