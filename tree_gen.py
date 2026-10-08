import os
import ast

IGNORE_DIRS = {'.venv', 'venv', '__pycache__', '.idea', '.git'}

with open('readme/readme.txt', 'w', encoding='utf-8') as output_file:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                classes = {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
                           for n in tree.body if isinstance(n, ast.ClassDef)}

                if not funcs and not classes:
                    continue

                display_path = os.path.normpath(filepath).replace('\\', '/')
                output_file.write(f"### `{display_path}`\n")

                for func in funcs:
                    output_file.write(f"*   **{func}**\n")

                for cls_name, methods in classes.items():
                    output_file.write(f"*   **Class: {cls_name}**\n")
                    for method in methods:
                        output_file.write(f"    *   {method}\n")
                output_file.write("\n")

            except SyntaxError:
                output_file.write(f"### `{filepath}`\n*   [Syntax Error]\n")
