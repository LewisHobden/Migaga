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
    return pymysql.connect(host='discord.crtejrmgafyl.us-east-1.rds.amazonaws.com',
                           user='lewis',
                           password='ImABot12',
                           db='discord',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

class CustomCommands:
    """ Custom commands for your servers! """
    COMMANDS = {}
    
    def __init__(self, client):
        self.client = client

    async def checkIfCommandTriggered(self, message):
        try:
            a = CustomCommands.COMMANDS[message.server.id]
        except KeyError:
            print("Key error. No commands in this server.")
            return False

        results = []
        for check in CustomCommands.COMMANDS[message.server.id]:
            if check["name"].lower() == command.lower():
                results.append(check["response"])
        
        if results:
            return random.choice(results)
        else:
            return False

    async def checkIfServerCanAddMoreCommands(self, server_id):
        whitelist = ['84142598456901632']
        connection = connectToDatabase()
        with connection.cursor() as csr:
            sql = "SELECT COUNT(*) AS `total` FROM `discord_commands` WHERE `server_id` = %s"
            csr.execute(sql, server_id)

            for result in csr:
                if result["total"] >= 50 and not server_id in whitelist:
                    return False

        return True

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def addcommand(self, ctx, command_name):
        """ Add a new command to the server!

        You must have the Manage Emojis permission to do this. Servers have a limit of 50 commands each. If you think you deserve more, let me know."""
        can_add_commands = await self.checkIfServerCanAddMoreCommands(ctx.message.server.id)
        if not can_add_commands:
            await self.client.say("Sorry! Your server has over 50 custom commands attached to it! Delete some with -deletecommand or wait to see if you can have more!")
            return
        
        await self.client.say("Okay, can do. What should it respond with? Once you've finished the response, put a \"##\" and then write the command description.\n__Example__\n:eyes:##Make the bot give you the eyes.")
        response = await self.client.wait_for_message(author=ctx.message.author)
        response = response.content.split("##")

        connection = connectToDatabase()

        with connection.cursor() as cursor:
            sql = "INSERT INTO `discord_commands` VALUES (0, %s, %s, %s, %s)"
            cursor.execute(sql, [command_name, response[0], response[1], ctx.message.server.id])

            await self.client.say("Whew! All done! I have added the command **"+command_name+"**, with a response: **"+response[0]+"** and description: **"+response[1]+"** to the server **"+ctx.message.server.name+"**")
            await self.setCommand(command_name, response[1], response[0], ctx.message.server.id, cursor.lastrowid)

        connection.commit()


    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def deletecommand(self, ctx, commandName):
        """ Delete a command from the server """
        results = []
        for command in self.COMMANDS[ctx.message.server.id]:
            if command["name"].find(command_name) != -1:
                results.append(command)

        if len(results) == 0:
            await self.client.say("No commands were found using that search term!")
            return
        elif len(results) == 1:
            await self.deleteCommandFromDatabase(results[0]['id'])
            self.COMMANDS[ctx.message.server.id].remove(results[0])
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
            else:
                ids_to_delete = [response]
                
            for command_id in ids_to_delete:
                try:
                    command_id = int(command_id.strip()) - 1
                    self.COMMANDS[ctx.message.server.id].remove(results[command_id])
                    await self.deleteCommandFromDatabase(results[command_id]['id'])
                except ValueError:
                    print("User inputting a non-numeric figure.")
                    return

            await self.client.say("Done! Deleted!")

    async def deleteCommandFromDatabase(self, command_id):
        sql = "DELETE FROM `discord_commands` WHERE `id`=%s"
        connection = connectToDatabase()
        with connection.cursor() as cursor:
            cursor.execute(sql, command_id)

        connection.commit()

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
            await self.setCommand(self, row["name"], row["description"], row["response"], row["server_id"], row["id"])
                    
                    
    async def setCommand(self, name, description, response, server_id, command_id):
        command = {"name" : name, "response" : response, "description" : description, "id" : command_id}

        try:
            self.COMMANDS[server_id].append(command)
        except KeyError:
            self.COMMANDS[server_id] = [command]
                
        
def setup(client):
    client.add_cog(CustomCommands(client))

