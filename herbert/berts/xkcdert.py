"""
Bert

Looks up xkcd comics

provided commands:
    - xkcd
"""
import re
import json.decoder

from basebert import BaseBert
from herberror import Herberror
from common import hercurles_utils
from decorators import command, doc
import common.chatformat as cf


class XKCDert(BaseBert):
    """
    Wraps the xkcd command
    """

    @command(pass_string=True, allow_inline=True)
    @doc(
        f"""
        Retrieve a comic from www.xkcd.com, referenced by number or search query

        Retrieve a comic from www.xkcd.com. If the first parameter can be interpreted as a number, this loads the \
        corresponding comic; else, the argument string will be looked up on \
        {cf.link_to('http://www.duckduckgo.com/', name='DuckDuckGo')}, the first viable result will be returned.
        """
    )
    def xkcd(self, string):
        num = None
        try:
            num = int(float(string))
        except ValueError as err:
            results = hercurles_utils.search_for('xkcd ' + string)
            for res in results:
                match = re.match(r'.*xkcd\.com/(\d+)', res)
                if match:
                    num = match.group(1)
                    break

            if not num:
                raise Herberror('That is no comic.') from err

        url = f'www.xkcd.com/{num}/info.0.json'
        try:
            info_json = hercurles_utils.load_json(url)
            self.reply_photo_url(
                info_json.get('img'),
                caption=f"{num}: {info_json.get('title')}\n\n{info_json.get('alt')}"
            )

        except json.decoder.JSONDecodeError as err:
            raise Herberror("That didn't work out, sorry.") from err
