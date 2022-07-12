# The Sea Programming Language
The Sea language is essentially a translation of the C language, with Python-like syntax. The goal is to make C easier to read, write, and debug. This increase in programming speed will more than make up for the small increase in compilation time.

Sea - It's C, just written differently.

# File Extensions and Pronunciation
With this language comes a few file extension requirements:
* `.sea`; equivalent to `.c`
* `.hea`; equivalent to `.h`
* `.seatmp`; used for temporary compiler data

Let's set the record straight now and avoid creating a "gif" situation.
The `.sea` file extension is pronounced like the English word "sea."
The `.hea` file extension is pronounced like the English word "he."

Sea is a play-on-words of C.
The name matches the concept of writing C in a different way.
For headers, `.hea` was the obvious choice as it is `.sea` with an "h" and contains the first three letters of "header." I chose the pronunciation so that it would rhyme.

# Compiler Functionality
This program includes a versatile Sea compiler, as well as language documentation.
The compiler can transpile Sea to C.
From there, the program can automatically use `gcc` to compile, assemble, and or link.
You may also provide your own script to compile the generated C files if you wish.

# Install Instructions
The ideal way to install Sea is to `git clone` this repository into a permanent install location.

Then, inside of a `~/.bashrc`, `~/.zshrc`, etc. file, add a global alias to `sea.bash`.
Example:
- `alias sea=/home/user/Downloads/Sea-Programming-Language/sea.bash`

Otherwise, you may simply run the `sea.bash` command locally.
Replace all future `sea` commands in this text with `sea.bash`.
Also be aware that without specifying an output directory, the compiler will dump all created files in the location you run it from.

# Run Instructions
Usage: sea [OPTIONS]... [DIR|FILE]...

### OPTIONS
Run `sea --help` to see the usage information.

To see the generated tokens and AST, add the `--debug` option.

To update the compiler using git, run `sea --update`.

To recieve updates as the program runs, add the `--verbose` option.

To check the compiler version, run `sea --version`.

To customize the compilation of the generated C files, add the `--callback=PATH` option, where `PATH` is the path to the runnable script file.
Once C files are created, this script will be ran.
Without this argument, the program will call `gcc` and try to complete the process.
Note that the compiler will create a `manifest.seatmp` file in the output directory containing a list of the output filepaths. This may be useful for your script.

To stop compilation at a specific stage, use the `--mode=MODE` option, where `MODE` is one of the following (note that only the first letter is checked):
* t, short for transpile, does above and compiles (transpiles) Sea to C.
Generates `.c` and `.h` files only.
* p, short for preprocess, does above and preprocesses the C files.
Generates `.c` files only.
* c, short for compile, does above and compiles C to assembly.
Generates `.s` assembly files only.
* a, short for assemble, does above and assebles objects.
Generates `.o` object files only.
* l, short for link, does above and links objects into an executable.
Generates a `main` executable file only.
This is the default option when the `--mode` option is not specified.

To specify a custom output directory, use the `--out=OUT` option, where `OUT` is the path to an existing or non-existing folder to place all output into.
By default, `OUT` is the directory the program is ran from.

### DIR|FILE
This must come after the options, or the options will break.
You can simply run `sea [OPTIONS] file1 file2 dir1 dir2 ...` in no particular order.
If you enter a file, it will be compiled if it is a Sea file.
If you enter a directory, all sea files within it and all child directories will be compiled.
You may enter relative or absolute paths.
If you enter a relative path, the parent directories will be recreated in the output directory.
If the same file is input multiple times, it will only be compiled once.
The generated output files, if mode is not l, will be the same name as the source files.

# Future Development
I'd like to...
* rewrite the compiler in Sea, once it is finished.
* make syntax highlighting, icons, logos, and a linter for VS Code.
Perhaps for other IDEs as well.
* make the compiler usable on non-Unix systems.
* create optional libraries to make Sea more like Python.

# Documentation and Syntax
I've included [documentation](./docs/docs.adoc) for the Sea language and compiler.

To see the complete development history, check out the [legacy repository](https://github.com/DavidMacDonald11/Sea-Programming-Language-LEGACY).

# Legal
I am basing much of this code on [David Callanan's BASIC interpreter written in Python](https://github.com/davidcallanan/py-myopl-code) which is licensed under [MIT](https://github.com/davidcallanan/py-myopl-code/blob/master/LICENSE).

Feel free to write your own program to interact with this code and absolutely feel free to use the Sea language. It is my intention for this language and code to be useful. If you think my current license is too strict to achieve that, let me know. See [LICENSE](./LICENSE) for details.

Feel free to use my code as a basis for your own compiler, programming language, etc!
