"""
FIXME this contains several specific hardcoded style definitions and conversions
please improve (without breaking things)
"""
import re
from html.parser import HTMLParser
from typing import Tuple, List

from telegram import MessageEntity

from common.basic_decorators import as_partial
from common.basic_utils import utf16len
from herberror import BadHerberror

STYLE_MD = 'MARKDOWN'
STYLE_HTML = 'HTML'

# use custom style cause i want to use chars like _ and <
# if anyone needs to use !§![ or !§!] the prefixes can be
# made increasingly weird on demand
STYLE_BACKEND = 'CUSTOM'
STYLE_PARA = '§§'

STYLE = STYLE_BACKEND


class MessageMarkupError(Exception):
    """ thrown if the markup of a message is invalid """


def get_parse_mode(style=STYLE):
    """ return the current encoding type """
    return style


def get_output_mode(style=STYLE):
    """ return the correct output encoding after rendering """
    if style in (STYLE_BACKEND, STYLE_PARA, STYLE_MD):
        return STYLE_HTML
    return style


def render_style_backend(string, target_style=STYLE_HTML):
    """ transform STYLE_BACKEND to target_style """
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


def render_style_para(string, target_style=STYLE_BACKEND):
    """ transform STYLE_PARA to target_style """
    assert target_style == STYLE_BACKEND, "Direct HTML rendering is not supported yet"
    string = re.sub(r'm§([^§]*)§', lambda m: mono(m.group(1), style=STYLE_BACKEND), string)
    string = re.sub(r'b§([^§]*)§', lambda m: bold(m.group(1), style=STYLE_BACKEND), string)
    string = re.sub(r'i§([^§]*)§', lambda m: italic(m.group(1), style=STYLE_BACKEND), string)

    return string


def render_style_markdown(string, target_style=STYLE_HTML):
    """ transform STYLE_PARA to target_style """
    string = re.sub(r'`([^`]*)`', lambda m: mono(m.group(1), style=target_style), string)
    string = re.sub(r'_([^`]*)_', lambda m: bold(m.group(1), style=target_style), string)
    string = re.sub(r'\*([^`]*)\*', lambda m: italic(m.group(1), style=target_style), string)

    return string


def render(text, input_style):
    """ transform text from one style to another """
    if input_style == STYLE_BACKEND:
        render_text = render_style_backend(text)
    elif input_style == STYLE_MD:
        render_text = render_style_markdown(text)
    elif input_style == STYLE_PARA:
        render_text = render_style_backend(render_style_para(text, target_style=STYLE_BACKEND))
    else:
        render_text = text

    return render_text, get_output_mode(input_style)


def ensure_markup_clean(string, msg='', style=STYLE):
    """ raise an error if string contains formatting character sequences """
    crimes = {
        STYLE_HTML: ('<', '>'),
        STYLE_MD: ('`', '_', '*', '['),
        STYLE_BACKEND: ('!§![', '!§!]'),
        STYLE_PARA: ('§',)
    }[style]

    if any(crime in string for crime in crimes):
        raise ValueError(f'{string} contains (invalid?) markup sequences. {msg}')


def escape_string(string, style=STYLE):
    """ to allow <, > in html formatted strings they need to be escaped first """
    # only html can be escaped. hope for the best.
    if style == STYLE_HTML:
        return string.replace("<", "&lt;").replace(">", "&gt;")

    return string


def parse_entities(string, style=STYLE) -> Tuple[str, List[MessageEntity]]:
    """ convert in-string markup into message entities """
    if style is None:
        return string, []
    text, output_mode = render(string, style)

    if output_mode != STYLE_HTML:
        raise BadHerberror(f"Invalid output format {output_mode}, cannot parse entities")

    type_map = {
        'a': MessageEntity.URL,
        'i': MessageEntity.ITALIC,
        'b': MessageEntity.BOLD,
        'code': MessageEntity.CODE
    }

    class Parser(HTMLParser):
        """ handles the html tags in a message """
        def __init__(self):
            super().__init__()
            self.output = ''
            self.entities = []
            self.entity_stacks = dict()

        @property
        def output_pos(self):
            """
            return number of processed utf-16 code units
            """
            return utf16len(self.output)

        def handle_starttag(self, tag, attrs):
            if tag not in self.entity_stacks:
                self.entity_stacks[tag] = list()

            self.entity_stacks[tag].append(
                {
                    'start': self.output_pos,
                    'type': tag,
                    'attrs': dict(attrs)
                }
            )

        def handle_endtag(self, tag):
            if (tag not in self.entity_stacks or
                    len(self.entity_stacks[tag]) == 0):
                raise BadHerberror("Invalid markup generated: Illegal closing tag.")

            data = self.entity_stacks[tag].pop()

            if data['type'] not in type_map:
                raise BadHerberror("Invalid markup generated: Illegal tag type.")

            entity_type = type_map[data['type']]
            start = data['start']

            entity = MessageEntity(entity_type, start, self.output_pos - start)

            if entity_type == MessageEntity.URL:
                if 'href' in data['attrs']:
                    entity.url = data['attrs']['href']

            self.entities.append(entity)

        def handle_data(self, data):
            self.output += data

        def error(self, message):
            raise BadHerberror("Invalid markup generated")

    parser = Parser()
    parser.feed(text)
    return parser.output, parser.entities


def link_to(url, name=None, style=STYLE):
    """ return the link encoding of style to url shown as name """
    name = name or url
    try:
        return {
            STYLE_HTML: f'<a href="{url}">{name}</a>',
            STYLE_MD: f'[{name}]({url})',
            STYLE_BACKEND: f'!§![a{url}!§!|A{name}!§!]a',
        }[style]
    except KeyError as err:
        raise ValueError(f'Style {style} is undefined or cannot markup links.') from err


def _wrap_delimiters(style_dict: dict, text: str, escape=True, style=STYLE) -> str:
    try:
        prefix, suffix = style_dict[style]
        if escape:
            text = escape_string(text, style)

        return prefix + text + suffix

    except KeyError as err:
        raise ValueError(f'Style {style} is undefined.') from err


@as_partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<i>', '</i>'),
        STYLE_MD: ('_', '_'),
        STYLE_BACKEND: ('!§![i', '!§!]i'),
        STYLE_PARA: ('i§', '§')
    }
)
def italic(): """ adds italic formatting to the given text """


@as_partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<b>', '</b>'),
        STYLE_MD: ('*', '*'),
        STYLE_BACKEND: ('!§![b', '!§!]b'),
        STYLE_PARA: ('b§', '§')
    }
)
def bold(): """ adds bold formatting to the given text """


@as_partial(
    _wrap_delimiters,
    {
        STYLE_HTML: ('<code>', '</code>'),
        STYLE_MD: ('*', '*'),
        STYLE_BACKEND: ('!§![c', '!§!]c'),
        STYLE_PARA: ('i§', '§')
    }
)
def mono(): """ adds monospaced formatting to the given text """
