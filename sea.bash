#!/bin/bash

print_usage() {
    printf "\t%-30s" "$1"
    printf "\t%-30s\n\n" "$2"
}

usage() {
    printf "Usage: sea [options...] [files|dirs...]\n"
    printf "Options:\n"

    print_usage "--help or -h" "prints the sea command's usage information."
}

for (( i=1; i<= "$#"; i++ ))
do
    if [[ "${!i}" == "--help" ||  "${!i}" == "-h" ]]
    then
        usage
        exit 1
    fi
done

python="./venv/bin/python3"
main="./modules/main.py"

eval "$python" "$main"

exit 0
