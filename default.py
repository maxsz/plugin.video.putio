import urllib,urllib2,re,xbmcplugin,xbmc,xbmcgui,xbmcaddon
import resources.lib.putio as putio

handle = int(sys.argv[1])
putio_addon = xbmcaddon.Addon("plugin.video.putio")

# Shows a notification
def showMessage(heading, message, duration):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, duration))

# Startup
api_key = putio_addon.getSetting("putio_api_key")
api_secret = putio_addon.getSetting("putio_api_secret")

while (api_key == "" and api_secret == ""):
	showMessage("Put.io Login Error", "Please enter your credentials before using put.io plugin", 15)
	putio_addon.openSettings()
	api_key = putio_addon.getSetting("putio_api_key")
	api_secret = putio_addon.getSetting("putio_api_secret")
	
api = putio.Api(api_key=api_key,api_secret=api_secret)

# List all items in dir with 'id' - pass in None if you want to list main menu
def listItems(id):
	try:
		if id != None:
			items = api.get_items(parent_id=id, offset=0)
		else:
			items = api.get_items(offset=0)

		for it in items:
			if it.type == 'folder': 
				li = xbmcgui.ListItem(it.name,iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				xbmcplugin.addDirectoryItem(handle=handle, url=sys.argv[0] + '?id=' + it.id, listitem=li, isFolder=True)    

			elif it.type == 'movie':
				li=xbmcgui.ListItem(it.name, iconImage="default.png", thumbnailImage=it.screenshot_url)
				li.setInfo(type="Video", infoLabels={ "Title": it.name })
				xbmcplugin.addDirectoryItem(handle=handle, url=it.get_stream_url(), listitem=li, isFolder=False)

			elif it.type == 'audio':
				li=xbmcgui.ListItem(it.name, iconImage="default.png", thumbnailImage=it.screenshot_url)
				li.setInfo(type="Audio", infoLabels={ "Title": it.name })
				xbmcplugin.addDirectoryItem(handle=handle, url=it.get_stream_url(), listitem=li, isFolder=False)
			
			# TODO: Images won't open
			# elif it.type == 'image':
			# 	li=xbmcgui.ListItem(it.name, iconImage="default.png", thumbnailImage=it.screenshot_url)
			# 	li.setInfo(type="Image", infoLabels={ "Title": it.name })
			# 	xbmcplugin.addDirectoryItem(handle=handle, url=it.get_stream_url(), listitem=li, isFolder=False)

		xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
	except putio.PutioError:
		showMessage("Put.io Communication Error", "Whoops, something went wrong. Did you enter api-key/-secret corretly?", 15)

# List items in dir with 'id'
def show_directory(id):
	item = api.get_items(id=id)[0]
	if item.is_dir:
		listItems(id=id)

# Borrowed from plugin.video.ccctv
def parameters_string_to_dict(parameters):
	''' Convert parameters encoded in a URL to a dict. '''
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

params = parameters_string_to_dict(sys.argv[2])
dirID = str(params.get("id", ""))
if not sys.argv[2]:
	# list main menu
    listItems(None)
else:
	# show current dir
    show_directory(dirID)
