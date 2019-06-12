"""
Global Constants
"""
from common import chatformat

GITHUB_URL = 'http://www.github.com/nodatapoints/nodatabot'
GITHUB_REF = chatformat.link_to(GITHUB_URL, name="GitHub")
SEP_LINE = '———————————'

ERROR_FAILED = 'Oops, something went wrong! 😱'
ERROR_PREFIX = '💥'
BAD_ERROR_SUFFIX = f"""
{SEP_LINE}
You apparently found a bug.
Please report Bugs at {GITHUB_REF}, if you want to get them fixed
(and fix them yourself if you {chatformat.italic('actually')} want to get them fixed)
"""

OLD_HERBERT_TITLE = chatformat.mono("""
 _  _         _             _
| || |___ _ _| |__  ___ _ _| |_
| __ / -_) '_| '_ \\/ -_) '_|  _|
|_||_\\___|_| |_.__/\\___|_|  \\__|
""")

HERBERT_TITLE = chatformat.mono("""
 _  _        _          _
| || |__ _ _| |_ __ _ _| |_
| __ /._) '_| ' \\._) '_|  _|
|_||_\\__|_| |_._/__|_|  \\__|
""")

ERROR_TEMPLATE = """{} {}"""  # emoji, description
BAD_ERROR_TEMPLATE = ERROR_TEMPLATE + BAD_ERROR_SUFFIX

EMOJI_WARN = '⚠️'
EMOJI_EXPLOSION = '💥'

NUM_SUFFIXES = ['th', 'st', 'nd', 'rd']
FLAG_CHARS = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"

ONLY_BASIC_HELP = 42
