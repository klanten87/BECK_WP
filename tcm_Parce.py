import re

def parse_symbols(filename):
    with open(filename, encoding='utf-8') as f:
        content = f.read()

    # Find all <Symbol>...</Symbol> segments
    symbols = re.findall(r'<Symbol>(.*?)</Symbol>', content, re.DOTALL)

    for symbol in symbols:
        # Extract <Name>
        name_match = re.search(r'<Name>(.*?)</Name>', symbol)
        if not name_match:
            continue
        name = name_match.group(1)
        if '_Extal' not in name:
            continue

        # Extract <Comment>
        comment_match = re.search(r'<Comment><!\[CDATA\[(.*?)\]\]></Comment>', symbol, re.DOTALL)
        comment = comment_match.group(1) if comment_match else ''

        # Split comment at last comma
        if ',' in comment:
            main_comment, last_part = comment.rsplit(',', 1)
            main_comment = main_comment.strip()
            last_part = last_part.strip()
        else:
            main_comment = comment.strip()
            last_part = ''

        # Format name
        formatted_name = name.replace('.', '_').replace('_Extal', '')

        print(f"{formatted_name};{main_comment};{last_part}")

# Example usage:
parse_symbols('PLC.tmc')



