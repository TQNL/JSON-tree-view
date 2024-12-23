# JSON Tree Viewer

This Python script provides a utility for transforming JSON structures into a visually appealing tree-like ASCII representation. It uses PCRE2-like regex algorithms to process the JSON, handling nested objects and arrays, and generating a structured, readable output.

## Features

- Converts JSON arrays into numbered tree branches.
- Handles nested JSON structures and formats them as an ASCII tree.
- Fills in vertical lines for continuity between branches.
- Differentiates final branches with unique characters.
- Simple file selection using a graphical interface (Tkinter).

## Requirements

- Python 3.x
- `tkinter` (usually included with Python installations)

## Installation

1. Clone this repository or download the script.
2. Ensure Python 3.x is installed on your machine.
3. Install dependencies if needed (e.g., Tkinter).

## Usage

1. Run the script:

   ```bash
   python script_name.py
   ```

2. A file dialog will appear. Select a JSON file to process.
3. The script will read and process the selected JSON file.
4. The tree-like ASCII representation will be displayed in the console.

## Example Output

For a JSON input:

```json
{
  "name": "John",
  "age": 30,
  "children": ["Alice", "Bob"],
  "address": {
    "city": "New York",
    "zip": "10001"
  }
}
```

The output might look like this:

```
JSON
├─ name = "John"
├─ age = 30
├─ children
│   ╠═[0]: "Alice"
│   ╚═[1]: "Bob"
└─ address
    ├─ city = "New York"
    └─ zip = "10001"
```

## Notes

- Only fully prettified (expanded) JSON structures with proper indentation are supported.
- Ensure your JSON file is correctly formatted before processing.

## Acknowledgments

This script was developed with the assistance of ChatGPT, a language model by OpenAI.

## License

licensed under the GNU General Public License v3.0. See GNU License for details.

## Contributions

Contributions and feedback are welcome! If you encounter any issues or have suggestions for improvement, feel free to submit a pull request or open an issue.

