import re

def parse_arguments(line):
    args = {}
    for (key, value) in re.findall(r'<([A-Z]+)>(.*?)</\1>', line):
        args[key] = value.strip()
    return args
