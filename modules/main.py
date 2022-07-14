import sys
from lexing.lexer import Lexer
from util.file import generate_map
from util.misc import check_verbose, printv
from util.warnings import CompilerError

def main():
    options, mode, out_dir, *filenames = sys.argv[1:]
    out_dir = out_dir[:-1] if out_dir[-1] == "/" else out_dir

    check_verbose(options)

    printv("Finding files and dirs...")
    file_map = generate_map(mode, out_dir, filenames)

    for file_pair in file_map:
        printv(f"Compiling {file_pair[0]}...")
        compile_file(options, file_pair)

def compile_file(options, file_pair):
    try:
        lexer = Lexer(file_pair[0])
        lexer.make_tokens()

        write_output(file_pair[1])
    except CompilerError as error:
        print(error.printable())
    finally:
        output_debug(options, file_pair[0], lexer)

def write_output(out_file_path):
    with open(out_file_path, "w", encoding = "UTF-8") as out_file:
        pass

def output_debug(options, name, lexer):
    if "d" not in options:
        return

    print(f"Tokens from {name}:\n\t{None if lexer is None else lexer.tokens}")
    print()

if __name__ == "__main__":
    main()
