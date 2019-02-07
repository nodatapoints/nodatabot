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
(and fix them yourself if you <i>actually</i> want to get them fixed)
"""

HERBERT_TITLE = chatformat.mono("""
 _  _         _             _   
| || |___ _ _| |__  ___ _ _| |_ 
| __ / -_) '_| '_ \/ -_) '_|  _|
|_||_\___|_| |_.__/\___|_|  \__|
""")
