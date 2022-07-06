import sys
from util.file import generate_map
from util.misc import check_verbose, printv

def main():
    options, mode, out_dir, *filenames = sys.argv[1:]
    out_dir = out_dir[:-1] if out_dir[-1] == "/" else out_dir

    debug = "d" in options
    check_verbose(options)

    printv("Finding files and dirs...")
    file_map = generate_map(mode, out_dir, filenames)


if __name__ == "__main__":
    main()
