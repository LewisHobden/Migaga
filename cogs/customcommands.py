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
            await self.setCommand(row["name"], row["description"], row["response"], row["server_id"])

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


    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def deletecommand(self, ctx, commandName):
        """ Delete a command from the server """
        sql = "SELECT `id`, `response`, `name` FROM `discord_commands` WHERE `server_id`=%s AND `name` LIKE %s"

        connection = connectToDatabase()
        with connection.cursor() as cursor:
            cursor.execute(sql, [ctx.message.server.id, "%"+commandName+"%"])
            results = []
            for row in cursor:
                results.append(row)

            if len(results) == 0:
                await self.client.say("No commands were found using that search term!")
                return
            elif len(results) == 1:
                await self.deleteCommandFromDatabase(results[0]['id'])
                await self.client.say("Nice! Deleted the command **-{0}**!".format(results[0]['name']))
            else:
                counter = 0
                msg = "Multiple commands have been found.. Respond with the command number for it to be deleted. Separate them with commas for multiple to be deleted!\n"
                for command in results:
                    msg += "{0!s}. **{1}** - responding with `{2}`\n".format(counter+1, command['name'], command['response'])
                    counter += 1

                await self.client.say(msg)
                response = await self.client.wait_for_message(author=ctx.message.author)
                response = response.content
                if response.find(",") != -1:
                    ids_to_delete = response.split(",")
                    for command_id in ids_to_delete:
                        try:
                            command_id -= 1
                            await self.deleteCommandFromDatabase(results[command_id]['id'])
                        except:
                            print("User inputting a non-numeric figure inside a comma separated check")
                else:
                    try:
                        print(response)
                        command_id = int(response)-1
                        await self.deleteCommandFromDatabase(results[command_id]['id'])
                    except ValueError:
                        print("Number detected when trying to delete a command was not a number at all!")
                        return

                await self.client.say("Done! Deleted!")
                await self.readCommands()                        
                    
                    


    async def deleteCommandFromDatabase(self, command_id):
        sql = "DELETE FROM `discord_commands` WHERE `id`=%s"
        connection = connectToDatabase()
        with connection.cursor() as cursor:
            cursor.execute(sql, command_id)
                
        
def setup(client):
    client.add_cog(CustomCommands(client))

