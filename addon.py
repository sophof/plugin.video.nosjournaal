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
xbmcplugin.setContent(pluginhandle, 'video')
#constants
uitzendingen_url = 'http://nos.nl/uitzending/nos-journaal.html'
nos_prefix = 'http://nos.nl'
regex_journaals = SoupStrainer(href=re.compile('/uitzending/[0-9]+-nos-journaal.html'))

def list():
    """
    create root folder listing all possible streams
    :return: None
    """
    def build_plugin_url(action,url=None):
        query = {'action':action}
        if url: 
            query['url'] = url
        return (pluginurl + '?' + urlencode(query))
       
    li = xbmcgui.ListItem('Laatste Journaal', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    li.setInfo('video', infoLabels={'Title':'Laatste Journaal','mediatype':'video'})
    xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_plugin_url('latest'), listitem=li)
    li = xbmcgui.ListItem('Acht uur Journaal', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    li.setInfo('video', infoLabels={'Title':'Laatste Acht uur Journaal','mediatype':'video'})
    xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_plugin_url('acht'), listitem=li)

    for journaal in get_journaals():
        title = journaal['time'] + ' Journaal'
        li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', infoLabels={'Title':title,'mediatype':'video'})
        xbmcplugin.addDirectoryItem(handle=pluginhandle, url=build_plugin_url('play', url=journaal['url']), listitem=li)
    xbmcplugin.endOfDirectory(pluginhandle)

def get_journaals():
    """
    get an iterator over journaals from the url
    :return: an iterator over journaal dicts containing 'url' and 'time'
    """
    r = requests.get(uitzendingen_url)
    html = BeautifulSoup(r.text,'html.parser', parse_only=regex_journaals)
    for link in html:
        journaal = {}
        journaal['url'] = nos_prefix + link.get('href') 
        journaal['time'] = link.time.text.strip()
        yield journaal

def play_latest():
    for journaal in get_journaals():
        play_stream(journaal['url'])
        break #only do it for the first item in the list

def play_acht():
    for journaal in get_journaals():
        if journaal['time'] == '20:00':
            play_stream(journaal['url'])
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
