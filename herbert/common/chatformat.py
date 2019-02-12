from functools import partial

STYLE_MD = 'MARKDOWN'
STYLE_HTML = 'HTML'

# use custom style cause i want to use chars like _ and <
# if anyone needs to use !§![ or !§!] the prefixes can be
# made increasingly weird on demand
STYLE_CUSTOM = 'CUSTOM'

STYLE = STYLE_CUSTOM


def get_parse_mode(style=STYLE):
    return style


def get_output_mode(style=STYLE):
    if style == STYLE_CUSTOM:
        return STYLE_HTML
    return style


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

    string = escape_string(string, style=target_style)

    for key, val in substitutions.items():
        string = string.replace(key, val)

    return string


def ensure_markup_clean(string, msg='', style=STYLE):
    crimes = {
        STYLE_HTML: ('<', '>'),
        STYLE_MD: ('`', '_', '*', '['),
        STYLE_CUSTOM: ('!§![', '!§!]')
    }[style]

    if any(crime in string for crime in crimes):
        raise ValueError(f'{string} contains (invalid?) markup sequences. {msg}')


def escape_string(string, style=STYLE):
    # markdown cannot be escaped. hope for the best.
    if style == STYLE_HTML:
        return string.replace("<", "&lt;").replace(">", "&gt;")

    return string


def link_to(url, name=None, style=STYLE):
    name = name or url
    try:
        return {
            STYLE_HTML: f'<a href="{url}">{name}</a>',
            STYLE_MD: f'[{name}]({url})',
            STYLE_CUSTOM: f'!§![a{url}!§!|A{name}!§!]a'
        }[style]
    except KeyError:
        raise ValueError(f'Style {style} is undefined.')


def _wrap_delimiters(style_dict, text, escape=True, style=STYLE):
    try:
        prefix, suffix = style_dict[style]
        if escape:
            text = escape_string(text, style)

        return prefix + text + suffix

    except KeyError:
        raise ValueError(f'Style {style} is undefined.')


italic = em = it = partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<i>', '</i>'),
        STYLE_MD: ('_', '_'),
        STYLE_CUSTOM: ('!§![i', '!§!]i')
    }
)

bold = partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<b>', '</b>'),
        STYLE_MD: ('*', '*'),
        STYLE_CUSTOM: ('!§![b', '!§!]b')
    }
)

mono = partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<code>', '</code>'),
        STYLE_MD: ('*', '*'),
        STYLE_CUSTOM: ('!§![c', '!§!]c')
    }
)
