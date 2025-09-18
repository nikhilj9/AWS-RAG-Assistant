import os

def print_tree(base_dir=".", max_depth=2, prefix=""):
    base_name = os.path.basename(os.path.abspath(base_dir))
    print(base_name if prefix == "" else prefix + base_name + "/")
    
    def walk(dir_path, prefix="", depth=0):
        if depth >= max_depth:
            return
        entries = [e for e in sorted(os.listdir(dir_path)) if not e.startswith(".")]
        for i, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            print(prefix + connector + entry + ("/" if os.path.isdir(path) else ""))
            if os.path.isdir(path):
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                walk(path, new_prefix, depth + 1)

    walk(base_dir, "", 0)

# run in your project root
print_tree(".", max_depth=2)
