import logging

import discord
from discord.ext import commands

from cogs.storage.database import Database
from cogs.utilities import credential_checks
from model.custom_command import CustomCommand

log = logging.getLogger(__name__)


async def check_if_command_triggered(message, command):
    return CustomCommand.get_random_response_by_name(command)


class CustomCommands(commands.Cog):
    """ Custom commands for your servers! """
    COMMANDS = {}

    def __init__(self, client):
        self.database = Database()
        self.client = client

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def addcommand(self, ctx, command_name):
        """ Add a new command to the server!

        You must have the Manage Emojis permission to do this."""

        await ctx.send(
            "Okay, can do. What should it respond with? Once you've finished the response, put a \"##\" and then "
            "write the command description.\n__Example__\n:eyes:##Make the bot give you the eyes.")

        reply = await self.client.wait_for("message", check=lambda m: m.author == ctx.message.author)

        response = reply.content.split("##")
        description = response[1] if len(response) == 2 else ""

        CustomCommand.create(name=command_name, description=description, response=response[0],
                             server_id=ctx.message.guild.id).save()

        embed = discord.Embed(title="Command Added", description="Here's your new command!",
                              colour=discord.Colour.green())
        embed.add_field(name="Command", value=command_name)
        embed.add_field(name="Response", value=response[0])
        embed.add_field(name="Description", value= "_Not provided_" if "" == description else description )

        await ctx.send(embed=embed)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def deletecommand(self, ctx, command_name):
        """ Delete a command from the server """
        results = await self.searchCommands(ctx.message.guild.id, command_name)

        if len(results) == 0:
            await self.client.send("No commands were found using that search term!")
            return
        elif len(results) == 1:
            await self.deleteCommandFromDatabase(results[0]['id'])
            self.COMMANDS[ctx.message.guild.id].remove(results[0])
            await self.client.send("Nice! Deleted the command **{0}**!".format(results[0]['name']))
        else:
            counter = 0
            msg = "Multiple commands have been found.. Respond with the command number for it to be deleted. Separate " \
                  "them with commas for multiple to be deleted!\n "
            for command in results:
                msg += "{0!s}. **{1}** - responding with `{2}`\n".format(counter + 1, command['name'],
                                                                         command['response'])
                counter += 1

            await self.client.send(msg)
            response = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel)

            response = response.content

            if response.find(",") != -1:
                ids_to_delete = response.split(",")
            else:
                ids_to_delete = [response]

            for command_id in ids_to_delete:
                try:
                    command_id = int(command_id.strip()) - 1
                    self.COMMANDS[ctx.message.guild.id].remove(results[command_id])
                    await self.deleteCommandFromDatabase(results[command_id]['id'])
                except ValueError:
                    print("User inputting a non-numeric figure.")
                    return

            await self.client.send("Done! Deleted!")

    async def deleteCommandFromDatabase(self, command_id):
        sql = "DELETE FROM `discord_commands` WHERE `id`=%s"
        self.database.query(sql, command_id)

    @commands.command(no_pm=True, pass_context=True)
    async def search(self, ctx, command_name):
        results = await self.searchCommands(ctx.message.guild.id, command_name)
        result_str = "{} commands found".format(len(results))
        result_str += "```\n"

        commands = []
        for result in results:
            if "!{}\n".format(result['name']) in commands:
                pass
            else:
                commands.append("!{}\n".format(result['name']))

        result_str += "".join(commands)
        result_str += "```"

        await self.client.send(result_str)


def setup(client):
    client.add_cog(CustomCommands(client))
