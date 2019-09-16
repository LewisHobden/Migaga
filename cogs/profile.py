from discord.ext import commands
import discord

from peewee import *

from model.profile_field import ProfileFieldModel
from model.profile import ProfileModel


async def _profile_embed(member: discord.Member):
    try:
        profile = ProfileModel.get_by_id(member.id)
    except DoesNotExist:
        return None

    embed = discord.Embed(colour=discord.Colour(profile.colour), description=profile.bio, title=profile.tag)

    for field in profile.fields:
        embed.add_field(name=field.key, value=field.value)

    embed.set_author(name=str(member), icon_url=member.avatar_url)

    return embed


class Profile(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """ View your own profile! """
        embed = await _profile_embed(member if member else ctx.message.author)

        if embed is None:
            if member is None:
                message = "You do not have a profile yet. Set it up with `!myprofile`"
            else:
                message = "This user does not have a profile!"

            await ctx.send(message)
            return

        await ctx.send(embed=embed)

    @commands.command()
    async def myprofile(self, ctx, colour: discord.Colour, tag: str, *, bio: str):
        """ Set up or edit your main profile. Use the help command for required parts. """
        ProfileModel.insert(discord_user_id=ctx.author.id, colour=colour.value, tag=tag, bio=bio) \
            .on_conflict(
                preserve=[ProfileModel.discord_user_id],
                update={ProfileModel.colour: colour.value, ProfileModel.tag: tag, ProfileModel.bio: bio}) \
            .execute()

        await ctx.send("Profile set up! Thank you! Here it is!", embed=await _profile_embed(ctx.author))

    @commands.command()
    async def set(self, ctx, field, *, value):
        """ Set a custom field of your profile!

        You need to set up a profile before using this command. See !myprofile."""
        try:
            ProfileModel.get_by_id(ctx.author.id)
        except DoesNotExist:
            await ctx.send("You don't have a profile. Set one up using `!myprofile`")

        ProfileFieldModel.insert(discord_user_id=ctx.author.id, key=field, value=value)\
            .on_conflict_replace(True).execute()

        await ctx.send("Successfully set your `" + field + "` to `" + str(value) + "`!")


def setup(client: commands.Bot):
    client.add_cog(Profile(client))
