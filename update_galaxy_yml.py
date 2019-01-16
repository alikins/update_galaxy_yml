#!/usr/bin/env python

# needs old ruamel.yaml to preserve order/comments/quotes
# pip install 'ruamel.yaml<0.15'

import logging
import os
import sys

import ruamel.yaml
import semver

log = logging.getLogger(__name__)


# sideeffect modifies data in place
def update_name(data):
    old_name = data['name']

    if '.' not in old_name or 'namespace' in data:
        return data

    _OrigType = type(old_name)
    parts = old_name.split('.', 1)

    # name = ruamel.yaml.scalarstring.DoubleQuotedScalarString(parts[1])
    name = _OrigType(parts[1])

    # namespace = ruamel.yaml.scalarstring.DoubleQuotedScalarString(parts[0])
    namespace = _OrigType(parts[0])

    data['name'] = name

    # insert namespace attr first
    data.insert(0, 'namespace', namespace)

    # but note it's already modified in place
    return data


def rev_major_version(data):
    ver_str = data['version']

    # to preserve quoting...
    _OrigType = type(ver_str)
    # ver = semver.parse_version_info(ver_str)
    new_ver_str = semver.bump_major(ver_str)

    data['version'] = _OrigType(semver.parse_version_info(new_ver_str))
    return data


def main():
    log.debug('sys.argv: %s', sys.argv)
    args = sys.argv[1:]
    for arg in args:
        fo = open(arg, 'r')
        # data = yaml.load(fo)
        data = ruamel.yaml.round_trip_load(fo, preserve_quotes=True)

        update_name(data)

        log.debug('b: %s', data['version'])

        rev_major_version(data)

        log.debug('a: %s', data['version'])

        ruamel.yaml.round_trip_dump(data, sys.stdout, block_seq_indent=2)

    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(process)d %(name)s %(funcName)s:%(lineno)d - %(message)s')
    sys.exit(main())
