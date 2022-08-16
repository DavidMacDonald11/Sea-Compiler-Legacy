#!/bin/bash
shopt -s extglob

sea_path="$(dirname "$0" | sed s/' '/'\\ '/g)"
working="$(pwd | sed s/' '/'\\ '/g)"

update() {
    eval cd "$sea_path"
    git pull origin main || sudo git pull origin main
}

print_usage() {
    printf "  %-20s" "$1"
    printf "\t%-52s\n" "$2"
}

usage() {
    printf "Usage: sea [OPTIONS]... [DIR|FILE]...\n"
    printf "Compiles Sea code in FILEs or in DIRs and subdirs.\n\n"
    printf "OPTIONS:\n"

    print_usage "-d, --debug" "writes debug information to a file."
    print_usage "-h, --help" "prints the sea command's usage information."
    print_usage "-u, --update" "uses git to update Sea to the latest version."
    print_usage "--version" "prints the program version information."
    printf "\n"

    print_usage "-c, --callback=FUNC" "specifies what to do after; depending"
    print_usage "" "on mode, this will usually call gcc by default;"
    print_usage "" "it will attempt to construct the desired files;"
    print_usage "" "specifying this option allows you to compile"
    print_usage "" "the C files as you wish; FUNC should be a"
    print_usage "" "callable script."
    print_usage "-m, --mode=MODE" "specifies what the program should do;"
    print_usage "" "  MODE=t    transpiles Sea to C,"
    print_usage "" "  MODE=p    does above and preprocesses C"
    print_usage "" "  MODE=c    does above and compiles C to asm,"
    print_usage "" "  MODE=a    does above and assembles asm to objects,"
    print_usage "" "  MODE=l    does above and links objects (default),"
    print_usage "" "  MODE=r    does above and runs generated program"
    print_usage "-o, --out=OUT" "specifies the output directory to compile to;"
    print_usage "" "all files will be written into OUT, which is"
    print_usage "" "the current directory by default; The directory"
    print_usage "" "will be created if it does not exist."
}

options="-"
mode="l"
callback=""
out_dir="."
files=()

add() {
    options="${options}$1"
}

get_arg_return=""

get_arg() {
    if [[ "${OPTARG}" == *"="* ]]
    then
        get_arg_return="${OPTARG#*=}"
        return 0
    fi

    printf "Must supply an argument to %s.\n" "$1"
    exit 1
}

get_single_arg() {
    get_arg "$1"

    char="${get_arg_return::1}"

    if [[ "$2" == "" || "$2" == *"$char"* ]]
    then
        get_arg_return="$char"
        return 0
    fi

    printf "Argument must be one of '%s'.\n" "$2"
    exit 3
}

mode_args="tpcalr"

while getopts ":-:hdum:o:c:" arg
do
    case "${arg}" in
        -)
            case "${OPTARG}" in
                "help")
                    usage
                    exit 0 ;;
                "debug")
                    add "d" ;;
                "update")
                    update
                    exit "$?" ;;
                "version")
                    printf "Sea 0.0.0\n"
                    exit 0 ;;
                "callback"|"callback="*)
                    get_arg "--callback"
                    callback="$get_arg_return" ;;
                "mode"|"mode="*)
                    get_single_arg "--mode" "$mode_args"
                    mode="$get_arg_return" ;;
                "out"|"out="*)
                    get_arg "--out"
                    out_dir="$get_arg_return" ;;
                *)
                    printf "Invalid option: --%s.\n" "${OPTARG}"
                    exit 2 ;;
            esac ;;
        "h")
            usage
            exit 0 ;;
        "d")
            add "d" ;;
        "u")
            update
            exit "$?" ;;
        "c")
            get_arg "-c"
            callback="$get_arg_return" ;;
        "m")
            get_single_arg "-m" "$mode_args"
            mode="$get_arg_return" ;;
        "o")
            get_arg "-o"
            out_dir="$get_arg_return" ;;
        :)
            printf "Must supply an argument to -%s.\n" "$OPTARG"
            exit 1 ;;
        ?)
            printf "Invalid option: -%s.\n" "${OPTARG}"
            exit 2 ;;
    esac
done

printv() {
    [[ "$options" == *"v"* ]] && printf "%s" "$@"
}

for (( i=1; i<= "$#"; i++ ))
do
    [[ "${!i}" == -* ]] && continue

    if [[ ! -f "${!i}" && ! -d "${!i}" ]]
    then
        printf "'%s' is not an existing file or directory.\n" "${!i}"
        exit 4
    fi

    files+=("${!i}")
done

if [[ "${files[*]}" == "" ]]
then
    printf "Requires input files or directories to compile.\n"
    exit 6
fi

if [[ "$callback" != "" && ! -x "$callback" ]]
then
    [[ -f "$callback" ]] && printf "Provided callback is not executable.\n"
    [[ ! -f  "$callback" ]] && printf "Provided callback does not exist.\n"
    exit 5
fi

mkdir -p "$out_dir"

python=$(printf '%s/venv/bin/python3' "$sea_path")
main=$(printf '%s/modules/main.py' "$sea_path")

eval cd "$sea_path"

if [[ ! -f "$python" ]]
then
    python3 -m venv venv
fi

source venv/bin/activate
eval cd "$working"

eval "$python" "$main" "$options" "$mode" "$out_dir" "${files[*]@Q}"

if [[ "$callback" != "" || "$mode" == "t" ]]
then
    printv "Running callback..."
    eval "$callback"
    exit $?
fi

gcc_arg=""
gcc_output=""
objects=""

case "$mode" in
    "p")
        gcc_arg="-E"
        gcc_output="_preprocessed.c" ;;
    "c")
        gcc_arg="-S"
        gcc_output=".s" ;;
    "a"|"l"|"r")
        gcc_arg="-c"
        gcc_output=".o" ;;
esac

manifest="$out_dir/manifest.seatmp"
generated="$manifest"

while read -r line
do
    objects="$objects $line.o"
    eval gcc "$gcc_arg" "$line.c" -o "$line$gcc_output"
    generated="$generated $line.c $line$gcc_output"
done <"$manifest"

if [[ "$mode" == "l" || "$mode" == "r" ]]
then
    eval gcc "$objects" -o "$out_dir/main" -lm -lgcc_s -lgcc -lc && eval rm -r "$generated"
fi

if [[ "$mode" == "r" ]]
then
    eval cd "$out_dir"
    ./main
fi

exit 0
