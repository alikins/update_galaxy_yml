#!/bin/bash -x

REMOTE=${REMOTE:-origin}
BRANCH=${BRANCH:-master}

ensure_plugins_dir()
{
    # if no plugins/ dir, create it, add it, commit it
    if [ -d plugins/ ]; then
        return
    fi

    echo "Adding a plugins/ dir"
    mkdir plugins/

    echo "Adding plugins/ to git"
    git add plugins

    git commit -m "adding plugins/ dir" plugins
}

# __init__.py files in plugins/ is no longer needed
rm_plugins_init_py()
{
    # Note: this assumes a git repo
    find plugins/ -name '__init__.py' | xargs git rm

    echo "Removing plugins/ __init__.py files"
    git commit -m "Removing now unneeded __init__.py files in plugins/"
}


CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "${CURRENT_BRANCH}" != "${BRANCH}" ] ; then
    echo "This script defaults to pushing changes to origin master but you are on local branch ${CURRENT_BRANCH}"
    echo "Use and 'REMOTE=<Your remote here> BRANCH=${CURRENT_BRANCH} update_collection.sh'"
    echo "to push to other remotes or branches"
    exit 1
fi

# migrate modules/ and module_utils under plugins/
git ls-files --error-unmatch modules/ 2>/dev/null
HAS_MODULES=$?

git ls-files --error-unmatch module_utils/ 2>/dev/null
HAS_MODULE_UTILS=$?


# if 'modules/' is tracked by git indicated by ls-files finding it
if [ $HAS_MODULES -eq 0 ]; then
    ensure_plugins_dir
    echo "Moving modules/ dir under plugins/"
    git mv modules/ plugins/
fi

if [ $HAS_MODULE_UTILS -eq 0 ]; then
    ensure_plugins_dir
    echo "Moving module_utils/ dir under plugins/"
    git mv module_utils/ plugins/
fi

# remove any plugins __init__.py files
rm_plugins_init_py

(update_galaxy_yml galaxy.yml > galaxy.yml.new)
# FIXME: if galaxy.yml.new is empty, exit
cp galaxy.yml.new galaxy.yml

# exit if any of this stuff errors
set -e
VER=$(cat galaxy.yml | shyaml get-value version)

git commit -v -a -m "rev to ${VER}"

git tag "${VER}" -m "${VER}"
git push --tags "${REMOTE}" "${BRANCH}"
