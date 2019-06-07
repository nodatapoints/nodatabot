import json.decoder

from basebert import InlineBaseBert, Herberror
from common import hercurles_utils
from decorators import command, doc
import re


class XKCDert(InlineBaseBert):
    @command(pass_string=True, allow_inline=True)
    @doc(
        """
        Retrieve a comic from www.xkcd.com, referenced by number or search query.
        """
    )
    def xkcd(self, string):
        num = None
        try:
            num = int(float(string))
        except ValueError:
            results = hercurles_utils.search_for('xkcd ' + string)
            for res in results:
                match = re.match(r'.*xkcd\.com/(\d+)', res)
                if match:
                    num = match.group(1)
                    break

            if not num:
                raise Herberror('That is no comic.')

        url = f'www.xkcd.com/{num}/info.0.json'
        try:
            info_json = hercurles_utils.load_json(url)
            self.reply_photo_url(
                info_json.get('img'),
                caption=f"{info_json.get('title')}\n\n{info_json.get('alt')}"
            )

        except json.decoder.JSONDecodeError:
            raise Herberror("That didn't work out, sorry.")
