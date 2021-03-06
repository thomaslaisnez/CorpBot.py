import asyncio
import discord
import random
import os
import configparser
import json
from discord.ext import commands
from discord import errors
import globals
from operator import itemgetter

import urllib.request
import urllib
import requests
import re
import webbrowser
import platform
import html
import math
import datetime as dt
import sys
import tempfile
import shutil
from os.path import splitext
from PIL import Image

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

  ###           ###
 # Dilbert Stuff #
###           ###

try:
    # Python 2.6-2.7
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser

import datetime

def get_ext(url):
    """Return the filename extension from url, or ''."""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext[1:]  # or ext if you want the leading '.'

def julianDate(my_date):
    # Takes a date string MM-DD-YYYY and
    # returns Julian Date
    date = my_date.split("-")

    month = int(date[0])
    day   = int(date[1])
    year  = int(date[2])

    month=(month-14)/12
    year=year+4800
    JDate=1461*(year+month)/4+367*(month-2-12*month)/12-(3*((year+month+100)/100))/4+day-32075
    return JDate

# Function from:  https://gist.github.com/jiffyclub/1294443
def date_to_jd(year,month,day):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5
    return jd

# Function from:  https://gist.github.com/jiffyclub/1294443
def jd_to_date(jd):
    jd = jd + 0.5
    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    day = C - E + F - math.trunc(30.6001 * G)
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
    return year, month, day

# Find string between 2 strings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_first_between( source, start_sep, end_sep ):
	result=[]
	tmp=source.split(start_sep)
	for par in tmp:
		if end_sep in par:
			result.append(par.split(end_sep)[0])
	if len(result) == 0:
		return None
	else:
		return result[0]

def find_last_between( source, start_sep, end_sep ):
	result=[]
	tmp=source.split(start_sep)
	for par in tmp:
		if end_sep in par:
			result.append(par.split(end_sep)[0])
	if len(result) == 0:
		return None
	else:
		return result[len(result)-1] # Return last item

def getImageHTML ( url ):
	try:
		with urllib.request.urlopen(url) as f:
			htmlSource = str(f.read())
			return htmlSource
	except:
		return None

def getImageURL ( html ):
    imageURL = find_between( html, "data-image=", "data-date=" )
    return imageURL.replace('"', '').strip()

def getImageTitle ( html ):
    imageTitle = find_between( html, "data-title=", "data-tags=" )
    h = HTMLParser()
    imageTitle = h.unescape(imageTitle)
    #print(h.unescape(imageTitle))
    return imageTitle.replace('"', '').strip()

# C&H Methods

def getCHURL ( html, date ):
	# YYYY.MM.DD format
	# <a href="[comic url]">2005.01.31</a>
	comicBlock = find_last_between( html, '<a href="', "\">" + date + "</a>")
	
	if comicBlock == None:
		return None
	else:
		return comicBlock.replace('"', '').strip()
		
		
def getCHImageURL ( html ):
	# comicBlock = find_last_between( html, 'div id="comic-container"', "</div>")
	
	# if comicBlock == None:
		# return None
	
	imageURL = find_last_between( html, 'id="main-comic" src=', '>' )
	
	if imageURL == None:
		return None
	
	imageURL = imageURL.replace('"', '').strip()
	
	imageURL = imageURL.split("?t=")[0]
	
	if imageURL[0:2] == "//":
		# Add http?
		imageURL = "http:" + imageURL
	if imageURL[-1:] == "/":
		# Strip trailing /
		return imageURL[0:-1]
	else:
		return imageURL

	
# XKCD Methods	

def getNewestXKCD ( html ):
	comicBlock = find_last_between( html, 'div id="middleContainer"', "</div>")
	
	if comicBlock == None:
		return None
	
	imageURL = find_first_between( comicBlock, "href=", " title=" )
	imageURL = imageURL.replace('/', '').strip()
	return imageURL.replace('"', '').strip()
	
def getXKCDURL ( html, date ):
	# YYYY-M(M)-D(D) format
	# <a href="/17/" title="2006-1-1">What If</a>
	comicBlock = find_last_between( html, 'div id="comic"', "</div>")
	
	if comicBlock == None:
		return None
	
	imageURL = find_first_between( html, "href=", " title=\"" + date + "\"" )
	if imageURL == None:
		return None
	else:
		return imageURL.replace('"', '').strip()

def getXKCDImageURL ( html ):
	comicBlock = find_last_between( html, 'div id="comic"', "</div>")
	
	if comicBlock == None:
		return None
	
	imageURL = find_last_between( comicBlock, "img src=", "title=" )
	imageURL = imageURL.replace('"', '').strip()
	
	if imageURL[0:2] == "//":
		# Add http?
		return "http:" + imageURL
	else:
		return imageURL

def getXKCDImageTitle ( html ):
	comicBlock = find_last_between( html, 'div id="comic"', "</div>")
	
	if comicBlock == None:
		return None
	
	imageTitle = find_last_between( comicBlock, "alt=", ">" )
	h = HTMLParser()
	imageTitle = h.unescape(imageTitle)
	imageTitle = imageTitle.replace('"', '').strip()
	imageTitle = imageTitle.replace('/', '').strip()
	return imageTitle

# Garfield Minus Garfield Methods

def getGMGImageURL ( html ):
	comicBlock = find_last_between( html, 'div class="photo"', "</a>")
	
	if comicBlock == None:
		return None
	
	imageURL = find_last_between( comicBlock, "img src=", " alt=" )
	imageURL = imageURL.replace('"', '').strip()
	
	return imageURL	
	

	
# Download image to location
def downloadImage( url, fileName ):
    with urllib.request.urlopen(url) as f:
        htmlSource = str(f.read())
        imageURL = find_between( htmlSource, "data-image=", "data-date=" )
        urlNoQuotes = imageURL.replace('"', '').strip()
        #print("Image URL: " + str(urlNoQuotes))
        #webbrowser.open(urlNoQuotes)
        urllib.request.urlretrieve(urlNoQuotes, fileName)

def downloadImageTo( url, fileName ):
    urllib.request.urlretrieve(url, fileName)

  ###           ###
 # Dilbert Stuff #
###           ###



def to_python(image, size):
	limit = size # 500000 = 500kb
	img = Image.open(image)
	image = Image.open(image)
	width, height = img.size
	ratio = float(width) / float(height)
	quality = 100
	while len(image.read()) > limit:
		width -= 100
		quality -= 10
		height = int(width / ratio)
		img.resize((width, height), Image.ANTIALIAS)
		img.save(image.name, "JPEG", quality=quality)
		image = open(image.name)
		# reset the file pointer to the beginning so the while loop can read properly
		image.seek(0)
	return image








bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description='A that does stuff.... probably')
settingsFile = "./Settings.txt"
userFile = "./Users.txt"
jsonFile = "Settings.json"
globals.serverList = {}

  ###           ###
 # Initial Setup #
###           ###

def checkServer(server, serverDict):
    # Assumes server = discord.Server and serverList is a dict
    if not "Servers" in serverDict:
        # Let's add an empty placeholder
        serverDict["Servers"] = []
    found = False
    for x in serverDict["Servers"]:
        if x["Name"] == server.name:
            # We found our server
            found = True
            # print("Found our server: " + server.name)

    if found == False:
        # We didn't locate our server
        # print("Server not located, adding...")
        newServer = { "Name" : server.name, "ID" : server.id,
											"AutoRole" : "No", # No/ID/Position
											"DefaultRole" : "1",
											"AdminLock" : "No",
											"MinimumXPRole" : "1",
											"RequiredLinkRole" : "", #ID or blank for Admin-Only
											"RequiredHackRole" : "", #ID or blank for Admin-Only
											"XPApprovalChannel" : "",
											"LastAnswer" : "",
											"HourlyXP" : "1",
											"IncreasePerRank" : "1",
											"RequireOnline" : "Yes",
											"AdminUnlimited" : "Yes",
											"XPPromote" : "Yes",
											"PromoteBy" : "Array", # Position/Array
											"MaxPosition" : "5",
											"RequiredXP" : "0",
											"DifficultyMultiplier" : "0",
											"PadXPRoles" : "0",
											"XPDemote" : "No",
											"Rules" : "Be nice to each other.",
											"PromotionArray" : [],
											"Hacks" : [],
											"Links" : [],
											"Members" : [],
											"AdminArray" : [],
											"ChannelMOTD" : []}
        serverDict["Servers"].append(newServer)

    return serverDict

def checkUser(user, server, serverDict):
	# Make sure our server exists in the list
	serverDict = checkServer(server, serverDict)
	# Check for our username
	found = False
	for x in serverDict["Servers"]:
		if x["ID"] == server.id:
			# We found our server, now to iterate users
			for y in x["Members"]:
				if y["ID"] == user.id:
					found = True
					# Check XP, ID, Discriminator
					if not "XP" in y:
						# print("No XP - adding...")
						y["XP"] = 0
					if not "XPReserve" in y:
						# print("No XP - adding...")
						y["XPReserve"] = 10
					if not "ID" in y:
						# print("No ID - adding...")
						y["ID"] = user.id
					if not "Discriminator" in y:
						# print("No Discriminator - adding...")
						y["Discriminator"] = user.discriminator
					# print("Found our user: " + userName)
					if not "Name" in y:
						y["Name"] = user.name
					if not "DisplayName" in y:
						y["DisplayName"] = user.display_name
					if not "Parts" in y:
						y["Parts"] = ""
					if not "Muted" in y:
						y["Muted"] = "No"
					if not "LastOnline" in y:
						y["LastOnline"] = "Unknown"
			if not found:
				# We didn't locate our user - add them
				newUser = { "Name" : user.name,
							"DisplayName" : user.display_name,
							"XP" : 0,
							"XPReserve" : 10,
							"ID" : user.id,
							"Discriminator" : user.discriminator }
				x["Members"].append(newUser)
	# All done - return
	return serverDict

def incrementStat(user, server, serverDict, stat, incrementAmount):
    serverDict = checkUser(user, server, serverDict)
    for x in serverDict["Servers"]:
        if x["ID"] == server.id:
            # We found our server, now to iterate users
            for y in x["Members"]:
                if y["ID"] == user.id:
                    tempStat = int(y[stat])
                    tempStat += int(incrementAmount)
                    y[stat] = tempStat
    return serverDict

def getUserStat(user, server, serverDict, stat):
	# Make sure our server exists in the list
	serverDict = checkServer(server, serverDict)
	# Check for our username
	found = False
	for x in serverDict["Servers"]:
		if x["ID"] == server.id:
			# We found our server, now to iterate users
			for y in x["Members"]:
				if y["ID"] == user.id:
					return y[stat]
	return None

def setUserStat(user, server, serverDict, stat, value):
	# Make sure our server exists in the list
	serverDict = checkServer(server, serverDict)
	# Check for our username
	found = False
	for x in serverDict["Servers"]:
		if x["ID"] == server.id:
			# We found our server, now to iterate users
			for y in x["Members"]:
				if y["ID"] == user.id:
					y[stat] = value

def getServerStat(server, serverDict, stat):
	# Make sure our server exists in the list
	serverDict = checkServer(server, serverDict)
	# Check for our username
	found = False
	for x in serverDict["Servers"]:
		if x["ID"] == server.id:
			# We found our server, now to iterate users
			return x[stat]
	return None

def setServerStat(server, serverDict, stat, value):
	# Make sure our server exists in the list
	serverDict = checkServer(server, serverDict)
	# Check for our username
	found = False
	for x in serverDict["Servers"]:
		if x["ID"] == server.id:
			# We found our server, now to iterate users
			x[stat] = value

async def flushSettings():
	while not bot.is_closed:
		print("Flushed Settings")
		# print("ServerList Flush: {}".format(globals.serverList))
		# Dump the json
		json.dump(globals.serverList, open(jsonFile, 'w'), indent=2)
		await asyncio.sleep(900) # runs only every 15 minutes
	'''await bot.wait_until_ready()
	counter = 0
	channel = discord.Object(id='channel_id_here')
	while not bot.is_closed:
		counter += 1
		await bot.send_message(channel, counter)
		await asyncio.sleep(900) # task runs every 15 minutes'''

async def addXP():
	while not bot.is_closed:
		await asyncio.sleep(3600) # runs only every 1 minute  #### CHANGE TO 3600 AT SOME POINT ####

		print("Adding XP: {}".format(datetime.datetime.now().time().isoformat()))
		
		for server in bot.servers:

			#for role in server.roles:
				#if role.position == 1:
					# print("Entry role: {}".format(role.name))

			# Iterate through the servers and add them
			globals.serverList = checkServer(server, globals.serverList)
			xpAmount = getServerStat(server, globals.serverList, "HourlyXP")
			onlyOnline = getServerStat(server, globals.serverList, "RequireOnline")
			for user in server.members:
				# print('{}: {}'.format(user.name, str(user.status)))
				bumpXP = False
				if onlyOnline.lower() == "yes":
					if str(user.status).lower() == "online":
						bumpXP = True
				else:
					bumpXP = True

				if bumpXP:
					boost = int(getServerStat(server, globals.serverList, "IncreasePerRank"))
					maxPos = int(getServerStat(server, globals.serverList, "MaxPosition"))
					biggest = 0
					xpPayload = 0
					for role in user.roles:
						if role.position <= maxPos and role.position > biggest:
							biggest = role.position

					# xpPayload = int(xpAmount)+biggest*boost

					xpPayload = int(xpAmount)

					#print("{} at level {} out of {}, gets {} XP".format(user.id, biggest, maxPos, xpPayload))

					globals.serverList = incrementStat(user, server, globals.serverList, "XPReserve", xpPayload)

		await quickFlush()
		
async def checkMOTD():		
	# print("MOTD Called")
	
	while not bot.is_closed:
		await asyncio.sleep(300)
		await quickMOTD()
		
					
async def quickMOTD():
	# print("MOTD Called")
	for server in bot.servers:
			
		globals.serverList = checkServer(server, globals.serverList)
		try:
			channelMOTDList = getServerStat(server, globals.serverList, "ChannelMOTD")
		except KeyError:
			channelMOTDList = []
		
		# print(channelMOTDList)
		
		if len(channelMOTDList) > 0:
			members = 0
			membersOnline = 0
			for member in server.members:
				members += 1
				if str(member.status).lower() == "online":
					membersOnline += 1
			
		for id in channelMOTDList:
			channel = bot.get_channel(id['ID'])
			# print(channel.id)
			if channel:
				# Got our channel - let's update
				motd = id['MOTD'] # A markdown message of the day
				listOnline = id['ListOnline'] # Yes/No - do we list all online members or not?
					
				if listOnline.lower() == "yes":
					msg = '{} - ({}/{} users online)'.format(motd, int(membersOnline), int(members))
				else:
					msg = motd
						
				# print(msg)
						
				await bot.edit_channel(channel, topic=msg)			


async def quickFlush():
	# Dump the json
	json.dump(globals.serverList, open(jsonFile, 'w'), indent=2)

# --------------------------------------------- #

  ###                        ###
 # BEGIN: Setup for Playlists #
###                        ###

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.

    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.

        If there is a song currently in the queue, then it is
        queued until the next song is done playing.

        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.

        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.

        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing anything right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about currently playing."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))

  ###                      ###
 # END: Setup for Playlists #
###                      ###

# --------------------------------------------- #

  ###           ###
 # BEGIN: Events #
###           ###

@bot.event
async def on_member_join(member):
	server = member.server

	# Initialize User
	globals.serverList = checkUser(member, server, globals.serverList)

	fmt = 'Welcome *{}* to *{}*!'.format(member.name, server.name)
	await bot.send_message(server, fmt.format(member, server))
	# Scan through roles - find "Entry Level" and set them to that

	autoRole = getServerStat(server, globals.serverList, "AutoRole")
	defaultRole = getServerStat(server, globals.serverList, "DefaultRole")
	rules = getServerStat(member.server, globals.serverList, "Rules")
	
	if autoRole.lower() == "position":
		newRole = discord.utils.get(server.roles, position=int(defaultRole))
		await bot.add_roles(member, newRole)
		fmt = 'You\'ve been auto-assigned the role *{}*!'.format(newRole.name)
		await bot.send_message(server, fmt)
	elif autoRole.lower() == "id":
		newRole = discord.utils.get(server.roles, id=defaultRole)
		await bot.add_roles(member, newRole)
		fmt = 'You\'ve been auto-assigned the role *{}*!'.format(newRole.name)
		await bot.send_message(server, fmt)

	fmt = 'Type `$quickhelp` for a list of available user commands.'
	await bot.send_message(server, fmt)

	# PM User
	fmt = "*{}* Rules:\n{}".format(server.name, rules)
	await bot.send_message(member, fmt)
	
	await quickFlush()

@bot.event
async def on_member_update(before, after):
	server = before.server
			
	globals.serverList = checkServer(server, globals.serverList)
	try:
		channelMOTDList = getServerStat(server, globals.serverList, "ChannelMOTD")
	except KeyError:
		channelMOTDList = []
		
	# print(channelMOTDList)
		
	if len(channelMOTDList) > 0:
		members = 0
		membersOnline = 0
		for member in server.members:
			members += 1
			if str(member.status).lower() == "online":
				membersOnline += 1
			
	for id in channelMOTDList:
		channel = bot.get_channel(id['ID'])
		# print(channel.id)
		if channel:
			# Got our channel - let's update
			motd = id['MOTD'] # A markdown message of the day
			listOnline = id['ListOnline'] # Yes/No - do we list all online members or not?
					
			if listOnline.lower() == "yes":
				msg = '{} - ({}/{} users online)'.format(motd, int(membersOnline), int(members))
			else:
				msg = motd
						
			# print(msg)
						
			await bot.edit_channel(channel, topic=msg)	

@bot.event
async def on_ready():
	print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
	# Now we give JSON a try
	if os.path.exists(jsonFile):
		globals.serverList = json.load(open(jsonFile))
	else:
		# No Users.json file - create a placeholder
		globals.serverList = {}

	for server in bot.servers:
		# Iterate through the servers and add them
		globals.serverList = checkServer(server, globals.serverList)
		for user in server.members:
			globals.serverList = checkUser(user, server, globals.serverList)

	# await flushSettings()
	bot.loop.create_task(flushSettings())
	bot.loop.create_task(addXP())
	#bot.loop.create_task(checkMOTD())

@bot.event
async def on_message(message):
	# Process commands - then check for mentions
	if not message.server:
		# This wasn't said in a server, process commands, then return
		await bot.process_commands(message)
		return
	
	# Initialize User
	globals.serverList = checkUser(message.author, message.server, globals.serverList)
	
	# Check if user is muted
	isMute = getUserStat(message.author, message.server, globals.serverList, "Muted")
	if isMute.lower() == "yes":
		# print('{} is muted.  Deleting message....'.format(message.author))
		isAdmin = message.author.permissions_in(message.channel).administrator
		if not isAdmin:
			checkAdmin = getServerStat(message.server, globals.serverList, "AdminArray")
			for role in message.author.roles:
				for aRole in checkAdmin:
					# Get the role that corresponds to the id
					if aRole['ID'] == role.id:
						isAdmin = True
		# Only mute non-admins
		if not isAdmin:
			await bot.delete_message(message)
	
	# Check for AdminLock
	needAdmin = getServerStat(message.server, globals.serverList, "AdminLock")
	if needAdmin.lower() == "yes":
		isAdmin = message.author.permissions_in(message.channel).administrator
		# Only allow admins to call the bot
		if not isAdmin:
			# await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	
	await bot.process_commands(message)

	'''if message.author == bot.user:
		return

	for user in message.mentions:
		print('User: {}'.format(user.name))
		if user == bot.user:
			msg = 'Hello {0.author.mention}'.format(message)
			await bot.send_message(message.channel, msg)'''
	# For adding roles - http://discordpy.readthedocs.io/en/latest/api.html#discord.Client.add_roles

  ###           ###
 # END:   Events #
###           ###

# --------------------------------------------- #

  ###             ###
 # BEGIN: Commands #
###             ###

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.command(pass_context=True)
async def getoffline(ctx):
	"""Forces the server to account for offline members - only important to the backend."""
	theServer = ctx.message.author.server
	#print("Hello")
	await bot.request_offline_members(theServer)
	for user in theServer.members:
		print('User: {}'.format(user.name))
	#print('{}'.format(theServer.members))


@bot.command(pass_context=True)
async def playgame(ctx, game : str = None):
	"""Sets the playing status of the bot (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if game == None:
		await bot.change_status(game=None)
		return

	await bot.change_status(game=discord.Game(name=game))



@bot.command(pass_context=True)
async def setxp(ctx, member : discord.Member = None, xpAmount : int = None):
	"""Sets an absolute value for the member's xp (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	# Check for formatting issues
	if xpAmount == None or member == None:
		msg = 'Usage: `$setxp [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if not type(xpAmount) is int:
		msg = 'Usage: `$setxp [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if xpAmount < 0:
		msg = 'Usage: `$setxp [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	setUserStat(member, ctx.message.server, globals.serverList, "XP", xpAmount)
	msg = '{}\'s xp was set to *{}!*'.format(member.name, xpAmount)
	await bot.send_message(ctx.message.channel, msg)


@setxp.error
async def setxp_error(ctx, error):
    # do stuff
	msg = 'setxp Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def setxpreserve(ctx, member : discord.Member = None, xpAmount : int = None):
	"""Set's an absolute value for the member's xp reserve (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	# Check for formatting issues
	if xpAmount == None or member == None:
		msg = 'Usage: `$setxpreserve [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if not type(xpAmount) is int:
		msg = 'Usage: `$setxpreserve [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if xpAmount < 0:
		msg = 'Usage: `$setxpreserve [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	setUserStat(member, ctx.message.server, globals.serverList, "XPReserve", xpAmount)
	msg = '{}\'s XPReserve was set to {}!'.format(member.name, xpAmount)
	await bot.send_message(ctx.message.channel, msg)


@setxpreserve.error
async def setxpreserve_error(ctx, error):
    # do stuff
	msg = 'setxp Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def xp(ctx, member : discord.Member = None, xpAmount : int = None):
	"""Gift xp to other members."""
	# Check for formatting issues
	if xpAmount == None or member == None:
		msg = 'Usage: `$xp [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if not type(xpAmount) is int:
		msg = 'Usage: `$xp [member] [amount]`'
		await bot.send_message(ctx.message.channel, msg)
		return
	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return


	# Initialize User
	globals.serverList = checkUser(member, ctx.message.server, globals.serverList)

	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	adminUnlim = getServerStat(ctx.message.server, globals.serverList, "AdminUnlimited")
	reserveXP = getUserStat(ctx.message.author, ctx.message.server, globals.serverList, "XPReserve")
	minRole = getServerStat(ctx.message.server, globals.serverList, "MinimumXPRole")

	approve = True
	decrement = True

	# MinimumXPRole
	if ctx.message.author.top_role.position < int(minRole):
		approve = False
		msg = 'You don\'t have the permissions to give xp.'

	if xpAmount > int(reserveXP):
		approve = False
		msg = 'You can\'t give *{} xp*, you only have *{}!*'.format(xpAmount, reserveXP)

	if ctx.message.author == member:
		approve = False
		msg = 'You can\'t give yourself xp!  *Nice try...*'

	if xpAmount < 0:
		msg = 'Only admins can take away xp!'
		approve = False

	# Check admin last - so it overrides anything else
	if isAdmin and adminUnlim.lower() == "yes":
		# No limit - approve
		approve = True
		decrement = False

	userRole = member.top_role.position

	if approve:
		msg = '{} was given *{} xp!*'.format(member.name, xpAmount)
		globals.serverList = incrementStat(member, ctx.message.server, globals.serverList, "XP", xpAmount)
		if decrement:
			globals.serverList = incrementStat(ctx.message.author, ctx.message.server, globals.serverList, "XPReserve", (-1*xpAmount))

		xpPromote = getServerStat(ctx.message.server, globals.serverList, "XPPromote")
		xpDemote = getServerStat(ctx.message.server, globals.serverList, "XPDemote")
		promoteBy = getServerStat(ctx.message.server, globals.serverList, "PromoteBy")
		requiredXP = int(getServerStat(ctx.message.server, globals.serverList, "RequiredXP"))
		maxPosition = getServerStat(ctx.message.server, globals.serverList, "MaxPosition")
		padXP = getServerStat(ctx.message.server, globals.serverList, "PadXPRoles")
		difficulty = int(getServerStat(ctx.message.server, globals.serverList, "DifficultyMultiplier"))

		userXP = getUserStat(member, ctx.message.server, globals.serverList, "XP")
		userXP = int(userXP)+(int(requiredXP)*int(padXP))

		if xpPromote.lower() == "yes":
			# We use XP to promote - let's check our levels
			if promoteBy.lower() == "position":
				# We use the position to promote
				gotLevels = 0
				for x in range(0, int(maxPosition)+1):
					# Let's apply our difficulty multiplier

					# print("{} + {}".format((requiredXP*x), ((requiredXP*x)*difficulty)))

					required = (requiredXP*x) + (requiredXP*difficulty)
					# print("Level: {}\nXP: {}".format(x, required))
					if userXP >= required:
						gotLevels = x
				if gotLevels > int(maxPosition):
					# If we got too high - let's even out
					gotLevels = int(maxPosition)
				#print("Got: {} Have: {}".format(gotLevels, userRole))
				#if gotLevels > userRole:
					# We got promoted!
					#msg = '{} was given {} xp, and was promoted to {}!'.format(member.name, xpAmount, discord.utils.get(ctx.message.server.roles, position=gotLevels).name)
				gotLevels+=1
				for x in range(0, gotLevels):
					# fill in all the roles between
					for role in ctx.message.server.roles:
						if role.position < gotLevels:
							if not role in member.roles:
								# Only add if we need to
								await bot.add_roles(member, role)
								msg = '{} was given *{} xp*, and was promoted to {}!'.format(member.name, xpAmount, discord.utils.get(ctx.message.server.roles, position=gotLevels).name)
			elif promoteBy.lower() == "array":
				promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")
				serverRoles = ctx.message.server.roles
				for role in promoArray:
					# Iterate through the roles, and add what we can
					if int(role['XP']) <= userXP:
						# We *can* have this role, let's see if we already do
						currentRole = None
						for aRole in serverRoles:
							# Get the role that corresponds to the id
							if aRole.id == role['ID']:
								# We found it
								currentRole = aRole

						# Now see if we have it, and add it if we don't
						if not currentRole in member.roles:
							await bot.add_roles(member, currentRole)
							msg = '{} was given *{} xp*, and was promoted to {}!'.format(member.name, xpAmount, currentRole.name)
					else:
						if xpDemote.lower() == "yes":
							# Let's see if we have this role, and remove it.  Demote time!
							currentRole = None
							for aRole in serverRoles:
								# Get the role that corresponds to the id
								if aRole.id == role['ID']:
									# We found it
									currentRole = aRole

							# Now see if we have it, and add it if we don't
							if currentRole in member.roles:
								await bot.remove_roles(member, currentRole)
								msg = '{} was demoted from {}!'.format(member.name, currentRole.name)


	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()

@xp.error
async def getxp_error(ctx, error):
    # do stuff
	msg = 'xp Error: {}'.format(ctx)
	await bot.say(msg)

@bot.command(pass_context=True)
async def removemotd(ctx, channel : discord.Channel = None):
	"""Removes the message of the day from the selected channel."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	if channel == None:
		msg = 'Usage: `$removemotd [channel]`'
		await bot.send_message(ctx.message.channel, msg)
		return	
	if type(channel) is str:
		try:
			channel = discord.utils.get(message.server.channels, name=channel)
		except:
			print("That channel does not exist")
			return
	# At this point - we should have the necessary stuff
	motdArray = getServerStat(ctx.message.server, globals.serverList, "ChannelMOTD")
	for a in motdArray:
		# Get the channel that corresponds to the id
		if a['ID'] == channel.id:
			# We found it - throw an error message and return
			motdArray.remove(a)
			setServerStat(ctx.message.server, globals.serverList, "ChannelMOTD", motdArray)
			
			msg = 'MOTD for {} removed.'.format(channel.name)
			await bot.send_message(ctx.message.channel, msg)
			await bot.edit_channel(channel, topic=None)
			await quickMOTD()
			await flushSettings()
			return		
	msg = 'MOTD for {} not found.'.format(channel.name)
	await bot.send_message(ctx.message.channel, msg)
	return		
	
@removemotd.error
async def removemotd_error(ctx, error):
    # do stuff
	msg = 'removemotd Error: {}'.format(ctx)
	await bot.say(msg)	
			
			
	
@bot.command(pass_context=True)
async def setmotd(ctx, channel : discord.Channel = None, message : str = None, users : str = "No"):
	"""Adds a message of the day to the selected channel."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	if channel == None or message == None:
		msg = 'Usage: `$setmotd [channel] "[message]" [usercount Yes/No (default is No)]`'
		await bot.send_message(ctx.message.channel, msg)
		return	
	if type(channel) is str:
		try:
			channel = discord.utils.get(message.server.channels, name=channel)
		except:
			print("That channel does not exist")
			return
	
	# At this point - we should have the necessary stuff
	motdArray = getServerStat(ctx.message.server, globals.serverList, "ChannelMOTD")
	for a in motdArray:
		# Get the channel that corresponds to the id
		if a['ID'] == channel.id:
			# We found it - throw an error message and return
			
			a['MOTD'] = message
			a['ListOnline'] = users
			setServerStat(ctx.message.server, globals.serverList, "ChannelMOTD", motdArray)
			
			msg = 'MOTD for {} changed.'.format(channel.name)
			await bot.send_message(ctx.message.channel, msg)
			await quickMOTD()
			await flushSettings()
			return

	# If we made it this far - then we can add it
	motdArray.append({ 'ID' : channel.id, 'MOTD' : message, 'ListOnline' : users })
	setServerStat(ctx.message.server, globals.serverList, "ChannelMOTD", motdArray)

	msg = 'MOTD for {} added.'.format(channel.name)
	await bot.send_message(ctx.message.channel, msg)
	await quickMOTD()
	await flushSettings()
	return

	
@setmotd.error
async def setmotd_error(ctx, error):
    # do stuff
	msg = 'setmotd Error: {}'.format(ctx)
	await bot.say(msg)		


@bot.command(pass_context=True)
async def addrole(ctx, role : discord.Role = None, xp : int = None):
	"""Adds a new role to the xp promotion/demotion system (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None or xp == None:
		msg = 'Usage: `$addrole [role] [required xp]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if not type(xp) is int:
		msg = 'Usage: `$addrole [role] [required xp]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# Now we see if we already have that role in our list
	promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")

	for aRole in promoArray:
		# Get the role that corresponds to the id
		if aRole['ID'] == role.id:
			# We found it - throw an error message and return
			msg = '{} is already in the list.  Required xp: {}'.format(role.name, aRole['XP'])
			await bot.send_message(ctx.message.channel, msg)
			return

	# If we made it this far - then we can add it
	promoArray.append({ 'ID' : role.id, 'Name' : role.name, 'XP' : xp })
	setServerStat(ctx.message.server, globals.serverList, "PromotionArray", promoArray)

	msg = '{} added to list.  Required xp: {}'.format(role.name, xp)
	await bot.send_message(ctx.message.channel, msg)
	return

@addrole.error
async def addrole_error(ctx, error):
    # do stuff
	msg = 'addrole Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def listroles(ctx):
	"""Lists all roles, id's, and xp requirements for the xp promotion/demotion system."""
	promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")
	
	# rows_by_lfname = sorted(rows, key=itemgetter('lname','fname'))
	
	promoSorted = sorted(promoArray, key=itemgetter('XP', 'Name'))
	
	roleText = "Current Roles:\n"

	for arole in promoSorted:
		roleText = '{}**{}** : *{} XP* (ID : `{}`)\n'.format(roleText, arole['Name'], arole['XP'], arole['ID'])

	await bot.send_message(ctx.message.channel, roleText)




@bot.command(pass_context=True)
async def removerole(ctx, role : discord.Role = None):
	"""Removes a role from the xp promotion/demotion system (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None:
		msg = 'Usage: `$removerole [role]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# If we're here - then the role is a real one
	promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")

	for aRole in promoArray:
		# Get the role that corresponds to the id
		if aRole['ID'] == role.id:
			# We found it - let's remove it
			promoArray.remove(aRole)
			setServerStat(ctx.message.server, globals.serverList, "PromotionArray", promoArray)
			msg = '{} removed successfully.'.format(aRole['Name'])
			await bot.send_message(ctx.message.channel, msg)
			return

	# If we made it this far - then we didn't find it
	msg = '{} not found in list.'.format(aRole['Name'])
	await bot.send_message(ctx.message.channel, msg)

@removerole.error
async def removerole_error(ctx, error):
    # do stuff
	msg = 'removerole Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def autorole(ctx, setting : str = None, role : discord.Role = None):
	"""Sets the autorole value - can be No, ID, or Position (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	usageMessage = 'Usage: `$autorole [No/ID/Position] [role]`'
	if setting == None:
		await bot.send_message(ctx.message.channel, usageMessage)
		return

	if not type(setting) == str:
		await bot.send_message(ctx.message.channel, usageMessage)
		return

	if setting.lower() == "no":
		# We don't need a second var
		setServerStat(ctx.message.server, globals.serverList, "AutoRole", "No")
		msg = 'AutoRole set to No'
		await bot.send_message(ctx.message.channel, msg)
		return

	if role == None:
		await bot.send_message(ctx.message.channel, usageMessage)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, id=role)
		except:
			print("That role does not exist")
			return

	if setting.lower() == "id":
		# Found the role!  Let's add it
		setServerStat(ctx.message.server, globals.serverList, "AutoRole", "ID")
		setServerStat(ctx.message.server, globals.serverList, "DefaultRole", '{}'.format(role.id))
		msg = 'AutoRole set to ID: {}'.format(role.id)
		await bot.send_message(ctx.message.channel, msg)
		return

	if setting.lower() == "position":
		# Found the role!  Let's add it
		setServerStat(ctx.message.server, globals.serverList, "AutoRole", "Position")
		setServerStat(ctx.message.server, globals.serverList, "DefaultRole", str(role.position))
		msg = 'AutoRole set to Position: {}'.format(role.position)
		await bot.send_message(ctx.message.channel, msg)
		return

	await bot.send_message(ctx.message.channel, usageMessage)
	return


@autorole.error
async def autorole_error(ctx, error):
    # do stuff
	msg = 'autorole Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def stats(ctx, member: discord.Member = None):
	"""List the xp and xp reserve of a listed member."""
	# await bot.say("You tried this")
	if member is None:
		member = ctx.message.author
		#await bot.say('Usage: `$stats [member]`')
		#return
	#if member is None:
	#	bot.say("Usage: $stats @MemberName")
	#	return

	# Ensure user is setup
	globals.serverList = checkUser(member, ctx.message.server, globals.serverList)
	# Get user's xp
	newStat = getUserStat(member, ctx.message.server, globals.serverList, "XP")
	newState = getUserStat(member, ctx.message.server, globals.serverList, "XPReserve")

	msg = '{} has *{} xp*, and can gift up to *{} xp!*'.format(member.name, newStat, newState)
	await bot.send_message(ctx.message.channel, msg)
	
@bot.command(pass_context=True)
async def rank(ctx, member: discord.Member = None):
	"""Say the highest rank of a listed member."""
	
	if member is None:
		member = ctx.message.author
		
	promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")
	# rows_by_lfname = sorted(rows, key=itemgetter('lname','fname'))
	promoSorted = sorted(promoArray, key=itemgetter('XP', 'Name'))
	
	highestRole = ""
	
	for role in promoSorted:
		# We *can* have this role, let's see if we already do
		currentRole = None
		for aRole in member.roles:
			# Get the role that corresponds to the id
			if aRole.id == role['ID']:
				# We found it
				highestRole = aRole.name

	if highestRole == "":
		msg = '{} has not acquired a rank yet.'.format(member.name)
	else:
		msg = '{} is a **{}**'.format(member.name, highestRole)
		
	await bot.send_message(ctx.message.channel, msg)



@bot.command(pass_context=True)
async def getstat(ctx, stat : str = None, member : discord.Member = None):
	"""Gets the value for a specific stat for the listed member (case-sensitive)."""
	if member == None:
		member = ctx.message.author

	if str == None:
		msg = 'Usage: `$getstat [stat] [member]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	if member is None:
		msg = 'Usage: `$getstat [stat] [member]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	try:
		newStat = getUserStat(member, ctx.message.author.server, globals.serverList, stat)
	except KeyError:
		msg = '"{}" is not a valid stat for {}'.format(stat, member.name)
		await bot.send_message(ctx.message.channel, msg)
		return

	msg = '{} for {} is {}'.format(stat, member.name, newStat)
	await bot.send_message(ctx.message.channel, msg)

# Catch errors for stat
@getstat.error
async def getstat_error(ctx, error):
    # do stuff
	msg = 'getstat Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def setsstat(ctx, stat : str = None, value : str = None):
	"""Sets a server stat (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if stat == None or value == None:
		msg = 'Usage: $setsstat Stat Value'
		await bot.send_message(ctx.message.channel, msg)
		return

	setServerStat(ctx.message.server, globals.serverList, stat, value)

	msg = '{} set to {}!'.format(stat, value)
	await bot.send_message(ctx.message.channel, msg)


@bot.command(pass_context=True)
async def getsstat(ctx, stat : str = None):
	"""Gets a server stat (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if stat == None:
		msg = 'Usage: `$getsstat [stat]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	value = getServerStat(ctx.message.server, globals.serverList, stat)

	msg = '{} is currently {}!'.format(stat, value)
	await bot.send_message(ctx.message.channel, msg)

	
	
@bot.command(pass_context=True)
async def setlinkrole(ctx, role : discord.Role = None):
	"""Sets the required role ID to add/remove links (admin only)."""
	
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None:
		setServerStat(ctx.message.server, globals.serverList, "RequiredLinkRole", "")
		msg = 'Add/remove links now *admin-only*.'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# If we made it this far - then we can add it
	setServerStat(ctx.message.server, globals.serverList, "RequiredLinkRole", role.id)

	msg = 'Role required for add/remove links set to *{}*.'.format(role.name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()
	return

@setlinkrole.error
async def linkrole_error(ctx, error):
    # do stuff
	msg = 'setlinkrole Error: {}'.format(ctx)
	await bot.say(msg)

	
	
@bot.command(pass_context=True)
async def addlink(ctx, name : str = None, link : str = None):
	"""Add a link to the link list."""
	
	# Check for role requirements
	requiredRole = getServerStat(ctx.message.server, globals.serverList, "RequiredLinkRole")
	if requiredRole == "":
		#admin only
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	else:
		#role requirement
		hasPerms = False
		for role in ctx.message.author.roles:
			if role.id == requiredRole:
				hasPerms = True
		if not hasPerms:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
			
	# Passed role requirements!
	if name == None or link == None:
		msg = 'Usage: `$addlink "[link name]" [url]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkList = getServerStat(ctx.message.server, globals.serverList, "Links")
	if linkList == None:
		linkList = []

	linkList.append({"Name" : name, "URL" : link})

	setServerStat(ctx.message.server, globals.serverList, "Links", linkList)

	msg = '{} added to link list!'.format(name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()
	
	
@bot.command(pass_context=True)
async def removelink(ctx, name : str = None):
	"""Remove a link from the link list."""
	
	# Check for role requirements
	requiredRole = getServerStat(ctx.message.server, globals.serverList, "RequiredLinkRole")
	if requiredRole == "":
		#admin only
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	else:
		#role requirement
		hasPerms = False
		for role in ctx.message.author.roles:
			if role.id == requiredRole:
				hasPerms = True
		if not hasPerms:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	
	if name == None:
		msg = 'Usage: `$removelink "[link name]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkList = getServerStat(ctx.message.server, globals.serverList, "Links")
	if linkList == None or linkList == []:
		msg = 'No links in list!  You can add some with the `$addlink "[link name]" [url]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	for alink in linkList:
		if alink['Name'].lower() == name.lower():
			linkList.remove(alink)
			setServerStat(ctx.message.server, globals.serverList, "Links", linkList)
			msg = '{} removed from link list!'.format(name)
			await bot.send_message(ctx.message.channel, msg)
			return

	msg = '{} not found in link list!'.format(name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()


@bot.command(pass_context=True)
async def link(ctx, name : str = None):
	"""Retrieve a link from the link list."""
	if name == None or link == None:
		msg = 'Usage: `$link "[link name]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkList = getServerStat(ctx.message.server, globals.serverList, "Links")
	if linkList == None or linkList == []:
		msg = 'No links in list!  You can add some with the `$addlink "[link name]" [url]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	for alink in linkList:
		if alink['Name'].lower() == name.lower():
			msg = '{}\n{}'.format(alink['Name'], alink['URL'])
			await bot.send_message(ctx.message.channel, msg)




@bot.command(pass_context=True)
async def links(ctx):
	"""List all links in the link list."""
	linkList = getServerStat(ctx.message.server, globals.serverList, "Links")
	if linkList == None or linkList == []:
		msg = 'No links in list!  You can add some with the `$addlink "[link name]" [url]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkText = "Current Links:\n\n"

	for alink in linkList:
		linkText = '{}*{}*, '.format(linkText, alink['Name'])

	# Speak the link list while cutting off the end ", "
	await bot.send_message(ctx.message.channel, linkText[:-2])
	
	
	
	
	
	
	
@bot.command(pass_context=True)
async def sethackrole(ctx, role : discord.Role = None):
	"""Sets the required role ID to add/remove hacks (admin only)."""
	
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None:
		setServerStat(ctx.message.server, globals.serverList, "RequiredHackRole", "")
		msg = 'Add/remove hacks now *admin-only*.'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# If we made it this far - then we can add it
	setServerStat(ctx.message.server, globals.serverList, "RequiredHackRole", role.id)

	msg = 'Role required for add/remove hacks set to *{}*.'.format(role.name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()
	return

@sethackrole.error
async def hackrole_error(ctx, error):
    # do stuff
	msg = 'sethackrole Error: {}'.format(ctx)
	await bot.say(msg)

	
	
@bot.command(pass_context=True)
async def addhack(ctx, name : str = None, hack : str = None):
	"""Add a hack to the hack list."""
	
	# Check for role requirements
	requiredRole = getServerStat(ctx.message.server, globals.serverList, "RequiredHackRole")
	if requiredRole == "":
		#admin only
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	else:
		#role requirement
		hasPerms = False
		for role in ctx.message.author.roles:
			if role.id == requiredRole:
				hasPerms = True
		if not hasPerms:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
			
	# Passed role requirements!
	if name == None or hack == None:
		msg = 'Usage: `$addlink "[hack name]" [hack]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	hackList = getServerStat(ctx.message.server, globals.serverList, "Hacks")
	if hackList == None:
		hackList = []

	hackList.append({"Name" : name, "Hack" : hack})

	setServerStat(ctx.message.server, globals.serverList, "Hacks", hackList)

	msg = '{} added to hack list!'.format(name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()
	
	
@bot.command(pass_context=True)
async def removehack(ctx, name : str = None):
	"""Remove a hack from the hack list."""
	
	# Check for role requirements
	requiredRole = getServerStat(ctx.message.server, globals.serverList, "RequiredHackRole")
	if requiredRole == "":
		#admin only
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	else:
		#role requirement
		hasPerms = False
		for role in ctx.message.author.roles:
			if role.id == requiredRole:
				hasPerms = True
		if not hasPerms:
			await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
	
	if name == None:
		msg = 'Usage: `$removehack "[hack name]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkList = getServerStat(ctx.message.server, globals.serverList, "Hacks")
	if linkList == None or linkList == []:
		msg = 'No hacks in list!  You can add some with the `$addhack "[hack name]" [hack]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	for alink in linkList:
		if alink['Name'].lower() == name.lower():
			linkList.remove(alink)
			setServerStat(ctx.message.server, globals.serverList, "Hacks", linkList)
			msg = '{} removed from hack list!'.format(name)
			await bot.send_message(ctx.message.channel, msg)
			return

	msg = '{} not found in hack list!'.format(name)
	await bot.send_message(ctx.message.channel, msg)
	await quickFlush()


@bot.command(pass_context=True)
async def hack(ctx, name : str = None):
	"""Retrieve a hack from the hack list."""
	if name == None:
		msg = 'Usage: `$hack "[hack name]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkList = getServerStat(ctx.message.server, globals.serverList, "Hacks")
	if linkList == None or linkList == []:
		msg = 'No hacks in list!  You can add some with the `$addhack "[hack name]" [hack]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	for alink in linkList:
		if alink['Name'].lower() == name.lower():
			msg = '{}\n{}'.format(alink['Name'], alink['Hack'])
			await bot.send_message(ctx.message.channel, msg)




@bot.command(pass_context=True)
async def hacks(ctx):
	"""List all links in the link list."""
	linkList = getServerStat(ctx.message.server, globals.serverList, "Hacks")
	if linkList == None or linkList == []:
		msg = 'No hacks in list!  You can add some with the `$addhack "[hack name]" [hack]` command!'
		await bot.send_message(ctx.message.channel, msg)
		return

	linkText = "Current Hacks:\n\n"

	for alink in linkList:
		linkText = '{}*{}*, '.format(linkText, alink['Name'])

	# Speak the hack list while cutting off the end ", "
	await bot.send_message(ctx.message.channel, linkText[:-2])
	
	
	
	
	
	
@bot.command(pass_context=True)
async def parts(ctx, member : discord.Member = None):
	"""Retrieve a member's parts list."""
	if member == None:
		member = ctx.message.author

	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	# Initialize User
	globals.serverList = checkUser(member, ctx.message.server, globals.serverList)
	parts = getUserStat(member, ctx.message.server, globals.serverList, "Parts")
	
	if parts == None or parts == "":
		msg = '{} has not added their parts yet!  They can add them with the `$setparts "[parts text]"` command!'.format(member.name)
		await bot.send_message(ctx.message.channel, msg)
		return

	msg = '{}\'s Parts:\n\n{}'.format(member.name, parts)
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def setparts(ctx, parts : str = None):
	"""Set your own parts - can be a url, formatted text, or nothing to clear."""
	globals.serverList = checkUser(ctx.message.author, ctx.message.server, globals.serverList)
	if parts == None:
		parts = ""
		
	setUserStat(ctx.message.author, ctx.message.server, globals.serverList, "Parts", parts)
	msg = '{}\'s parts have been set to:\n\n{}'.format(ctx.message.author.name, parts)
	await bot.send_message(ctx.message.channel, msg)
	await flushSettings()
	
	
@bot.command(pass_context=True)
async def partstemp(ctx):
	"""Gives a copy & paste style template for setting a parts list."""
	msg = '\$setparts \"\`\`\`      CPU : \n   Cooler : \n     MOBO : \n      GPU : \n      RAM : \n      SSD : \n      HDD : \n      PSU : \n     Case : \nWiFi + BT : \n Lighting : \n Keyboard : \n    Mouse : \n  Monitor : \n      DAC : \n Speakers : \`\`\`\"'	
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def online(ctx):
	"""Lists the number of users online."""
	server = ctx.message.server
	members = 0
	membersOnline = 0
	for member in server.members:
		members += 1
		if str(member.status).lower() == "online":
			membersOnline += 1
	msg = 'There are *{}* out of *{}* users online.'.format(membersOnline, members)
	await bot.send_message(ctx.message.channel, msg)
	
	


@bot.command(pass_context=True)
async def quickhelp(ctx):
	"""List compact member-only help."""
	commandString = "```Quick Help:\n\n"

	commandString = commandString + "Music:\n"
	commandString = commandString + "   volume       Sets the volume of the currently playing song.\n"
	commandString = commandString + "   stop         Stops playing audio and leaves the voice channel.\n"
	commandString = commandString + "   skip         Vote to skip a song. The song requester can automatically skip.\n"
	commandString = commandString + "   join         Joins a voice channel.\n"
	commandString = commandString + "   resume       Resumes the currently played song.\n"
	commandString = commandString + "   pause        Pauses the currently played song.\n"
	commandString = commandString + "   play         Plays a song.\n"
	commandString = commandString + "   playing      Shows info about the currently played song.\n"
	commandString = commandString + "   summon       Summons the bot to join your voice channel.\n"

	commandString = commandString + "User Commands:\n"
	commandString = commandString + "   xp           Gift xp to other members.\n"
	commandString = commandString + "   stats        List the xp and xp reserve of a listed member (case-sensitive).\n"
	commandString = commandString + "   getstat      Gets the value for a specific stat for the listed member.\n"
	commandString = commandString + "   listroles    Lists all roles, id's, and xp requirements for the xp promotion/demotion system.\n"
	commandString = commandString + "   rank         Say the highest rank of a listed member.\n"
	commandString = commandString + "   link         Retrieve a link from the link list.\n"
	commandString = commandString + "   links        List all links in the link list.\n"
	commandString = commandString + "   addlink      Add a link to the link list.\n"
	commandString = commandString + "   removelink   Remove a link from the link list.\n"
	commandString = commandString + "   hack         Retrieve a hack from the hack list.\n"
	commandString = commandString + "   hacks        List all hacks in the hack list.\n"
	commandString = commandString + "   addhack      Add a hack to the hack list.\n"
	commandString = commandString + "   removehack   Remove a hack from the hack list.\n"
	commandString = commandString + "   parts        Retrieve a member's parts list.\n"
	commandString = commandString + "   setparts     Set your own parts - can be a url, formatted text, or nothing to clear.\n"
	commandString = commandString + "   partstemp    Gives a copy & paste style template for setting a parts list."
	
	commandString = commandString + "```"
	await bot.send_message(ctx.message.channel, commandString)
	
	commandString = "```"
	
	commandString = commandString + "   joined       Says when a member joined.\n"
	commandString = commandString + "   choose       Chooses between multiple choices.\n"
	commandString = commandString + "   add          Adds two numbers together.\n"
	commandString = commandString + "   randilbert   Randomly picks and displays a Dilbert comic.\n"
	commandString = commandString + "   dilbert      Displays the Dilbert comic for the passed date (MM-DD-YYYY).\n"
	commandString = commandString + "   randxkcd     Randomly picks and displays an XKCD comic.\n"
	commandString = commandString + "   xkcd         Displays the XKCD comic for the passed date (MM-DD-YYYY) or comic number if found.\n"
	commandString = commandString + "   randgarfield Randomly picks and displays a Garfield Minus Garfield comic.\n"
	commandString = commandString + "   garfield     Displays the Garfield Minus Garfield comic for the passed date (MM-DD-YYYY) if found.\n"
	commandString = commandString + "   randcalvin   Randomly picks and displays a Calvin & Hobbes comic.\n"
	commandString = commandString + "   calvin       Displays the Calvin & Hobbes comic for the passed date (MM-DD-YYYY) if found.\n"
	commandString = commandString + "   randcyanide  Randomly picks and displays a Cyanide & Happiness comic.\n"
	commandString = commandString + "   cyanide      Displays the Cyanide & Happiness comic for the passed date (MM-DD-YYYY) if found.\n"
	commandString = commandString + "   roll         Rolls a dice in NdN format.\n"
	commandString = commandString + "   online       Lists the number of users online.\n"
	commandString = commandString + "   thinkdeep    Spout out some intellectual brilliance.\n"
	commandString = commandString + "   brainfart    Spout out some uh.... intellectual brilliance...\n"
	commandString = commandString + "   nocontext    Spout out some intersexual brilliance.\n"
	commandString = commandString + "   question     Spout out some interstellar questioning... ?\n"
	commandString = commandString + "   answer       Spout out some interstellar answering... ?\n"
	commandString = commandString + "   fart         PrincessZoey :P\n"
	commandString = commandString + "   wallpaper    Get something pretty to look at.\n"
	commandString = commandString + "   earthporn    Earth is good.\n"
	commandString = commandString + "   gamble       Gamble your xp reserves for a chance at winning xp!\n"
	commandString = commandString + "   help         Shows the main help message.\n"
	commandString = commandString + "   quickhelp    Shows this help message.\n"
	commandString = commandString + "   adminhelp    Shows the admin help message."

	commandString = commandString + "```"

	await bot.send_message(ctx.message.channel, commandString)


@bot.command(pass_context=True)
async def adminhelp(ctx):
	"""List compact admin-only help."""
	commandString = "```Admin Help:\n\n"

	commandString = commandString + "Admin Commands:\n"
	commandString = commandString + "   addrole      Adds a new role to the xp promotion/demotion system (admin only).\n"
	commandString = commandString + "   removerole   Removes a role from the xp promotion/demotion system (admin only).\n"
	commandString = commandString + "   autorole     Sets the autorole value - can be No, ID, or Position (admin only).\n"
	commandString = commandString + "   setlinkrole  Sets the required role ID to add/remove links (admin only).\n"
	commandString = commandString + "   sethackrole  Sets the required role ID to add/remove hacks (admin only).\n"
	commandString = commandString + "   getsstat     Gets a server stat (admin only).\n"
	commandString = commandString + "   setsstat     Sets a server stat (admin only).\n"
	commandString = commandString + "   setxp        Sets an absolute value for the member's xp (admin only).\n"
	commandString = commandString + "   setxpreserve Set's an absolute value for the member's xp reserve (admin only).\n"
	commandString = commandString + "   setmotd      Adds a message of the day to the selected channel.\n"
	commandString = commandString + "   removemotd   Removes the message of the day from the selected channel.\n"
	commandString = commandString + "   playgame     Sets the playing status of the bot (admin only).\n"
	commandString = commandString + "   flush        Flush the bot settings to disk (admin only).\n"

	commandString = commandString + "```"

	await bot.send_message(ctx.message.channel, commandString)
	


@bot.command(pass_context=True)
async def flush(ctx):
	"""Flush the bot settings to disk (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		return
	# Flush settings
	await quickFlush()
	msg = 'Flushed settings to disk.'
	await bot.send_message(ctx.message.channel, msg)



@bot.command(pass_context=True)
async def randilbert(ctx):
	"""Randomly picks and displays a Dilbert comic."""
	# Get some preliminary values
	todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "04-16-1989"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

	# Get a random Julian date between the first comic and today
	startJDate = random.uniform(fJDate, tJDate)

	# Let's create our url
	gDate = jd_to_date(startJDate)

    # Prep dir names
	yDir = str(gDate[0])
	mDir = str(gDate[1])
	dName = str(int(gDate[2]))

	if (gDate[1] < 10):
		mDir = "0"+mDir

	if (gDate[2] < 10):
		dName = "0"+dName

	# Get URL
	getURL = "http://dilbert.com/strip/" + str(gDate[0]) + "-" + mDir + "-" + dName

	# Retrieve html and info
	imageHTML = getImageHTML(getURL)
	
	if imageHTML == None:
		# No image for that day - try again
		await randilbert(ctx)
		return
	
	imageURL  = getImageURL(imageHTML)
	imageDisplayName = getImageTitle(imageHTML)
	imageName = imageDisplayName + ".jpg"

	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)



@bot.command(pass_context=True)
async def dilbert(ctx, date : str = None):
	"""Displays the Dilbert comic for the passed date (MM-DD-YYYY)."""
	if date == None:
        # Auto to today's date
		date = dt.datetime.today().strftime("%m-%d-%Y")
	try:
		startDate = date.split("-")
	except ValueError:
		msg = 'Usage: `$dilbert "[date MM-DD-YYYY]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	# Get some preliminary values
	todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "04-16-1989"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))



	# Get a a Julian date for the passed day
	startJDate = date_to_jd(int(startDate[2]), int(startDate[0]), int(startDate[1]))

	outOfRange = False

	# Check date ranges
	if startJDate < fJDate:
		outOfRange = True
	if startJDate > tJDate:
		outOfRange = True

	if outOfRange:
		msg = "Date out of range. Must be between {} and {}".format(firstDate, todayDate)
		await bot.send_message(ctx.message.channel, msg)
		return

	# Let's create our url
	gDate = jd_to_date(startJDate)

    # Prep dir names
	yDir = str(gDate[0])
	mDir = str(gDate[1])
	dName = str(int(gDate[2]))

	if (gDate[1] < 10):
		mDir = "0"+mDir

	if (gDate[2] < 10):
		dName = "0"+dName

	# Get URL
	getURL = "http://dilbert.com/strip/" + str(gDate[0]) + "-" + mDir + "-" + dName

	# Retrieve html and info
	imageHTML = getImageHTML(getURL)
	
	if imageHTML == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return
	
	imageURL  = getImageURL(imageHTML)
	imageDisplayName = getImageTitle(imageHTML)
	imageName = imageDisplayName + ".jpg"

	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)

	
@bot.command(pass_context=True)
async def randxkcd(ctx):
	"""Displays a random XKCD comic."""
	
	# Must be a comic number
	archiveURL = "http://xkcd.com/archive/"
	archiveHTML = getImageHTML(archiveURL)
	newest = int(getNewestXKCD(archiveHTML))
	
	date = random.randint(1, newest)
		
	if int(date) > int(newest) or int(date) < 1:
		msg = "Comic out of range. Must be between 1 and {}".format(newest)
		await bot.send_message(ctx.message.channel, msg)
		return
		
	comicURL = "/" + str(date) + "/"
		
	
	if comicURL == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return

	comicURL = "http://xkcd.com" + comicURL

    # now we get the actual comic info
	imageHTML = getImageHTML(comicURL)
	
	if imageHTML == None:
		# No comic for that day - try again
		await randxkcd(ctx)
		return
	
	imageURL = getXKCDImageURL(imageHTML)
	imageDisplayName = getXKCDImageTitle(imageHTML)
	imageName = imageDisplayName + ".png"
	# imageDest = dirPath + "/" + imageName + ".png"

	msg = '{} (*{}*)'.format(imageDisplayName, date)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
	#with urllib.request.urlretrieve(imageURL) as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)


@bot.command(pass_context=True)
async def xkcd(ctx, date : str = None):
	"""Displays the XKCD comic for the passed date (MM-DD-YYYY) or comic number if found."""
	startDate = None
	if date == None:
		# Auto to today's date
		date = dt.datetime.today().strftime("%m-%d-%Y")
	try:
		startDate = date.split("-")
	except ValueError:
		# If it's an int - let's see if it fits
		if not type(date) == int:
			msg = 'Usage: `$xkcd "[date MM-DD-YYYY]"`'
			await bot.send_message(ctx.message.channel, msg)
			return
	
	if len(startDate) < 3:
		try:
			date = int(date)
		except:
			return
		# Must be a comic number
		archiveURL = "http://xkcd.com/archive/"
		archiveHTML = getImageHTML(archiveURL)
		newest = int(getNewestXKCD(archiveHTML))
		
		if int(date) > int(newest) or int(date) < 1:
			msg = "Comic out of range. Must be between 1 and {}".format(newest)
			await bot.send_message(ctx.message.channel, msg)
			return
		
		comicURL = "/" + str(date) + "/"
		
	else:
		
		# Get some preliminary values
		todayDate = dt.datetime.today().strftime("%m-%d-%Y")
		tDate = todayDate.split("-")
		tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

		# Can't be before this date.
		firstDate = "01-01-2006"
		fDate = firstDate.split("-")
		fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

		# Get a a Julian date for the passed day
		startJDate = date_to_jd(int(startDate[2]), int(startDate[0]), int(startDate[1]))

		outOfRange = False

		# Check date ranges
		if startJDate < fJDate:
			outOfRange = True
		if startJDate > tJDate:
			outOfRange = True
	
		if outOfRange:
			msg = "Date out of range. Must be between {} and {}".format(firstDate, todayDate)
			await bot.send_message(ctx.message.channel, msg)
			return

		# Let's create our url
		gDate = jd_to_date(startJDate)

		# Prep dir names
		yDir = str(gDate[0])
		mDir = str(gDate[1])
		dName = str(int(gDate[2]))

		if (gDate[1] < 10):
			mDir = "0"+mDir

		if (gDate[2] < 10):
			dName = "0"+dName

		# Get URL
		archiveURL = "http://xkcd.com/archive/"
		archiveHTML = getImageHTML(archiveURL)
		
		#print(archiveHTML)
		xkcdDate = "{}-{}-{}".format(int(yDir), int(mDir), int(dName))
		comicURL = getXKCDURL( archiveHTML, xkcdDate )
		
		
	
	if comicURL == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return
	comicNumber = comicURL.replace('/', '').strip()
	comicURL = "http://xkcd.com" + comicURL

    # now we get the actual comic info
	imageHTML = getImageHTML(comicURL)
	imageURL = getXKCDImageURL(imageHTML)
	imageDisplayName = getXKCDImageTitle(imageHTML)
	imageName = imageDisplayName + ".png"
	# imageDest = dirPath + "/" + imageName + ".png"

	msg = '{} (*{}*)'.format(imageDisplayName, comicNumber)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
	#with urllib.request.urlretrieve(imageURL) as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)

	
	
	
@bot.command(pass_context=True)
async def randgarfield(ctx):
	"""Randomly picks and displays a Garfield Minus Garfield comic."""
	# Get some preliminary values
	todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "02-13-2008"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

	# Get a random Julian date between the first comic and today
	gotComic = False
	tries = 0
	while gotComic == False:
	
		if tries >= 10:
			break
			
		startJDate = random.uniform(fJDate, tJDate)

		# Let's create our url
		gDate = jd_to_date(startJDate)

		# Prep dir names
		yDir = str(gDate[0])
		mDir = str(gDate[1])
		dName = str(int(gDate[2]))

		if (gDate[1] < 10):
			mDir = "0"+mDir

		if (gDate[2] < 10):
			dName = "0"+dName

		# Get URL
		getURL = "http://garfieldminusgarfield.net/day/" + yDir + "/" + mDir + "/" + dName

	
		#print(getURL)
	
		# Retrieve html and info
		imageHTML = getImageHTML(getURL)
	
		if not imageHTML == None:
			imageURL  = getGMGImageURL(imageHTML)
			#print(imageURL)
	
			if not imageURL == None:
				gotComic = True
			
		tries += 1

	if tries >= 10:
		msg = 'Failed to find working link.'
		await bot.send_message(ctx.message.channel, msg)
		return
	
	imageDisplayName = "Day " + yDir + "-" + mDir + "-" + dName
	imageName = imageDisplayName + ".png"
	
	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)



@bot.command(pass_context=True)
async def garfield(ctx, date : str = None):
	"""Displays the Garfield Minus Garfield comic for the passed date (MM-DD-YYYY) if found."""
	if date == None:
        # Auto to today's date
		date = dt.datetime.today().strftime("%m-%d-%Y")
	try:
		startDate = date.split("-")
	except ValueError:
		msg = 'Usage: `$dilbert "[date MM-DD-YYYY]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	# Get some preliminary values
	todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "02-13-2008"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))



	# Get a a Julian date for the passed day
	startJDate = date_to_jd(int(startDate[2]), int(startDate[0]), int(startDate[1]))

	outOfRange = False

	# Check date ranges
	if startJDate < fJDate:
		outOfRange = True
	if startJDate > tJDate:
		outOfRange = True

	if outOfRange:
		msg = "Date out of range. Must be between {} and {}".format(firstDate, todayDate)
		await bot.send_message(ctx.message.channel, msg)
		return

	# Let's create our url
	gDate = jd_to_date(startJDate)

    # Prep dir names
	yDir = str(gDate[0])
	mDir = str(gDate[1])
	dName = str(int(gDate[2]))

	if (gDate[1] < 10):
		mDir = "0"+mDir

	if (gDate[2] < 10):
		dName = "0"+dName

	# Get URL
	getURL = "http://garfieldminusgarfield.net/day/" + yDir + "/" + mDir + "/" + dName
	
	#print(getURL)

	# Retrieve html and info
	imageHTML = getImageHTML(getURL)
	
	if imageHTML == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return
	
	imageURL  = getGMGImageURL(imageHTML)
	
	#print(imageURL)
	
	if imageURL == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return

	imageDisplayName = "Day " + yDir + "-" + mDir + "-" + dName
	imageName = imageDisplayName + ".png"

	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)

	
	# http://marcel-oehler.marcellosendos.ch/comics/ch/1986/11/198611.html
	
	
@bot.command(pass_context=True)
async def randcalvin(ctx):
	"""Randomly picks and displays a Calvin & Hobbes comic."""
	# Get some preliminary values
	todayDate = "12-31-1995"
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "11-18-1985"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

	# Get a random Julian date between the first comic and today
	gotComic = False
	tries = 0
	while gotComic == False:
	
		if tries >= 10:
			break
					
		startJDate = random.uniform(fJDate, tJDate)

		# Let's create our url
		gDate = jd_to_date(startJDate)

		# Prep dir names
		yDir = str(gDate[0])
		mDir = str(gDate[1])
		dName = str(int(gDate[2]))

		if (gDate[1] < 10):
			mDir = "0"+mDir

		if (gDate[2] < 10):
			dName = "0"+dName

		# Get URL
		getURL = "http://marcel-oehler.marcellosendos.ch/comics/ch/" + yDir + "/" + mDir + "/" + yDir + mDir + dName + ".gif"

	
		#print(getURL)
	
		# Retrieve html and info
		imageHTML = getImageHTML(getURL)
	
		if not imageHTML == None:
			imageURL  = getURL
			gotComic = True
			
		tries += 1
		
	if tries >= 10:
		msg = 'Failed to find working link.'
		await bot.send_message(ctx.message.channel, msg)
		return
		
	imageDisplayName = "Calvin & Hobbes " + yDir + "-" + mDir + "-" + dName
	imageName = imageDisplayName + ".gif"
	
	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)



@bot.command(pass_context=True)
async def calvin(ctx, date : str = None):
	"""Displays the Calvin & Hobbes comic for the passed date (MM-DD-YYYY) if found."""
	if date == None:
        # Auto to today's date
		date = "12-31-1995"
	try:
		startDate = date.split("-")
	except ValueError:
		msg = 'Usage: `$dilbert "[date MM-DD-YYYY]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	# Get some preliminary values
	todayDate = "12-31-1995"
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "01-26-2005"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

	# Get a a Julian date for the passed day
	startJDate = date_to_jd(int(startDate[2]), int(startDate[0]), int(startDate[1]))

	outOfRange = False

	# Check date ranges
	if startJDate < fJDate:
		outOfRange = True
	if startJDate > tJDate:
		outOfRange = True

	if outOfRange:
		msg = "Date out of range. Must be between {} and {}".format(firstDate, todayDate)
		await bot.send_message(ctx.message.channel, msg)
		return

	# Let's create our url
	gDate = jd_to_date(startJDate)

    # Prep dir names
	yDir = str(gDate[0])
	mDir = str(gDate[1])
	dName = str(int(gDate[2]))

	if (gDate[1] < 10):
		mDir = "0"+mDir

	if (gDate[2] < 10):
		dName = "0"+dName

	# Get URL
	getURL = "http://marcel-oehler.marcellosendos.ch/comics/ch/" + yDir + "/" + mDir + "/" + yDir + mDir + dName + ".gif"
	
	#print(getURL)

	# Retrieve html and info
	imageHTML = getImageHTML(getURL)
	
	if imageHTML == None:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return
	
	imageURL  = getURL

	imageDisplayName = "Calvin & Hobbes " + yDir + "-" + mDir + "-" + dName
	imageName = imageDisplayName + ".gif"

	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)
	
	
@bot.command(pass_context=True)
async def randcyanide(ctx):
	"""Randomly picks and displays a Cyanide & Happiness comic."""
	# Get some preliminary values
	todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "01-26-2005"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))

	# Get a random Julian date between the first comic and today
	gotComic = False
	tries = 0
	while gotComic == False:
	
		if tries >= 10:
			break
					
		startJDate = random.uniform(fJDate, tJDate)

		# Let's create our url
		gDate = jd_to_date(startJDate)

		# Prep dir names
		yDir = str(gDate[0])
		mDir = str(gDate[1])
		dName = str(int(gDate[2]))

		if (gDate[1] < 10):
			mDir = "0"+mDir

		if (gDate[2] < 10):
			dName = "0"+dName

		# Get URL
		getURL = "http://explosm.net/comics/archive/" + yDir + "/" + mDir

	
		#print(getURL)
	
		# Retrieve html and info
		imageHTML = getImageHTML(getURL)
		if imageHTML:
			imagePage = getCHURL(imageHTML, yDir + "." + mDir + "." + dName)
			if imagePage:
				comicHTML = getImageHTML(imagePage)
				if comicHTML:
					imageURL  = getCHImageURL( comicHTML )
					# print("{} : {} : {}".format(gDate, imagePage, imageURL))
					if imageURL:
						gotComic = True
			
		tries += 1
		
	if tries >= 10:
		msg = 'Failed to find working link.'
		await bot.send_message(ctx.message.channel, msg)
		return
		
	imageDisplayName = "Cyanide & Happiness " + yDir + "-" + mDir + "-" + dName
	imageName = imageURL.rsplit('/', 1)[-1]
	if get_ext(imageName) == "":
		# Add gif because?
		imageName = imageName + ".gif"
	
	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)



@bot.command(pass_context=True)
async def cyanide(ctx, date : str = None):
	"""Displays the Cyanide & Happiness comic for the passed date (MM-DD-YYYY) if found."""
	if date == None:
        # Auto to today's date
		todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	try:
		startDate = date.split("-")
	except ValueError:
		msg = 'Usage: `$dilbert "[date MM-DD-YYYY]"`'
		await bot.send_message(ctx.message.channel, msg)
		return

	# Get some preliminary values
	todayDate = todayDate = dt.datetime.today().strftime("%m-%d-%Y")
	tDate = todayDate.split("-")
	tJDate = date_to_jd(int(tDate[2]), int(tDate[0]), int(tDate[1]))

	# Can't be before this date.
	firstDate = "01-26-2005"
	fDate = firstDate.split("-")
	fJDate = date_to_jd(int(fDate[2]), int(fDate[0]), int(fDate[1]))



	# Get a a Julian date for the passed day
	startJDate = date_to_jd(int(startDate[2]), int(startDate[0]), int(startDate[1]))

	outOfRange = False

	# Check date ranges
	if startJDate < fJDate:
		outOfRange = True
	if startJDate > tJDate:
		outOfRange = True

	if outOfRange:
		msg = "Date out of range. Must be between {} and {}".format(firstDate, todayDate)
		await bot.send_message(ctx.message.channel, msg)
		return

	# Let's create our url
	gDate = jd_to_date(startJDate)

    # Prep dir names
	yDir = str(gDate[0])
	mDir = str(gDate[1])
	dName = str(int(gDate[2]))

	if (gDate[1] < 10):
		mDir = "0"+mDir

	if (gDate[2] < 10):
		dName = "0"+dName

	# Get URL
	getURL = "http://explosm.net/comics/archive/" + yDir + "/" + mDir
	
	#print(getURL)

	gotComic = False
	imageHTML = getImageHTML(getURL)
	if imageHTML:
		imagePage = getCHURL(imageHTML, yDir + "." + mDir + "." + dName)
		if imagePage:
			comicHTML = getImageHTML(imagePage)
			if comicHTML:
				imageURL  = getCHImageURL( comicHTML )
				# print("{} : {} : {}".format(gDate, imagePage, imageURL))
				if imageURL:
					gotComic = True
	
	if not gotComic:
		msg = 'No comic found for *{}*'.format(date)
		await bot.send_message(ctx.message.channel, msg)
		return
	
	imageDisplayName = "Cyanide & Happiness " + yDir + "-" + mDir + "-" + dName
	imageName = imageURL.rsplit('/', 1)[-1]
	if get_ext(imageName) == "":
		# Add gif because?
		imageName = imageName + ".gif"

	msg = '{}'.format(imageDisplayName)
	await bot.send_message(ctx.message.channel, msg)

	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	imagePath = dirpath + "/" + imageName
	urllib.request.urlretrieve(imageURL, imagePath)
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, f)

	shutil.rmtree(dirpath, ignore_errors=True)
	

@bot.command(pass_context=True)
async def thinkdeep(ctx):
	"""Spout out some intellectual brilliance."""
	r = requests.get('https://www.reddit.com/r/showerthoughts/top.json?sort=top&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	randnum = random.randint(0,99)
	theJSON = r.json()["data"]["children"][randnum]["data"]
	msg = '{}'.format(theJSON["title"])
	await bot.send_message(ctx.message.channel, msg)
	

@bot.command(pass_context=True)
async def brainfart(ctx):
	"""Spout out some uh... intellectual brilliance..."""
	r = requests.get('https://www.reddit.com/r/Showerthoughts/controversial.json?sort=controversial&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	randnum = random.randint(0,99)
	theJSON = r.json()["data"]["children"][randnum]["data"]
	msg = '{}'.format(theJSON["title"])
	await bot.send_message(ctx.message.channel, msg)
	
	
# https://www.reddit.com/r/nocontext/top/?sort=top&t=week
	

@bot.command(pass_context=True)
async def nocontext(ctx):
	"""Spout out some intersexual brilliance."""
	r = requests.get('https://www.reddit.com/r/nocontext/top.json?sort=top&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	randnum = random.randint(0,99)
	theJSON = r.json()["data"]["children"][randnum]["data"]
	msg = '{}'.format(theJSON["title"])
	await bot.send_message(ctx.message.channel, msg)
	

@bot.command(pass_context=True)
async def question(ctx):
	"""Spout out some interstellar questioning... ?"""
	r = requests.get('https://www.reddit.com/r/NoStupidQuestions/top.json?sort=top&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	randnum = random.randint(0,99)
	theJSON = r.json()["data"]["children"][randnum]["data"]
	setServerStat(ctx.message.server, globals.serverList, "LastAnswer", theJSON["url"])
	msg = '{}'.format(theJSON["title"])
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def answer(ctx):
	"""Spout out some interstellar answering... ?"""
	answer = getServerStat(ctx.message.server, globals.serverList, "LastAnswer")
	if answer == "":
		msg = 'You need to ask a $question first!'
	else:
		msg = '{}'.format(answer)
	await bot.send_message(ctx.message.channel, msg)
	

@bot.command(pass_context=True)
async def fart(ctx):
	"""PrincessZoey :P"""
	fartList = ["Poot", "Prrrrt", "Thhbbthbbbthhh", "Plllleerrrrffff", "Toot", "Blaaaaahnk", "Squerk"]
	randnum = random.randint(0, len(fartList)-1)
	msg = '{}'.format(fartList[randnum])
	await bot.send_message(ctx.message.channel, msg)

	
@bot.command(pass_context=True)
async def earthporn(ctx):
	"""Earth is good."""
	r = requests.get('https://www.reddit.com/r/EarthPorn/top.json?sort=top&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	extList = ["jpg", "jpeg", "png", "gif", "tiff"]
	
	gotImage = False
	
	while not gotImage:
		randnum = random.randint(0,99)
		theJSON = r.json()["data"]["children"][randnum]["data"]
		if get_ext(theJSON["url"]) in extList:
			gotImage = True
	
	
	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	
	tempFileName = theJSON["url"].rsplit('/', 1)[-1]
	# Strip question mark
	tempFileName = tempFileName.split('?')[0]
	
	imagePath = dirpath + "/" + tempFileName
	
	# req = urllib.request.urlretrieve(theJSON["url"], imagePath)
	
	# req.add_header('User-agent', 'CorpNewt DeepThoughtBot')
	
	#with open(imagePath, 'rb') as f:
		#await bot.send_file(ctx.message.channel, f)

	rImage = requests.get(theJSON["url"], stream = True, headers = {'User-agent': 'CorpNewt DeepThoughtBot'})	
	with open(imagePath, 'wb') as f:
		for chunk in rImage.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	
	# Let's make sure it's less than 8MB
	# myimage = Image.open(imagePath)
	# print('Image Size Before: {}'.format(myimage.size))
	# myimage = to_python(imagePath, 8000000)
	# print('Image Size After : {}'.format(myimage.size))
	
	imageSize = os.stat(imagePath)
	
	if int(imageSize.st_size) > 8000000:
		# print("Image is too big ({}b) - resizing...".format(imageSize.st_size))
		myimage = Image.open(imagePath)
		xsize, ysize = myimage.size
		ratio = 8000000/int(imageSize.st_size)
		# print("Current Size: {} x {}".format(xsize, ysize))
		xsize *= ratio
		ysize *= ratio
		# print("Resized: {} x {}".format(int(xsize), int(ysize)))
		msg = '{} - Resized to [{} x {}]'.format(theJSON["title"], int(xsize), int(ysize))
		await bot.send_message(ctx.message.channel, msg)
		myimage = myimage.resize((int(xsize), int(ysize)), Image.ANTIALIAS)
		myimage.save(imagePath)
	else:
		msg = '{}'.format(theJSON["title"])
		await bot.send_message(ctx.message.channel, msg)
	
	# print(imageSize.st_size)
	
	
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, imagePath)
	
	
	shutil.rmtree(dirpath, ignore_errors=True)
	
	
	
	
	
	
@bot.command(pass_context=True)
async def wallpaper(ctx):
	"""Get something pretty to look at."""
	r = requests.get('https://www.reddit.com/r/wallpapers/top.json?sort=top&t=week&limit=100', headers = {'User-agent': 'CorpNewt DeepThoughtBot'})
	extList = ["jpg", "jpeg", "png", "gif", "tiff"]
	
	gotImage = False
	
	while not gotImage:
		randnum = random.randint(0,99)
		theJSON = r.json()["data"]["children"][randnum]["data"]
		if get_ext(theJSON["url"]) in extList:
			gotImage = True
	
	
	# Make temp dir, download image, upload to discord
	# then remove temp dir
	dirpath = tempfile.mkdtemp()
	
	tempFileName = theJSON["url"].rsplit('/', 1)[-1]
	# Strip question mark
	tempFileName = tempFileName.split('?')[0]
	
	imagePath = dirpath + "/" + tempFileName
	
	# req = urllib.request.urlretrieve(theJSON["url"], imagePath)
	
	# req.add_header('User-agent', 'CorpNewt DeepThoughtBot')
	
	#with open(imagePath, 'rb') as f:
		#await bot.send_file(ctx.message.channel, f)

	rImage = requests.get(theJSON["url"], stream = True, headers = {'User-agent': 'CorpNewt DeepThoughtBot'})	
	with open(imagePath, 'wb') as f:
		for chunk in rImage.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	
	# Let's make sure it's less than 8MB
	# myimage = Image.open(imagePath)
	# print('Image Size Before: {}'.format(myimage.size))
	# myimage = to_python(imagePath, 8000000)
	# print('Image Size After : {}'.format(myimage.size))
	
	imageSize = os.stat(imagePath)
	
	if int(imageSize.st_size) > 8000000:
		# print("Image is too big ({}b) - resizing...".format(imageSize.st_size))
		myimage = Image.open(imagePath)
		xsize, ysize = myimage.size
		ratio = 8000000/int(imageSize.st_size)
		# print("Current Size: {} x {}".format(xsize, ysize))
		xsize *= ratio
		ysize *= ratio
		# print("Resized: {} x {}".format(int(xsize), int(ysize)))
		msg = '{} - Resized to [{} x {}]'.format(theJSON["title"], int(xsize), int(ysize))
		await bot.send_message(ctx.message.channel, msg)
		myimage = myimage.resize((int(xsize), int(ysize)), Image.ANTIALIAS)
		myimage.save(imagePath)
	else:
		msg = '{}'.format(theJSON["title"])
		await bot.send_message(ctx.message.channel, msg)
	
	# print(imageSize.st_size)
	
	
	with open(imagePath, 'rb') as f:
		await bot.send_file(ctx.message.channel, imagePath)
	
	
	shutil.rmtree(dirpath, ignore_errors=True)
	
'''@wallpaper.error
async def wallpaper_error(ctx, error):
    # do stuff
	msg = 'wallpaper Error: {}'.format(ctx)
	await bot.say(msg)
'''	
	

@bot.command(pass_context=True)
async def gamble(ctx, bet : int = None):
	"""Gamble your xp reserves for a chance at winning xp!"""
	# bet must be a multiple of 10, member must have enough xpreserve to bet
	msg = 'Usage: `gamble [xp reserve bet] (must be multiple of 10)`'
	
	if bet == None:
		await bot.send_message(ctx.message.channel, msg)
		return
		
	if not type(bet) == int:
		await bot.send_message(ctx.message.channel, msg)
		return
		
	# Initialize User
	globals.serverList = checkUser(ctx.message.author, ctx.message.server, globals.serverList)

	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	adminUnlim = getServerStat(ctx.message.server, globals.serverList, "AdminUnlimited")
	reserveXP = getUserStat(ctx.message.author, ctx.message.server, globals.serverList, "XPReserve")
	minRole = getServerStat(ctx.message.server, globals.serverList, "MinimumXPRole")

	approve = True

	# Check Bet
		
	if not bet % 10 == 0:
		approve = False
		msg = 'Bets must be in multiples of *10!*'
		
	if bet > int(reserveXP):
		approve = False
		msg = 'You can\'t bet *{}*, you only have *{}* xp reserve!'.format(bet, reserveXP)
		
	if bet < 0:
		msg = 'You can\'t bet negative amounts!'
		approve = False
		
	if bet == 0:
		msg = 'You can\'t bet *nothing!*'
		approve = False
		
	if ctx.message.author.top_role.position < int(minRole):
		approve = False
		msg = 'You don\'t have the permissions to bet.'
		
	# Check admin last - so it overrides anything else
	'''if isAdmin and adminUnlim.lower() == "yes":
		# No limit - approve
		approve = True
		decrement = False'''
		
	if approve:
		# Bet was approved - let's take the XPReserve right away
		takeReserve = -1*bet
		globals.serverList = incrementStat(ctx.message.author, ctx.message.server, globals.serverList, "XPReserve", takeReserve)
		
		# Bet more, less chance of winning, but more winnings!
		if bet < 100:
			betChance = 5
			payout = int(bet/10)
		elif bet < 500:
			betChance = 15
			payout = int(bet/4)
		else:
			betChance = 25
			payout = int(bet/2)
		
		# 1/betChance that user will win - and payout is 1/10th of the bet
		randnum = random.randint(1, betChance)
		# print('{} : {}'.format(randnum, betChance))
		if randnum == 1:
			# YOU WON!!
			globals.serverList = incrementStat(ctx.message.author, ctx.message.server, globals.serverList, "XP", int(payout))
			msg = '{} bet {} and ***WON*** *{} xp!*'.format(ctx.message.author.name, bet, int(payout))
			#await bot.send_message(ctx.message.channel, msg)
			
			# Got XP - let's see if we need to promote
			xpPromote = getServerStat(ctx.message.server, globals.serverList, "XPPromote")
			xpDemote = getServerStat(ctx.message.server, globals.serverList, "XPDemote")
			promoteBy = getServerStat(ctx.message.server, globals.serverList, "PromoteBy")
			requiredXP = int(getServerStat(ctx.message.server, globals.serverList, "RequiredXP"))
			maxPosition = getServerStat(ctx.message.server, globals.serverList, "MaxPosition")
			padXP = getServerStat(ctx.message.server, globals.serverList, "PadXPRoles")
			difficulty = int(getServerStat(ctx.message.server, globals.serverList, "DifficultyMultiplier"))

			userXP = getUserStat(ctx.message.author, ctx.message.server, globals.serverList, "XP")
			userXP = int(userXP)+(int(requiredXP)*int(padXP))

			if xpPromote.lower() == "yes":
				# We use XP to promote - let's check our levels
				if promoteBy.lower() == "position":
					# We use the position to promote
					gotLevels = 0
					for x in range(0, int(maxPosition)+1):
						# Let's apply our difficulty multiplier

						# print("{} + {}".format((requiredXP*x), ((requiredXP*x)*difficulty)))

						required = (requiredXP*x) + (requiredXP*difficulty)
						# print("Level: {}\nXP: {}".format(x, required))
						if userXP >= required:
							gotLevels = x
					if gotLevels > int(maxPosition):
						# If we got too high - let's even out
						gotLevels = int(maxPosition)
					#print("Got: {} Have: {}".format(gotLevels, userRole))
					#if gotLevels > userRole:
						# We got promoted!
						#msg = '{} was given {} xp, and was promoted to {}!'.format(member.name, xpAmount, discord.utils.get(ctx.message.server.roles, position=gotLevels).name)
					gotLevels+=1
					for x in range(0, gotLevels):
						# fill in all the roles between
						for role in ctx.message.server.roles:
							if role.position < gotLevels:
								if not role in ctx.message.author.roles:
									# Only add if we need to
									await bot.add_roles(ctx.message.author, role)
									msg = '{} bet {} and ***WON*** *{} xp*, promoting them to {}!'.format(ctx.message.author.name, bet, int(payout), discord.utils.get(ctx.message.server.roles, position=gotLevels).name)
				elif promoteBy.lower() == "array":
					promoArray = getServerStat(ctx.message.server, globals.serverList, "PromotionArray")
					serverRoles = ctx.message.server.roles
					for role in promoArray:
						# Iterate through the roles, and add what we can
						if int(role['XP']) <= userXP:
							# We *can* have this role, let's see if we already do
							currentRole = None
							for aRole in serverRoles:
								# Get the role that corresponds to the id
								if aRole.id == role['ID']:
									# We found it
									currentRole = aRole

							# Now see if we have it, and add it if we don't
							if not currentRole in ctx.message.author.roles:
								await bot.add_roles(ctx.message.author, currentRole)
								msg = '{} bet {} and ***WON*** *{} xp*, promoting them to {}!'.format(ctx.message.author.name, bet, int(payout), currentRole.name)
						else:
							if xpDemote.lower() == "yes":
								# Let's see if we have this role, and remove it.  Demote time!
								currentRole = None
								for aRole in serverRoles:
									# Get the role that corresponds to the id
									if aRole.id == role['ID']:
										# We found it
										currentRole = aRole

							# Now see if we have it, and add it if we don't
								if currentRole in ctx.message.author.roles:
									await bot.remove_roles(ctx.message.author, currentRole)
									msg = '{} was demoted from {}!'.format(ctx.message.author.name, currentRole.name)
			
			
			
			
		else:
			msg = '{} bet {} and.... *didn\'t* win.  Better luck next time!'.format(ctx.message.author.name, bet)
		
	await bot.send_message(ctx.message.channel, msg)
		
	await flushSettings()
			
			
		
	# globals.serverList = incrementStat(ctx.message.author, ctx.message.server, globals.serverList, "XPReserve", incrementAmount)
	
@bot.command(pass_context=True)
async def nickname(ctx, name : str = None):
	"""Set the bot's nickname (admin-only)."""
	
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	
	# Let's get the bot's member in the current server
	botName = "{}#{}".format(bot.user.name, bot.user.discriminator)
	botMember = ctx.message.server.get_member_named(botName)
	await bot.change_nickname(botMember, name)
	
	
@bot.command(pass_context=True)
async def setrules(ctx, rules : str = None):
	"""Set the server's rules (admin-only)."""
	
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	
	if rules == None:
		rules = ""
		
	setServerStat(ctx.message.server, globals.serverList, "Rules", rules)
	msg = 'Rules now set to:\n{}'.format(rules)
	
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def rules(ctx):
	"""Display the server's rules."""
	rules = getServerStat(ctx.message.server, globals.serverList, "Rules")
	msg = "{} Rules:\n{}".format(ctx.message.server.name, rules)
	await bot.send_message(ctx.message.channel, msg)
	

@bot.command(pass_context=True)
async def lock(ctx):
	"""Toggles whether the bot only responds to admins (admin-only)."""
	
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
	
	isLocked = getServerStat(ctx.message.server, globals.serverList, "AdminLock")
	if isLocked.lower() == "yes":
		msg = 'Admin lock now *Off*.'
		setServerStat(ctx.message.server, globals.serverList, "AdminLock", "No")
	else:
		msg = 'Admin lock now *On*.'
		setServerStat(ctx.message.server, globals.serverList, "AdminLock", "Yes")
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def islocked(ctx):
	"""Says whether the bot only responds to admins."""
	
	isLocked = getServerStat(ctx.message.server, globals.serverList, "AdminLock")
	if isLocked.lower() == "yes":
		msg = 'Admin lock is *On*.'
	else:
		msg = 'Admin lock is *Off*.'
		
	await bot.send_message(ctx.message.channel, msg)
	
	
@bot.command(pass_context=True)
async def mute(ctx, member : discord.Member = None):
	"""Toggles whether a member can send messages in chat (admin-only)."""

	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	if not isAdmin:
		checkAdmin = getServerStat(ctx.message.server, globals.serverList, "AdminArray")
		for role in ctx.message.author.roles:
			for aRole in checkAdmin:
				# Get the role that corresponds to the id
				if aRole['ID'] == role.id:
					isAdmin = True
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return
		
	if member == None:
		msg = 'Usage: `mute [member]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	# Initialize User
	globals.serverList = checkUser(member, ctx.message.server, globals.serverList)
			
	isMute = getUserStat(member, ctx.message.server, globals.serverList, "Muted")
	if isMute.lower() == "yes":
		msg = '{} has been *Unmuted*.'.format(member)
		setUserStat(member, ctx.message.server, globals.serverList, "Muted", "No")
	
	else:
		msg = '{} has been *Muted*.'.format(member)
		setUserStat(member, ctx.message.server, globals.serverList, "Muted", "Yes")

	await bot.send_message(ctx.message.channel, msg)
	
@mute.error
async def mute_error(ctx, error):
    # do stuff
	msg = 'mute Error: {}'.format(ctx)
	await bot.say(msg)
	
@bot.command(pass_context=True)
async def ismuted(ctx, member : discord.Member = None):
	"""Says whether a member is muted in chat."""
		
	if member == None:
		msg = 'Usage: `ismuted [member]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(member) is str:
		try:
			member = discord.utils.get(message.server.members, name=member)
		except:
			print("That member does not exist")
			return

	# Initialize User
	globals.serverList = checkUser(member, ctx.message.server, globals.serverList)
			
	isMute = getUserStat(member, ctx.message.server, globals.serverList, "Muted")
	if isMute.lower() == "yes":
		msg = '{} is *Muted*.'.format(member)	
	else:
		msg = '{} is *Unmuted*.'.format(member)
		
	await bot.send_message(ctx.message.channel, msg)
	
@ismuted.error
async def ismuted_error(ctx, error):
    # do stuff
	msg = 'ismuted Error: {}'.format(ctx)
	await bot.say(msg)
	
	
@bot.command(pass_context=True)
async def addadmin(ctx, role : discord.Role = None):
	"""Adds a new role to the xp promotion/demotion system (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None:
		msg = 'Usage: `$addadmin [role]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# Now we see if we already have that role in our list
	promoArray = getServerStat(ctx.message.server, globals.serverList, "AdminArray")

	for aRole in promoArray:
		# Get the role that corresponds to the id
		if aRole['ID'] == role.id:
			# We found it - throw an error message and return
			msg = '{} is already in the list.'.format(role.name)
			await bot.send_message(ctx.message.channel, msg)
			return

	# If we made it this far - then we can add it
	promoArray.append({ 'ID' : role.id, 'Name' : role.name })
	setServerStat(ctx.message.server, globals.serverList, "AdminArray", promoArray)

	msg = '{} added to list.'.format(role.name)
	await bot.send_message(ctx.message.channel, msg)
	return

@addadmin.error
async def addadmin_error(ctx, error):
    # do stuff
	msg = 'addadmin Error: {}'.format(ctx)
	await bot.say(msg)



@bot.command(pass_context=True)
async def listadmin(ctx):
	"""Lists admin roles and id's."""
	promoArray = getServerStat(ctx.message.server, globals.serverList, "AdminArray")
	
	# rows_by_lfname = sorted(rows, key=itemgetter('lname','fname'))
	
	promoSorted = sorted(promoArray, key=itemgetter('Name'))
	
	roleText = "Current Admin Roles:\n"

	for arole in promoSorted:
		roleText = '{}**{}** (ID : `{}`)\n'.format(roleText, arole['Name'], arole['ID'])

	await bot.send_message(ctx.message.channel, roleText)




@bot.command(pass_context=True)
async def removeadmin(ctx, role : discord.Role = None):
	"""Removes a role from the admin list (admin only)."""
	isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
	# Only allow admins to change server stats
	if not isAdmin:
		await bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
		return

	if role == None:
		msg = 'Usage: `$removeadmin [role]`'
		await bot.send_message(ctx.message.channel, msg)
		return

	if type(role) is str:
		try:
			role = discord.utils.get(message.server.roles, name=role)
		except:
			print("That role does not exist")
			return

	# If we're here - then the role is a real one
	promoArray = getServerStat(ctx.message.server, globals.serverList, "AdminArray")

	for aRole in promoArray:
		# Get the role that corresponds to the id
		if aRole['ID'] == role.id:
			# We found it - let's remove it
			promoArray.remove(aRole)
			setServerStat(ctx.message.server, globals.serverList, "AdminArray", promoArray)
			msg = '{} removed successfully.'.format(aRole['Name'])
			await bot.send_message(ctx.message.channel, msg)
			return

	# If we made it this far - then we didn't find it
	msg = '{} not found in list.'.format(aRole['Name'])
	await bot.send_message(ctx.message.channel, msg)

@removeadmin.error
async def removeadmin_error(ctx, error):
    # do stuff
	msg = 'removeadmin Error: {}'.format(ctx)
	await bot.say(msg)
	

	
  ###             ###
 # END:   Commands #
###             ###

# --------------------------------------------- #

  ###       ###
 # Bot Start #
###       ###

with open('token.txt', 'r') as f:
  token = f.read()
  
bot.add_cog(Music(bot))
# bot.loop.create_task(flushSettings())

bot.run(token)

# --------------------------------------------- #

