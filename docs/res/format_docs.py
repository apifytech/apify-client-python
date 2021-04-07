#!/usr/bin/env python3
import re

# The markdown generated by Sphinx has a few issues, we have to fix those manually
subs = [
    (r'class (\w+)\([^)]+\)', r'class \1'),  # remove class signature, it is duplicated in __init__ method
    (r'\n\n###', r'\n***\n\n###'),  # add horizontal line before each class and method
    (r'\\__init__', r'__init__'),  # remove bad escape in __init__
    (r'(?<=\*\*Return type\*\*\n\n    )([\w.]+)', r'`\1`'),  # put return types in backticks if not already
    (r'(?<=\*\*Return type\*\*\n\n    )`((\w+)Client)`', r'[`\1`](#\1)'),  # add fragment links to return types if they are of type SomethingClient
    (r' None([, ])', r' `None`\1'),  # replace None with `None`, if it's in a normal sentence (surrounded by whitespace or comma)
    (r'\*\*Parameters\*\*\n\n    \*\*', '**Parameters**\n\n    * **'),  # workaround for sphinx bug with single parameter not being rendered as list
    (r'\(`(.*), optional`\)', r'(`\1`, *optional*)'),  # workaround for bug formatting parameter types
    # (r'\*\*\[\*\*(\w+)\*\*\]', r'[\1]'),  # workaround for bug formatting parameter types
    (r'`(\w+)`\[`(\w+)`\]', r'`\1[\2]`'),  # workaround for complex parameter types with backticks
    (\
        r'`Union`\[`str`, `int`, `float`, `bool`, `None`, `Dict`\[`str`, `Any`\], `List\[Any\]`\]', \
        '`Union[str, int, float, bool, None, Dict[str, Any], List[Any]]`' \
    ),  # workaround for the JSONSerializable type being rendered badly (I know this would be better generic, but it would be really hard to write)
    (r'(###[^\n]+)\n', r'\1\n\n'),  # add empty line after every heading
    (r'\n +\n', '\n\n'),  # remove whitespace from empty lines
    (r'\n\n+', '\n\n'),  # reduce 3+ newlines to 2
    (r'    ', r'  '),  # indent with 2 spaces instead of 4
]

# Load the api_reference.md generated by Sphinx
with open('api_reference.md', 'r+') as api_reference:
    api_reference_content = api_reference.read()

    # Do the above defined replacements
    for (pattern, repl) in subs:
        api_reference_content = re.sub(pattern, repl, api_reference_content, flags=re.M)

    # Generate the table of contents for each class
    toc = {}
    current_class = ''
    for line in api_reference_content.splitlines():
        match = re.match(r'### class (\w+)', line)
        if match is not None:
            current_class = match.group(1)
        match = re.match(r'#### (\w+)', line)
        if match is not None:
            method = match.group(1)
            method = re.sub('_', '\\_', method)
            if current_class not in toc:
                toc[current_class] = [method]
            else:
                toc[current_class].append(method)

    # Parse the whole file again and add fragment links
    transformed_lines = []
    current_class = ''
    in_class_description = False
    for line in api_reference_content.splitlines():
        # Add special fragment link marker to each class header (will get used in Apify docs to display "Copy link" link)
        match = re.match(r'### class (\w+)', line)
        if match is not None:
            current_class = match.group(1)
            in_class_description = True
            line = re.sub(r'### class', f'### [](#{current_class.lower()})', line)

        # Add special fragment link marker to each function header (will get used in Apify docs to display "Copy link" link)
        match = re.match(r'#### (\w+)', line)
        if match is not None:
            method = match.group(1)
            line = re.sub(r'(#### .*)\\\*(.*)', r'\1*\2', line)
            line = re.sub(r'#### (\w+)(\([^)]*\))', f'#### [](#{current_class.lower()}-{method.lower()}) `{current_class}.\\1\\2`', line)

        # Add table of contents to the beginning of each class (after the class description)
        match = re.match(r'^\*\*\*', line)
        if match is not None and in_class_description:
            transformed_lines.extend([f'* [{method}()](#{current_class.lower()}-{method.lower()})' for method in toc[current_class]])
            transformed_lines.append('')
            in_class_description = False

        # Lowercase all the links
        match = re.search(r'(\[[^\]]*\])(\(#[^)]+\))', line)
        if match is not None:
            line = re.sub(r'(\[[^\]]*\])(\(#[^)]+\))', f'{match.group(1)}{match.group(2).lower()}', line)

        transformed_lines.append(line)

    # Add a short header
    api_reference_content = \
        '\n## API Reference\n\n' + \
        'All public classes, methods and their parameters can be inspected in this API reference.\n\n' + \
        '\n'.join(transformed_lines) + '\n'

    # Rewrite the api_reference.md file with the transformed content
    api_reference.seek(0)
    api_reference.write(api_reference_content)
    api_reference.truncate()