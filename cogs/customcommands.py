from discord.ext import commands
from cogs.utilities import credential_checks

import discord
import datetime
import random
import logging
import pymysql
import time    

log = logging.getLogger(__name__)

def connectToDatabase():
    return pymysql.connect(host='108.167.181.32',
                           user='lewis_robots',
                           password='ImABot12',
                           db='lewis_discord',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

class CustomCommands:
    """ Custom commands for your servers! """
    def __init__(self, client):
        self.client = client
        
    COMMANDS = {}
    async def readCommands(self):
        connection = connectToDatabase()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `discord_commands`"
                cursor.execute(sql)
        except pymysql.MySQLError(error):
            print(error)
            return
        finally:
            connection.close()

        for row in cursor:
            await self.setCommand(self, row["name"], row["description"], row["response"], row["server_id"])

    async def checkIfCommandTriggered(self, message):
        try:
            a = CustomCommands.COMMANDS[message.server.id]
        except KeyError:
            return False
        
        space_location = message.content.find(" ")
        if space_location == -1:
            command = message.content[1:]
        else:
            command = message.content[1:space_location]

        results = []
        for check in CustomCommands.COMMANDS[message.server.id]:
            if check["name"] == command:
                results.append(check["response"])

        if results:
            return random.choice(results)
        else:
            return False

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def addcommand(self, ctx, commandName):
        """ Add a new command to the server!

        You must have the Manage Emojis permission to do this. Servers have a limit of 50 commands each. If you think you deserve more, let me know."""
        await self.client.say("Okay, can do. What should it respond with? Once you've finished the response, put a \"##\" and then write the command description.\n__Example__\n:eyes:##Make the bot give you the eyes.")
        response = await self.client.wait_for_message(author=ctx.message.author)
        response = response.content.split("##")

        connection = connectToDatabase()

        with connection.cursor() as cursor:
            sql = "INSERT INTO `discord_commands` VALUES (0, %s, %s, %s, %s)"
            cursor.execute(sql, [commandName, response[0], response[1], ctx.message.server.id])

        await self.client.say("Whew! All done! I have added the command **"+commandName+"**, with a response: **"+response[0]+"** and description: **"+response[1]+"** to the server **"+ctx.message.server.name+"**")
        await self.setCommand(commandName, response[1], response[0], ctx.message.server.id)
    
        

    async def setCommand(self, name, description, response, server_id):
        command = {"name" : name, "response" : response, "description" : description}

        try:
            self.COMMANDS[server_id].append(command)
        except KeyError:
            self.COMMANDS[server_id] = [command]
                
        
def setup(client):
    client.add_cog(CustomCommands(client))

