#!/usr/bin/env python

# Author: Andrea Barberio <insomniac@slackware.it>
# License: 3-clause BSD

# This simple script fetches a partition list and saves it as JSON and as a C
# function.
# Usage: ./partitions.py
#

import re
import json
import urllib
import collections


partitions_url = 'http://www.win.tue.nl/~aeb/partitions/partition_types-1.html'
partlist_url = 'https://github.com/insomniacslk/partlist'
rx = re.compile(r'^<DT><B>(?P<code>[0-9a-f]{2})  (?P<name>.+)</B><DD>$')


def fetch_partitions():
    print('Fetching {}'.format(partitions_url))
    return urllib.urlopen(partitions_url).read()


def parse_partitions(data):
    print('Parsing partitions')
    partitions = collections.defaultdict(list)
    for line in data.splitlines():
        match = rx.match(line)
        if match:
            mdict = match.groupdict()
            code = int(mdict['code'], 16)
            name = mdict['name']
            partitions[code].append(name)
    return partitions


def simple_quote(s):
    return s.replace('"', '\\"').replace("'", "\\'")


def to_json(partitions):
    with open('partitions.json', 'w') as fd:
        json.dump(partitions, fd, indent=4)
        print('Saved to partitions.json')


def to_c(partitions):
    with open('partitions.c', 'w') as fd:
        fd.write('/* Generated with partlist <{url}> */\n'.format(
            url=partlist_url))
        fd.write('/* Original data source: {url} */\n'.format(
            url=partitions_url))
        fd.write('const char *get_partition_type(unsigned char ptype) {\n')
        fd.write('\n')
        fd.write('    switch (ptype) {\n')
        for part_id, part_names in partitions.iteritems():
            part_names = simple_quote(', '.join(part_names))
            fd.write('    case {part_id}:\n'.format(part_id=part_id))
            fd.write('        return "{part_names}";\n'.format(
                part_names=part_names))
        fd.write('    default:\n')
        fd.write('        return "Unknown partition type";\n')
        fd.write('    }\n')
        fd.write('}\n')
        print('Saved to partitions.c')


def main():
    data = fetch_partitions()
    partitions = parse_partitions(data)
    to_json(partitions)
    to_c(partitions)


if __name__ == '__main__':
    main()
