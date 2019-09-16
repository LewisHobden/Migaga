from discord.ext import commands

import logging
import random

log = logging.getLogger(__name__)


async def _create_slots_board():
    # Create Board
    board = []
    for i in range(0, 3):
        board.append([])
        for j in range(0, 3):
            board[i].append(" ")

    return board


async def _get_result_message(player, total, bot_total):
    message = "And that's the end of the game! Let's see how we compared.. \n \n I got **{}** and you got **{}**! \n\n"

    if total > bot_total:
        message += "That means you won **{.name}**!!"
    elif total < bot_total:
        message += "That means.. ooh you lost, **{.name}**.. Better luck next time!"
    else:
        message += "That means.. it's a tie **{.name}**?! Good game!"

    return message.format(bot_total, total, player)


class Games(commands.Cog):
    """ All Games that can be played """

    def __init__(self, client):
        self.client = client
        self.money = client.get_cog("Currency")

    @commands.command()
    async def slots(self, ctx):
        """Play the slot machine!"""
        # Slots
        player = ctx.message.author
        server_emojis = ctx.guild.emojis

        if len(server_emojis) > 4:
            icons = random.sample(server_emojis, 5)
        else:
            icons = [":cat:", ":dog:", ":bee:", ":baby_chick:", ":rabbit:"]

        board = await _create_slots_board()

        # Initialise Board
        for rowNumber in range(0, 3):
            for columnNumber in range(0, 3):
                board[rowNumber][columnNumber] = icons[random.randint(0, len(icons) - 1)]

        # Detect Matches
        winnings = 0
        if board[0][0] == board[1][0] and board[0][0] == board[2][0]:
            winnings = winnings + 200
        if board[0][1] == board[1][1] and board[0][1] == board[2][1]:
            winnings = winnings + 200
        if board[0][2] == board[1][2] and board[0][2] == board[2][2]:
            winnings = winnings + 200

        if board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            winnings = winnings + 200
        if board[2][0] == board[1][1] and board[2][0] == board[0][2]:
            winnings = winnings + 200

        if board[0][0] == board[0][1] and board[0][0] == board[0][2]:
            winnings = winnings + 200
        if board[1][0] == board[1][1] and board[1][0] == board[1][2]:
            winnings = winnings + 200
        if board[2][0] == board[2][1] and board[2][0] == board[2][2]:
            winnings = winnings + 200

        message = "**{.name}** has got a match! **{}** points!".format(player, abs(winnings))

        if winnings == 0:
            message = "Aw, no **{.name}**! No matches this time!".format(player, abs(winnings))

        # Print Board
        line1 = str(board[0][0]) + str(board[0][1]) + str(board[0][2])
        line2 = str(board[1][0]) + str(board[1][1]) + str(board[1][2])
        line3 = str(board[2][0]) + str(board[2][1]) + str(board[2][2])

        await ctx.send(line1 + "\n" + line2 + "\n" + line3 + "\n" + message)

    @commands.command()
    async def rps(self, ctx):
        """ Challenge the bot to a game of rock, paper, scissors! """
        choices = ["rock", "paper", "scissors"]
        await ctx.send("Rock, paper or scissors?")
        player_choice = await self.client.wait_for(
            "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)

        player_choice = player_choice.content.lower()
        bot_choice = choices[random.randint(0, 2)]

        matchups = {"paper": ["rock", "scissors"], "rock": ["scissors", "paper"], "scissors": ["paper", "rock"]}

        if bot_choice == player_choice:
            await ctx.send("I choose.. " + bot_choice + "! We both chose the same thing! Oops!")
            return

        try:
            if matchups[player_choice][0] == bot_choice:
                await ctx.send("I choose.. " + bot_choice + "! You won! Nice!")
            else:
                await ctx.send("I choose.. " + bot_choice + "! I won! Better luck next time!")
                return
        except KeyError:
            await ctx.send("Not sure what a {} is...".format(player_choice))

    @commands.command()
    async def blackjack(self, ctx):
        """ Play Blackjack vs the bot! """
        suits = [":spades:", ":hearts:", ":diamonds:", ":clubs:"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "King", "Queen", "Jack", "Ace"]
        total = 0

        await ctx.send(
            "Welcome to blackjack! I am your host, I am going to draw my cards and see if you can beat me! Now let's "
            "draw your first card. Say anything to draw another card, say `stop` at any time to turn in your total!")

        while True:
            suit = random.choice(suits)
            value = random.choice(values)

            await ctx.send(
                "**" + ctx.message.author.name + "**, you drew the **" + str(value) + "** of " + suit + "!")

            total = total + await self._get_point_value(ctx, value)

            if total <= 21:
                await ctx.send(
                    "**" + ctx.author.name + "**, " + "You now have a total of " + str(total) + "!")
            elif total > 21:
                await ctx.send("Oh no! You got **{}** which looks to me like more than 21!".format(total))
                return

            will_continue = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel)

            if will_continue.content.lower() == "stop":
                bot_total = random.randint(16, 21)

                await ctx.send(await _get_result_message(ctx.author, total, bot_total))

                return

    async def _get_point_value(self, ctx, value):
        if value in ["King", "Queen", "Jack"]:
            return 10

        if value != "Ace":
            return value

        attempts = 0
        while attempts < 5:
            await ctx.send("Would you like that to be worth 11 or 1?")
            player_choice = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)

            try:
                if int(player_choice.content) == 11 or int(player_choice.content) == 1:
                    return int(player_choice.content)

                await ctx.send("Either 1 or 11, please.")
                attempts += 1

            except ValueError:
                await ctx.send("Could I have that in the form of a number, please?")
                attempts += 1


def setup(client):
    client.add_cog(Games(client))
