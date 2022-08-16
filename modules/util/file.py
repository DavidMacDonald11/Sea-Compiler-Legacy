import os

def generate_map(out_dir, filenames):
    result = []
    paths = make_paths(filenames)

    for path in paths:
        if not path.endswith(".sea"):
            continue

        out_path = create_out_path(out_dir, path)
        out_path_dirs = os.path.dirname(out_path)

        if out_path_dirs != "" and not os.path.exists(out_path_dirs):
            os.makedirs(out_path_dirs)

        result += [(path, out_path)]

    write_manifest(out_dir, result)
    return result

def make_paths(filenames):
    paths = set()

    for name in filenames:
        if os.path.isfile(name):
            paths.add(name)
        else:
            for file in find_files_in_dir(name):
                paths.add(file)

    return paths

def find_files_in_dir(directory):
    for root, _, names in os.walk(directory):
        for name in names:
            yield os.path.join(root, name)

def create_out_path(out_dir, path):
    if path[0] == "/":
        out_path = f"{out_dir}/{os.path.basename(path)}"
    else:
        path = "/".join(path.replace("./", "").split("/")[1:])
        out_path = f"{out_dir}/{path}"

    return out_path.replace(".sea", ".c")

def write_manifest(out_dir, file_map):
    with open(f"{out_dir}/manifest.seatmp", "w", encoding = "UTF-8") as manifest:
        for _, file in file_map:
            manifest.write(f"{file.replace('.c', '')}\n")
