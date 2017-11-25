#! /usr/bin/env bash

rsync --exclude="publish.sh" --exclude=".git" -vzcrSLh ./ application@46.101.20.20:~/hello-world.com/current/public
