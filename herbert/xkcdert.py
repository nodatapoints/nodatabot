import json

from basebert import BaseBert, Herberror
from common import network
from decorators import command


class XKCDert(BaseBert):
    @command(pass_args=True)
    def xkcd(self, args):
        """
        Retrieve a comic from www.xkcd.com, referenced by number.

        Search functionality coming soon.
        """
        try:
            num = int(float(args[0]))
            url = f"www.xkcd.com/{num}/info.0.json"
            info_json = json.loads(network.t_load(url).data)
            self.send_photo(info_json.get('img'), caption=f"{info_json.get('title')}\n\n{info_json.get('alt')}")
        except ValueError or json.decoder.JSONDecodeError as e:
            raise Herberror("That didn't work out, sorry.")


