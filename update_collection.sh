#!/bin/bash -x

(update_galaxy_yml galaxy.yml > galaxy.yml.new)
cp galaxy.yml.new galaxy.yml

VER=$(cat galaxy.yml | shyaml get-value version)

git commit -v -a -m "rev to ${VER}"
git tag "${VER}" -m "${VER}"
git push --tags origin master
