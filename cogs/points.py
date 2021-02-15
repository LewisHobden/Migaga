import io
import sys

import discord
from discord.ext import commands

from cogs.utilities.formatting import format_points
from model.model import *

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


class Points(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def inventory(self, ctx, *, member: discord.Member = None):
        """ Gets the number of points you have in yours or someone else's inventory. """
        if member is None:
            member = ctx.author

        config = await GuildConfig.get_for_guild(member.guild.id)

        if config.points_name is None:
            return

        async with ctx.channel.typing():
            position = await PointTransaction.get_position_in_guild_leaderboard(ctx.guild.id, ctx.author.id)

            user_total = await PointTransaction.get_total_for_member(member)

            if not user_total:
                return await ctx.send("I couldn't find any "+config.points_name+"!")

            font = ImageFont.truetype("/app/assets/fonts/Pixelar-Regular.ttf", 72)
            username_font = ImageFont.truetype("/app/assets/fonts/Pixelar-Regular.ttf", 72 - len(member.display_name))

            profile_image = member.avatar_url_as(format='png')
            profile_image_bytes = io.BytesIO(initial_bytes=await profile_image.read())
            profile_image = Image.open(profile_image_bytes).convert("RGBA").resize((150, 150))

            # get an image
            base = Image.open("/app/assets/inventory-backdrop.png").convert("RGBA").resize((640, 360))

            # get a drawing context
            d = ImageDraw.Draw(base)

            # crop image
            width, height = profile_image.size
            x = (width - height) // 2
            img_cropped = profile_image.crop((x, 0, x + height, height))

            # create grayscale image with white circle (255) on black background (0)
            mask = Image.new('L', img_cropped.size)
            mask_draw = ImageDraw.Draw(mask)
            width, height = img_cropped.size
            mask_draw.ellipse((0, 0, width, height), fill=255)

            # add mask as alpha channel
            img_cropped.putalpha(mask)

            d.text((200, 30), "{.display_name}#{.discriminator}".format(member, member), font=username_font, fill=(255, 255, 255, 255))
            d.text((275, 100), "{} {.points_name}".format(format_points(user_total), config), font=font, fill=(255, 255, 255, 255))
            d.text((40, 250), "#{} in {.name}".format(position[0], member.guild), font=font, fill=(255, 255, 255, 255))
            base.paste(img_cropped, (30, 30), img_cropped)

            # Load the points emoji from the config, add that to the image.
            emoji_id = config.points_emoji.split(":")[2][:-1]
            points_emoji = discord.utils.get(ctx.guild.emojis, id=int(emoji_id))
            emoji_image = points_emoji.url_as(format='png')
            emoji_image_bytes = io.BytesIO(initial_bytes=await emoji_image.read())
            emoji_image = Image.open(emoji_image_bytes).convert("RGBA")

            new_width = 50
            new_height = new_width * emoji_image.height / emoji_image.width

            emoji_image.thumbnail((new_width, new_height))

            base.paste(emoji_image, (200, 100), emoji_image)

            with io.BytesIO() as output:
                base.save(output, format="PNG")
                output.seek(0)

                await ctx.send(file=discord.File(output, filename="inventory.png"))

    @commands.command()
    async def leaderboard(self, ctx):
        """ Shows the leaderboard for the server.

         If you mention a person then you can get your placement on the leaderboard. """
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            return
        transactions = (PointTransaction
                        .select(PointTransaction.recipient_user_id,
                                fn.SUM(PointTransaction.amount).alias('total_points'))
                        .where(PointTransaction.guild_id == ctx.guild.id)
                        .group_by(PointTransaction.recipient_user_id)
                        .order_by(SQL('total_points DESC'))
                        .limit(10))

        body = "Showing the Top 10..\n"

        index = 1
        for transaction in transactions:
            member = ctx.guild.get_member(transaction.recipient_user_id)
            points = config.points_name[0].upper()
            points += config.points_name[1:]

            body += ("{}. **{}** - {}\n".format(index, member.display_name, format_points(transaction.total_points)))
            index += 1

        e = discord.Embed(colour=discord.Colour.gold(),
                          title="{} Leaderboard for {}".format(points, ctx.guild.name),
                          description=body)

        await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def points(self, ctx, action: str, member: discord.Member, amount: float):
        """ Give or takes away points from a user based on the action and how much you define.
        Your action is "give" or "take".. example, !points remove @Migaga 10

        You will need "Manage Roles" permissions to do this. """
        # Update the DB.
        config = await GuildConfig.get_for_guild(ctx.guild.id)

        if config.points_name is None:
            await ctx.send("You have not set up points in this server yet. Use `!config` to get started!")
            return

        if "take" == action:
            amount = amount * -1
            emoji = "\U0001f4c9"
            action = "Lost"
        elif "give" == action:
            emoji = "\U0001f4c8"
            action = "Got"
        else:
            return await ctx.send("You can either \"give\" or \"take\" points. See the help command for help.")

        await PointTransaction.grant_member(amount, member, ctx.author)
        user_total = await PointTransaction.get_total_for_member(member)

        embed = discord.Embed(title="{0} Points {1} {0}".format(emoji, action),
                              description="{.mention} just {} some {.points_name}{}".format(member, action.lower(),
                                                                                            config,
                                                                                            "" if config.points_emoji is None else " " + config.points_emoji),
                              color=discord.Color.green())

        embed.add_field(name="Total {}".format(action), value=str(abs(amount)))
        embed.add_field(name="New Total", value=format_points(user_total))

        await ctx.send(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Points(client))
