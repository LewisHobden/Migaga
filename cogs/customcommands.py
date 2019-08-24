import logging

import discord
from discord.ext import commands

from cogs.storage.database import Database
from cogs.utilities import credential_checks
from model.custom_command import CustomCommand

log = logging.getLogger(__name__)


async def check_if_command_triggered(message: discord.Message, command: str) -> str:
    return CustomCommand.get_random_response_by_name(message.channel.guild.id, command)


def truncate_command_response(response: str, length: int = 1900) -> str:
    return (response[:length] + '...') if len(response) > length else response


class CustomCommands(commands.Cog):
    """ Custom commands for your servers! """
    COMMANDS = {}

    def __init__(self, client):
        self.database = Database()
        self.client = client

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def addcommand(self, ctx, command_name: str):
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
        embed.add_field(name="Response", value=truncate_command_response(response, 1000))
        embed.add_field(name="Description", value="_Not provided_" if "" == description else description)

        await ctx.send(embed=embed)

    @commands.command(no_pm=True, pass_context=True)
    @credential_checks.hasPermissions(manage_emojis=True)
    async def deletecommand(self, ctx, command_name: str):
        """ Delete a command from the server """
        results = list(CustomCommand.get_responses_by_name(ctx.message.guild.id, command_name))

        if len(results) == 0:
            await ctx.send("No commands were found using that search term!")
            return
        elif len(results) == 1:
            results[0].delete_instance()

            await ctx.send("Nice! Deleted the command **{0}**!".format(results[0].name))
        else:
            counter = 0
            msg = "Multiple commands have been found.. Respond with the command number for it to be deleted. Separate " \
                  "them with commas for multiple to be deleted!\n "

            for command in results:
                command_text = "{0!s}. **{1}** - \"{2}\"\n"\
                    .format(counter + 1, command.name,
                            command.description if command.description else "responding with "+truncate_command_response
                            (command.response))

                if len(msg + command_text) > 2000:
                    await ctx.send(msg)
                    msg = command_text
                else:
                    msg += command_text

                counter += 1

            if len(msg) > 1:
                await ctx.send(msg)

            response = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel)

            ids_to_delete = response.content.split(",")

            for command_id in ids_to_delete:
                try:
                    index = int(command_id.strip()) - 1

                    results[index].delete_instance()

                except ValueError:
                    await ctx.send("Sorry I got confused with one of the indexes you provided. Please try again.")
                    return

            await ctx.send("Done! Deleted!")

    @commands.command(no_pm=True, pass_context=True)
    async def search(self, ctx, command_name):
        results = CustomCommand.get_responses_by_name(ctx.message.guild.id, command_name)
        result_str = "{} commands found".format(len(results))

        if 0 == len(results):
            await ctx.send(result_str)
            return

        result_str += "```\n"

        formatted_commands = []
        for result in results:
            if "!{}\n".format(result.name) in formatted_commands:
                pass
            else:
                formatted_commands.append("!{}\n".format(result.name))

        result_str += "".join(formatted_commands)
        result_str += "```"

        await ctx.send(result_str)


def setup(client):
    client.add_cog(CustomCommands(client))
