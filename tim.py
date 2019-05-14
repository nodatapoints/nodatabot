# i refuse to follow any python guidelines.
# comments are comments. strings are strings.

import urllib2


def curlmesome(url):
    response = urllib2.urlopen('http://python.org/')
    html = response.read()

