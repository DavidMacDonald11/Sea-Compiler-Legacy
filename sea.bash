#!/bin/bash

sea_path="$(dirname "$0")"
working="$(pwd | sed s/' '/'\\ '/g)"

print_usage() {
    printf "\t%-30s" "$1"
    printf "\t%-30s\n\n" "$2"
}

usage() {
    printf "Usage: sea [options...] [dirs|files...]\n"
    printf "Options:\n"

    print_usage "--help or -h" "prints the sea command's usage information."
    print_usage "--debug or -d" "writes debug information to a file."
    print_usage "--src [DIR]" "specifies the input directory to compile from."
    print_usage "--bin [DIR]" "specifies the output directory to compile to."
}

options="-"
in_dir=src
out_dir=bin
paths=()

add() {
    options="${options}$1"
}

for (( i=1; i<= "$#"; i++ ))
do
    arg="${!i}"

    if [[ "$arg" == --* ]]
    then
        case "$arg" in
            --help)
                usage
                exit 1
                ;;
            --src)
                (( i++ ))
                in_dir="${!i}"
                continue
                ;;
            --bin)
                (( i++ ))
                out_dir="${!i}"
                continue
                ;;
            --debug) add "d";;
        esac
    fi

    if [[ "$arg" == -* && "$arg" != --* ]]
    then
        case "$arg" in
            *h*)
                usage
                exit 1
                ;;
            *d*) add "d";;
        esac
    fi

    [[ "$arg" == -* ]] && continue
    paths+=("$arg")
done

python=$(printf '%s/venv/bin/python3' "$sea_path")
main=$(printf '%s/modules/main.py' "$sea_path")

eval cd "$sea_path"

if [[ ! -f "$python" ]]
then
    python3 -m venv venv
fi

source venv/bin/activate
eval cd "$working"

eval "$python" "$main" "$options" "$in_dir" "$out_dir" "${paths[@]}"

exit 0
