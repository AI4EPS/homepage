#!/bin/bash
git submodule foreach '
    default_branch=$(git remote show origin | grep "HEAD branch" | sed "s/.*: //");
    git pull origin $default_branch;
'

