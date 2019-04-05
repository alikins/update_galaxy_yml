#!/usr/bin/env python

# needs old ruamel.yaml to preserve order/comments/quotes
# pip install 'ruamel.yaml<0.15'

import logging
import sys

import ruamel.yaml
import semantic_version

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
    version = semantic_version.Version(ver_str)
    version_just_v = semantic_version.Version('%s.%s.%s' % (version.major, version.minor, version.patch))

    version2 = semantic_version.Version(ver_str)
    # ver_dict = semver.parse(ver_str)
    # log.debug('ver_dict: %s', ver_dict)
    log.debug('version: %s', version)
    log.debug('version sans prerelease and build: %s', version_just_v)

    assert version_part in ('major', 'minor', 'patch')

    old_build = version.build
    old_pre = version.prerelease

    # So we rev the version part, just rounding/truncating to existing ver
    if old_build or old_pre:
        version2 = version_just_v

    if version_part == 'major':
        version2 = version2.next_major()
    elif version_part == 'minor':
        version2 = version2.next_minor()
    elif version_part == 'patch':
        version2 = version2.next_patch()
    else:
        raise Exception('Unknown sem ver part "%s"' % version_part)

    log.debug('version1: %s', version)
    log.debug('version2: %s', version2)

    # ver_dict[version_part] = ver_dict[version_part] + 1
    # log.debug('ver_dict2: %s', ver_dict)
    new_ver_str = str(version2)

    log.debug('new_ver_str1: %s', new_ver_str)
    log.debug('old_build: %s', old_build)
    log.debug('old_pre: %s', old_pre)

    # This is unusual, for test cases with build/prerelease info, we want to
    # preserve that while revving versions, so re-append build/prerelease info
    if old_pre:
        new_ver_str = "%s-%s" % (new_ver_str, '.'.join(old_pre))
    if old_build:
        new_ver_str = "%s+%s" % (new_ver_str, '.'.join(old_build))

    # log.debug('new_ver_str: %s', new_ver_str)
    # new_ver_str = semver.format_version(**ver_dict)
    log.debug('new_ver_str2: %s', new_ver_str)

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


# Note: only supports deps list with just collection names, it doesn't support
# or expects deps to include version inof like 'geerlingguy.ntp >=1.1.1'
def dep_list_to_dep_dict(data):
    deps = data.get('dependencies', None)
    if deps is None:
        return data

    # already migrated
    if isinstance(deps, dict):
        return data

    deps_dict = {}

    log.debug('updating dependecies from a list to a dict')
    # whatever the RHS needs to be to signify no particular version required
    no_ver_specified_rhs = '*'
    for dep in deps:
        deps_dict[dep] = no_ver_specified_rhs

    data['dependencies'] = deps_dict
    log.debug('new dependencies dict: %s', data['dependencies'])
    return data


def license_to_list(data):
    license_ = data.get('license', None)

    new_license_list = []

    if isinstance(license_, list):
        new_license_list = license_
    else:
        new_license_list = [license_]
        log.debug("Converted 'license' (%s) to be a list (%s)", license_, new_license_list)

    data['license'] = new_license_list
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

        dep_list_to_dep_dict(data)

        license_to_list(data)

        ruamel.yaml.round_trip_dump(data, sys.stdout, block_seq_indent=2)

    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(process)d %(name)s %(funcName)s:%(lineno)d - %(message)s')
    sys.exit(main())
