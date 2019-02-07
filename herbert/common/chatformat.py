
STYLE_MD = 'MARKDOWN'
STYLE_HTML = 'HTML'

STYLE = STYLE_HTML


def get_parse_mode(use_style=STYLE):
    return use_style


def ensure_markup_clean(string, msg=None, use_style=STYLE):
    bad_strings = []
    if use_style == STYLE_HTML:
        bad_strings += ['<', '>']
    elif use_style == STYLE_MD:
        bad_strings += ['`', '_', '*', '[']

    total_count = 0
    for s in bad_strings:
        total_count += string.count(s)

    assert total_count == 0, (f"{string} contains (invalid?) markup sequences! " + (msg if msg else ''))


def escape_string(string, use_style=STYLE):
    # markdown cannot be escaped. hope for the best.
    if use_style == STYLE_MD:
        return string

    return string.replace("<", "&lt;").replace(">", "&gt;")


def link_to(url, name=None, use_style=STYLE):
    name = name or url

    if use_style == STYLE_HTML:
        return f'<a href="{url}">{name}</a>'
    elif use_style == STYLE_MD:
        return f'[{name}]({url})'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def italic(text, escape=True, use_style=STYLE):
    if escape:
        text = escape_string(text)
    if use_style == STYLE_HTML:
        return f'<i>{text}</i>'
    elif use_style == STYLE_MD:
        return f'_{text}_'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def bold(text, escape=True, use_style=STYLE):
    if escape:
        text = escape_string(text)
    if use_style == STYLE_HTML:
        return f'<b>{text}</b>'
    elif use_style == STYLE_MD:
        return f'*{text}*'
    else:
        raise ValueError(f"Style {use_style} is undefined.")


def mono(text, escape=True):
    if escape:
        text = escape_string(text)
    if STYLE == STYLE_HTML:
        return f'<code>{text}</code>'
    elif STYLE == STYLE_MD:
        return f'`{text}`'
    else:
        raise ValueError(f"Style {STYLE} is undefined.")
