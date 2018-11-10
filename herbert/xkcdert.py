import json

from basebert import BaseBert, Herberror
from common import network, hercurles_utils
from decorators import command
import re


class XKCDert(BaseBert):
    @command(pass_string=True)
    def xkcd(self, string):
        """
        Retrieve a comic from www.xkcd.com, referenced by number or search query.
        """
        num = None
        try:
            num = int(float(string))
        except ValueError:
            results = hercurles_utils.search_for("xkcd " + string)
            for res in results:
                match = re.match(".*xkcd\.com/(\\d+)", res)
                if match:
                    num = match.group(1)
                    break

            if not num:
                raise Herberror("That is no comic.")

        url = f"www.xkcd.com/{num}/info.0.json"
        try:
            info_json = json.loads(network.t_load(url).data)
            self.send_photo(info_json.get('img'), caption=f"{info_json.get('title')}\n\n{info_json.get('alt')}")
        except json.decoder.JSONDecodeError:
            raise Herberror("That didn't work out, sorry.")


