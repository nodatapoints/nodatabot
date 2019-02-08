
STYLE_MD = 'MARKDOWN'
STYLE_HTML = 'HTML'

# use custom style cause i want to use chars like _ and <
# if anyone needs to use !§![ or !§!] the prefixes can be
# made increasingly weird on demand
STYLE_CUSTOM = 'CUSTOM'

STYLE = STYLE_CUSTOM


def get_parse_mode(use_style=STYLE):
    return use_style


def get_output_mode(use_style=STYLE):
    if use_style == STYLE_CUSTOM:
        return STYLE_HTML
    return use_style


def render_custom(string, target_style=STYLE_HTML):
    assert target_style == STYLE_HTML, "Markdown rendering is not supported yet"
    substitutions = {
        '!§![i': '<i>',
        '!§!]i': '</i>',
        '!§![c': '<code>',
        '!§!]c': '</code>',
        '!§![b': '<b>',
        '!§!]b': '</b>',
        '!§![a': '<a href="',
        '!§!|A': '">',
        '!§!]a': '</a>'
    }

    string = escape_string(string, use_style=target_style)

    for key, val in substitutions.items():
        string = string.replace(key, val)

    return string


def ensure_markup_clean(string, msg=None, use_style=STYLE):
    bad_strings = []
    if use_style == STYLE_HTML:
        bad_strings += ['<', '>']
    elif use_style == STYLE_MD:
        bad_strings += ['`', '_', '*', '[']
    elif use_style == STYLE_CUSTOM:
        bad_strings += ['!§![', '!§!]']

    total_count = 0
    for s in bad_strings:
        total_count += string.count(s)

    assert total_count == 0, (f"{string} contains (invalid?) markup sequences! " + (msg if msg else ''))


def escape_string(string, use_style=STYLE):
    # markdown cannot be escaped. hope for the best.
    if use_style == STYLE_HTML:
        return string.replace("<", "&lt;").replace(">", "&gt;")

    return string


def link_to(url, name=None, use_style=STYLE):
    name = name or url

    if use_style == STYLE_HTML:
        return f'<a href="{url}">{name}</a>'
    elif use_style == STYLE_MD:
        return f'[{name}]({url})'
    elif use_style == STYLE_CUSTOM:
        return f'!§![a{url}!§!|A{name}!§!]a'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def italic(text, escape=True, use_style=STYLE):
    if escape:
        text = escape_string(text)
    if use_style == STYLE_HTML:
        return f'<i>{text}</i>'
    elif use_style == STYLE_MD:
        return f'_{text}_'
    elif use_style == STYLE_CUSTOM:
        return f'!§![i{text}!§!]i'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def bold(text, escape=True, use_style=STYLE):
    if escape:
        text = escape_string(text)
    if use_style == STYLE_HTML:
        return f'<b>{text}</b>'
    elif use_style == STYLE_MD:
        return f'*{text}*'
    elif use_style == STYLE_CUSTOM:
        return f'!§![b{text}!§!]b'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def mono(text, escape=True, use_style=STYLE):
    if escape:
        text = escape_string(text)
    if use_style == STYLE_HTML:
        return f'<code>{text}</code>'
    elif use_style == STYLE_MD:
        return f'`{text}`'
    elif use_style == STYLE_CUSTOM:
        return f'!§![c{text}!§!]c'
    else:
        raise ValueError(f"Style {use_style} is undefined.")
