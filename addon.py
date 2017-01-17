import sys
import os.path
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import streamlink
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
from urlparse import parse_qsl
from urllib import urlencode

# Get the plugin url in plugin:// notation.
pluginurl = sys.argv[0]
# Get the plugin handle as an integer number.
pluginhandle = int(sys.argv[1])
# Let kodi show the streams as a list of files
xbmcplugin.setContent(pluginhandle, 'tvshows')
#constants
uitzendingen_url = 'http://nos.nl/uitzending/nos-journaal.html'
nos_prefix = 'http://nos.nl'
regex_journaals = SoupStrainer(href=re.compile('/uitzending/[0-9]+-nos-journaal.html'))

def build_url(query):
    """
    build plugin url with the provided query
    :param query: dict
    :return: None
    """
    return (pluginurl + '?' + urlencode(query))

def list():
    """
    create root folder listing all possible streams
    :return: None
    """
    li = xbmcgui.ListItem('Laatste Journaal', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_url({'action':'latest'}), listitem=li)
    li = xbmcgui.ListItem('Acht uur Journaal', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_url({'action':'acht'}), listitem=li)

    journaals = get_journaals()
    for journaal in journaals:
        li = xbmcgui.ListItem(journaal['time'], iconImage='DefaultVideo.png')
        li.setProperty('IsPlayable', 'true')
        query = {'action': 'play', 'url':journaal['url']}
        xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_url(query), listitem=li)
    xbmcplugin.endOfDirectory(pluginhandle)

def parse_site():
    r = requests.get(uitzendingen_url)
    html = BeautifulSoup(r.text,'html.parser', parse_only=regex_journaals)
    return html

def get_journaals():
    """
    get a list of journaals from the url
    :return: list of dicts. dict has 'url' and 'time' keys
    """
    html = parse_site()
    journaals = []
    for link in html:
        journaal = {} 
        journaal['url'] = nos_prefix + link.get('href') 
        journaal['time'] = link.time.text.strip() 
        journaals.append(journaal)

    return journaals

def play_latest():
    html = parse_site()
    url = nos_prefix + html.a.get('href')
    play_stream(url)

def play_acht():
    html = parse_site()
    for link in html:
        if link.time.text.strip() == '20:00':
            play_stream(nos_prefix + link.get('href'))
            break

def play_stream(stream_url):
    """
    Resolve and play a stream at the provided url.
    :param stream_url: str
    :return: None
    """
    try:
        urls = streamlink.streams(stream_url)
    except streamlink.exceptions.NoPluginError:
        xbmcgui.Dialog().notification('Unable to play stream', 'no plugin for stream at {}'.format(stream_url), xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    url = urls['best'].url
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem=xbmcgui.ListItem(path=url))

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
        elif params['action'] == 'latest':
            play_latest()
        elif params['action'] == 'acht':
            play_acht()
        else:
            list()
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of streams
        list()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    router(sys.argv[2])
