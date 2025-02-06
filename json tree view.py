import tkinter as tk
from tkinter import filedialog
import re
# only fully prettified (expanded) with indent 2 JSON structures are currently supported


def process_content_with_pcre2(content):
    """
    Transform JSON content into a tree-like ASCII representation using a PCRE2-like algorithm.
    This function:
    - Processes lists (square-bracketed arrays), extracting their items and numbering them as [0], [1], etc.
    - Converts certain JSON structures into a branching ASCII tree format.
    - Cleans and normalizes the resulting structure.
    """

    # Matches individual list items inside square brackets.
    # The pattern assumes a fully expanded JSON, and captures indentation and the value.
    list_pattern = (
        r'(^\s*?)'                       # Capture indentation
        r'([\d\.]+|true|false|null|"[^"]*"|{.*?(?=}.[^}]*?(?=[{\]]))}),? ?'
    )
    list_flags = re.DOTALL | re.MULTILINE

    # Process lists while there are still '[' characters in the content.
    while '[' in content:
        # Find blocks of text enclosed in a single pair of square brackets (no nesting)
        matches = re.findall(r'\[[^\[\]]*\]', content)

        for match in matches:
            index_counter = 0

            def replace_with_index(m):
                nonlocal index_counter
                # m.group(1) is indentation, m.group(2) is the value.
                replacement = f"{m.group(1)}╠═({index_counter}): {m.group(2)}"
                index_counter += 1
                return replacement

            # Substitute each list item with the indexed format inside the match.
            substituted = re.sub(list_pattern, replace_with_index, match, flags=list_flags)

            # Replace the original match in the content, removing the brackets.
            content = content.replace(
                match,
                substituted.replace('[', '').replace(']', '')
            )

    # Replace index formatting from parentheses to square brackets
    content = content.replace('(', '[')
    content = content.replace(')', ']')

    # Apply various regex-based substitutions to finalize the ASCII tree format.

    # Convert certain tokens (object starts, equals signs) to tree-branch indicators.
    # (: ?{| = {| ?{|,)(\s*) → ${1}├─
    content = re.sub(r'(: ?{| = {| ?{|,)(\s*)', r'\2├─', content, flags=re.MULTILINE)

    # Remove trailing brackets after newlines: \n\s*[\)}] → 
    content = re.sub(r'\n\s*[\]}]', '', content, flags=re.MULTILINE)

    # Remove trailing whitespace: \s*$ →
    content = re.sub(r'\s*$', '', content, flags=re.MULTILINE)

    # Remove colons at line ends: :$ →
    content = re.sub(r':$', '', content, flags=re.MULTILINE)

    # Replace ": " with " = "
    content = re.sub(r': ', ' = ', content, flags=re.MULTILINE)

    # Replace empty lines with "JSON"
    content = re.sub(r'^$', 'JSON', content, flags=re.MULTILINE)

    return content


def fill_vertical_lines(content: str) -> str:
    """
    Fill in vertical lines between branches in the ASCII tree so that
    they connect properly without gaps.
    """
    lines = content.split('\n')
    vertical_map = {}

    def vertical_char_for(c):
        if c in ('├', '│'):
            return '│'
        elif c in ('╠', '║'):
            return '║'
        return None

    max_width = max(len(line) for line in lines)
    lines = [line.ljust(max_width) for line in lines]

    for i, line in enumerate(lines):
        line_list = list(line)

        # Continue vertical lines from above.
        for col, vchar in vertical_map.copy().items():
            if col < len(line_list):
                if line_list[col] == ' ':
                    line_list[col] = vchar
                else:
                    # If we encounter something else, we may need to stop or adjust vertical lines.
                    if line_list[col] not in (vchar, '├', '╠'):
                        del vertical_map[col]
                    else:
                        # If we see another branch at the same column, update the vertical line character if needed.
                        vc = vertical_char_for(line_list[col])
                        if vc and vc != vchar:
                            vertical_map[col] = vc
            else:
                # Column out of range, remove from vertical_map
                del vertical_map[col]

        # Detect new vertical or branch chars and update vertical_map
        for idx, c in enumerate(line_list):
            if c in ('├', '╠', '│', '║'):
                vc = vertical_char_for(c)
                if vc:
                    vertical_map[idx] = vc

        lines[i] = ''.join(line_list)

        # No vertical lines continue after the last line
        if i == len(lines) - 1:
            vertical_map.clear()

    # Trim trailing spaces
    lines = [line.rstrip() for line in lines]
    return "\n".join(lines)


def convert_final_branches(content: str) -> str:
    """
    Convert branches that have no siblings below (final siblings) to their ending counterparts:
    - '├' becomes '└'
    - '╠' becomes '╚'
    and remove vertical lines continuing below these final branches.
    """
    lines = content.split('\n')
    max_width = max(len(line) for line in lines)
    lines = [line.ljust(max_width) for line in lines]

    # Identify all branch characters
    branches = []
    for i, line in enumerate(lines):
        for idx, c in enumerate(line):
            if c in ('├', '╠'):
                branches.append((i, idx, c))

    # Determine which branches are final (no siblings below)
    for (lidx, col, c) in branches:
        is_final = True
        for j in range(lidx + 1, len(lines)):
            if col < len(lines[j]):
                down_char = lines[j][col]
                # Another '├' or '╠' at the same column would mean not final
                if down_char in ('├', '╠'):
                    is_final = False
                    break
                # If a non-vertical, non-space char appears, continuity breaks, leaving it final.
                if down_char not in ('│', '║', ' '):
                    break
            else:
                # No more lines at this column - still final
                break

        if is_final:
            # Convert the branch char to a final branch char
            replacement = '└' if c == '├' else '╚'
            line_list = list(lines[lidx])
            line_list[col] = replacement
            lines[lidx] = ''.join(line_list)

            # Remove vertical lines continuing below the final branch
            for j in range(lidx + 1, len(lines)):
                line_list_down = list(lines[j])
                if col < len(line_list_down) and line_list_down[col] in ('│', '║'):
                    line_list_down[col] = ' '
                    lines[j] = ''.join(line_list_down)
                else:
                    break

    # Trim trailing spaces after modifications
    lines = [line.rstrip() for line in lines]

    return "\n".join(lines)


def select_and_print_json_with_pcre2():
    """
    Display a file dialog to select a JSON file, then process it
    to produce a tree-like ASCII representation and print the result.
    """
    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select the JSON file
    file_path = filedialog.askopenfilename(
        title="Select a JSON File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        # Read the JSON file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Process the content
        content = process_content_with_pcre2(content)
        content = convert_final_branches(content)
        processed_content = fill_vertical_lines(content)

        # Print the processed content
        print("\nProcessed Content:\n")
        # Specify the output file name
        output_file = "output.txt"

        # Open the file in write mode and write the content to it
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(processed_content)

        print(f"Content saved to {output_file}")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


if __name__ == "__main__":
    select_and_print_json_with_pcre2()
