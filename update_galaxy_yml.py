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


def rev_version(data, version_part='patch'):
    ver_str = data['version']

    # to preserve quoting...
    _OrigType = type(ver_str)
    ver_dict = semver.parse(ver_str)
    log.debug('ver_dict: %s', ver_dict)

    assert version_part in ('major', 'minor', 'patch')

    ver_dict[version_part] = ver_dict[version_part] + 1
    log.debug('ver_dict2: %s', ver_dict)

    # log.debug('new_ver_str: %s', new_ver_str)
    new_ver_str = semver.format_version(**ver_dict)
    log.debug('new_ver_str: %s', new_ver_str)

    data['version'] = _OrigType(new_ver_str)
    return data


def keywords_to_tags(data):
    keywords = data.get('keywords', None)
    if not keywords:
        return data

    tags = data.get('tags', [])

    for keyword in keywords:
        # _OrigType = type(keyword)
        log.debug('Changing keyword "%s" to tag "%s"', keyword, keyword)

        if keyword not in tags:
            tags.append(keyword)

    data['tags'] = tags
    del data['keywords']
    log.debug('new tags: %s', tags)
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

        rev_version(data)

        log.debug('a: %s', data['version'])

        keywords_to_tags(data)

        ruamel.yaml.round_trip_dump(data, sys.stdout, block_seq_indent=2)

    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(process)d %(name)s %(funcName)s:%(lineno)d - %(message)s')
    sys.exit(main())
