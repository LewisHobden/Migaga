from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.utilities.tools import Tools
from cogs.storage.database import Database

from time import gmtime, strftime
import discord
import json
import datetime
import logging

import os, sys
from PIL import Image
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)

class ServerLogs(commands.Cog):
	""" Logging server activity. """
	def __init__(self, client):
		self.client = client

	async def showMemberLeave(self,member):
		e = await ServerLogs.generateBoilerPlateEmbed(member,'9319990')
		e.title = "\N{CROSS MARK} Member Left the Server! \N{CROSS MARK}"
		e.description = member.display_name+" has left this server. Sad to see them go!.. Or am I?"

		e.add_field(name="Member Since:",value=member.joined_at.strftime("%d of %b %Y at\n%H:%M:%S"))

		return e

	async def showMemberJoin(self,member):
		e = await ServerLogs.generateBoilerPlateEmbed(member,'6278268')
		e.title = "\N{CHECK MARK} User Joined the Server! \N{CHECK MARK}"
		e.description = member.display_name+" has joined the server. Welcome!"

		date_created = member.created_at.strftime("%d of %b %Y at\n%H:%M:%S")
#		if member.created_at < datetime.datetime.now()-datetime.timedelta(days=1):
#			date_created = "\N{WARNING SIGN} "+date_created+" \N{WARNING SIGN} **NEW ACCOUNT**"

		e.add_field(name="Account Created:",value=date_created)
		return e

	async def showMemberUnban(self,user):
		e = await ServerLogs.generateBoilerPlateEmbed(user,'1219369')
		e.title = "\N{LOW BRIGHTNESS SYMBOL} Member Unbanned \N{LOW BRIGHTNESS SYMBOL}"
		e.description = user.display_name+" was unbanned from the server. I hope they learned their lesson!"

		return e

	async def showMemberBan(self,member):
		e = await ServerLogs.generateBoilerPlateEmbed(member,'10162706')
		e.title = "\N{NAME BADGE} Member Banned \N{NAME BADGE}"
		e.description = member.display_name+" was banned from this server. Sad to see them go!.. Or am I?"

		return e

	async def showMessageDelete(self,message):
		if [] != message.embeds or [] != message.attachments:
			return None
		e = await ServerLogs.generateBoilerPlateEmbed(message.author,'11346466',message.channel)
		e.title = "\N{CROSS MARK} Message Deleted \N{CROSS MARK}"
		e.description = message.content

		return e

	async def showMessageEdit(self,message_before,message_after):
		if [] != message_after.embeds:
			return None

		e = await ServerLogs.generateBoilerPlateEmbed(message_after.author,'16235052',message_after.channel)
		e.title = "\N{WARNING SIGN} Message Edit \N{WARNING SIGN}"
		e.description = "**Before:**\n"+message_before.content+"\n**After:**\n"+message_after.content

		return e

	async def determineUserChange(client,member_before,member_after):
	#	if member_before.avatar_url != member_after.avatar_url:
	#		return await ServerLogs.showAvatarChange(client,member_before,member_after)
		if member_before.name != member_after.name:
			return await ServerLogs.showUserNameChange(member_before,member_after)
		elif member_before.nick != member_after.nick:
			return await ServerLogs.showNickNameChange(member_before,member_after)
		elif member_before.roles != member_after.roles:
			return await ServerLogs.showRoleChanges(member_before,member_after)


	async def showRoleChanges(member_before,member_after):
		e = await ServerLogs.generateBoilerPlateEmbed(member_after,member_before.top_role.colour.value)
		e.title = "\N{EXCLAMATION MARK} Role Alteration \N{EXCLAMATION MARK}"
		e.description = member_after.display_name+"'s roles have changed."

		e.add_field(name="Before",value=await ServerLogs.getRolesAsText(member_before))
		e.add_field(name="After",value=await ServerLogs.getRolesAsText(member_after))

		return e

	async def showUserNameChange(user_before,user_after):
		e = await ServerLogs.generateBoilerPlateEmbed(user_after,"7748003")
		e.title       = "\N{LOWER RIGHT PENCIL} Username Change \N{LOWER RIGHT PENCIL}"
		e.add_field(name="Before",value=user_before.name)
		e.add_field(name="After",value=user_after.name)
		return e

	async def showNickNameChange(user_before,user_after):
		e = await ServerLogs.generateBoilerPlateEmbed(user_after,"10047446")
		e.title       = "\N{LOWER RIGHT PENCIL} Nickname Change \N{LOWER RIGHT PENCIL}"
		e.add_field(name="Before",value=await Tools.ifNoneReplaceWith(Tools, user_before.nick, "No Nickname"))
		e.add_field(name="After",value=await Tools.ifNoneReplaceWith(Tools, user_after.nick, "No Nickname"))
		return e

	#async def showAvatarChange(self,user_before,user_after):
	#	e = await ServerLogs.generateBoilerPlateEmbed(user_after,"4359924")
	#	e.title       = ":frame_photo: Avatar Change :frame_photo:"
	#	e.description = "Before / After";
	#
	#	channel = self.client.get_channel("242963032844533761")
#
#		image1 = await ServerLogs.downloadImageFromURL(user_before.avatar_url,"image_1")
#		image2 = await ServerLogs.downloadImageFromURL(user_after.avatar_url,"image_2")
#
#		image = await client.send_file(channel,open(await ServerLogs.stitchTogetherTwoPhotos(image1, image2),"rb"))
#		image_url = image.attachments[0]['proxy_url']
#
#		e.set_image(url=image_url)
#		return e

	async def downloadImageFromURL(url,file_name):
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
		file_name = file_name+".png"
		f = open(file_name, "wb")
		f.write(urlopen(req).read())
		f.close()

		return file_name

	async def stitchTogetherTwoPhotos(file_name_1,file_name_2):
		image1 = Image.open(file_name_1)
		image2 = Image.open(file_name_2)

		(width1, height1) = image1.size
		(width2, height2) = image2.size

		result_width = width1 + width2
		result_height = max(height1, height2)

		result = Image.new('RGB', (result_width, result_height))
		result.paste(im=image1, box=(0, 0))
		result.paste(im=image2, box=(width1, 0))
		result.save("new_image.png")

		return "new_image.png"

	async def generateBoilerPlateEmbed(author,colour=None,channel=None):
		e = discord.Embed()

		if None != colour:
			e.colour = discord.Colour(colour)

		if None != channel:
			e.add_field(name="Channel Name:",value=channel)
			e.add_field(name="Channel Link:",value="<#"+channel.id+">")

		avatar = author.default_avatar_url if not author.avatar else author.avatar_url
		avatar = avatar.replace('.gif', '.jpg')
		e.set_author(name=author.display_name, icon_url=avatar)
		e.timestamp = datetime.datetime.now()

		return e

	async def getRolesAsText(member):
		string = ""
		i = 1
		for role in member.roles:
			string += role.name.replace("@","[at]")

			if i < len(member.roles):
				string += ", "

			i += 1

		return string

def setup(client):
	client.add_cog(ServerLogs(client))
