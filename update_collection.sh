#!/bin/bash -x

ensure_plugins_dir()
{
    # if no plugins/ dir, create it, add it, commit it
    if [ -d plugins/ ]; then
        return
    fi

    echo "Adding a plugins/ dir and __init__.py"
    mkdir plugins/
    touch plugins/__init__.py

    echo "Adding plugins/ to git"
    git add plugins

    git commit -m "adding plugins/ dir" plugins
}


# migrate modules/ and module_utils under plugins/
git ls-files --error-unmatch modules/
HAS_MODULES=$?

git ls-files --error-unmatch module_utils/
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

(update_galaxy_yml galaxy.yml > galaxy.yml.new)
cp galaxy.yml.new galaxy.yml

VER=$(cat galaxy.yml | shyaml get-value version)

git commit -v -a -m "rev to ${VER}"
git tag "${VER}" -m "${VER}"
git push --tags origin master
