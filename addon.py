import sys
import os.path
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import streamlink
from urlparse import parse_qsl
from urllib import urlencode

# Get the plugin url in plugin:// notation.
pluginurl = sys.argv[0]
# Get the plugin handle as an integer number.
pluginhandle = int(sys.argv[1])
# Let kodi show the streams as a list of files
xbmcplugin.setContent(pluginhandle, 'tvshows')

def play_url(url):
    """
    build plugin url with action=play
    :param url: str
    :return: None
    """
    query = {'action': 'play', 'url':url}
    return (pluginurl + '?' + urlencode(query))

def list():
    """
    create root folder listing all possible streams
    :return: None
    """

def play_stream(stream_url):
    """
    Resolve and play a stream at the provided url.
    :param stream_url: str
    :return: None
    """
    
def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: str
    :return:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring[1:]))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'play':
            # Play a video from a provided URL.
            play_stream(params['url'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of streams
        list()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    router(sys.argv[2])