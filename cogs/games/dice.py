import json
from datetime import datetime
from random import randint
from typing import List

from discord import Embed, Colour
from discord.ext import commands
from discord.ext.commands import BadArgument


class DiceConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        dice_components = argument.lower().split("d")

        if len(dice_components) != 2:
            raise KeyError("Unknown dice input: {}".format(argument))

        # Parse the input for its 2 components, its number of sides and how many to roll.
        total_requested = dice_components[0] if dice_components[0].isnumeric() and int(dice_components[0]) > 0 else 0
        dice_figure = dice_components[1] if dice_components[1].isnumeric() and int(dice_components[1]) > 0 else 0

        return [Die(total_sides=int(dice_figure)) for _ in range(0, int(total_requested))]


class KeepConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        keep = argument.lower()
        number_to_keep = argument.replace("k", "").replace("l", "")

        if not keep:
            return None

        # The keep string should either be empty, or "kl|k" followed by a number.
        if not keep.startswith("kl") and not keep.startswith("k"):
            raise BadArgument("Unknown \"keep\" argument: {}".format(keep))

        if not number_to_keep.isnumeric():
            raise BadArgument("Couldn't understand the number of dice to keep: {}".format(number_to_keep))

        return {"lowest": keep.startswith("kl"), "number_to_keep": int(number_to_keep)}


class Die:
    def __init__(self, total_sides: int):
        if total_sides < 2 or total_sides > 5000:
            raise BadArgument("Can't roll a dice with that many sides!")

        self._total_sides = total_sides
        self._roll_value = None

    def roll(self) -> int:
        if self._roll_value is None:
            self._roll_value = randint(1, int(self._total_sides))

        return self._roll_value


class DiceEmbed(Embed):
    def __init__(self, **kwargs):
        kwargs['colour'] = Colour.red()
        kwargs['timestamp'] = datetime.utcnow()

        super().__init__(**kwargs)

    def set_dice(self, dice: List[Die], number_to_keep: int = None, keep_lowest: bool = False):
        total = 0
        rolls = []

        for die in dice:
            rolls.append(die.roll())

            total += sum(rolls)

        self.add_field(name="Total", value=str(total), inline=False)
        self.description = "`{}`".format(json.dumps(rolls))

        if number_to_keep is not None:
            # Sort the list.
            rolls.sort(reverse=keep_lowest is False)
            filtered_rolls = rolls[0:number_to_keep]

            self.add_field(name="Dice To Keep", value="`{}`".format(json.dumps(filtered_rolls)))
            self.add_field(name="Kept Dice Total", value=str(sum(filtered_rolls)))


class DiceCog(commands.Cog, name="Dice"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="roll", aliases=["dice"])
    async def _roll(self, ctx, dice: DiceConverter, keep: KeepConverter = None):
        """ Ask the bot to roll a dice a number of times, try "3 D20" or "4 40". """
        if keep is None:
            keep = {"number_to_keep": None, "lowest": False}

        async with ctx.typing():
            embed = DiceEmbed(title="🎲 The dice have been cast!")
            embed.set_dice(dice, keep['number_to_keep'], keep['lowest'])
            embed.set_footer(text="Requested by {.display_name}".format(ctx.author))

            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(DiceCog(client))
