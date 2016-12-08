from discord.ext import commands
from cogs.utilities import credential_checks
from cogs.games.currency import Money

import discord
import datetime
import logging
import pymysql
import random
import time

log = logging.getLogger(__name__)

class Games:
    """ All Games that can be played """
    def __init__(self, client):
        self.client = client

    async def createBoard(self):
        # Create Board
        board = []
        for i in range(0,3):
            board.append([])
            for j in range(0,3):
                    board[i].append(" ")

        return board
    
    @commands.command(pass_context=True)
    async def slots(self, ctx):
        '''A slot machine, pay in 100 gold, you might get 200, or more out! '''
        #Check if games can be played here.
        
        # Slots
        player = ctx.message.author
        playerID = player.id

        fruits = [":cat:", ":dog:", ":bee:", ":baby_chick:", ":rabbit:"]

        board = await self.createBoard()

        # Initialise Board
        for rowNumber in range(0, 3):
            for columnNumber in range (0, 3):
                board[rowNumber][columnNumber] = fruits[random.randint(0, len(fruits) - 1)]
        
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

        if winnings == 0:
            winnings = -100
        
        if winnings > 0:
            playerWinnings = player.mention + " has won **" + str(winnings) + "**!"
        elif winnings < 0:
            playerWinnings = player.mention + " has lost **" + str(abs(winnings)) + "**!"
        
        # Print Board
        line1 = board[0][0] + board[0][1] + board[0][2]
        line2 = board[1][0] + board[1][1] + board[1][2]
        line3 = board[2][0] + board[2][1] + board[2][2]

        printedMessage = line1 + "\n" + line2 + "\n" + line3 + "\n" + playerWinnings
        await self.client.say(printedMessage)

        # Save new progress
        await Money.changeMoney(Money, playerID, int(winnings))

        # 10 second timeout.
        await self.client.wait_for_message(author=player, timeout=10, content="-slots")

    @commands.command(pass_context=True)
    async def rockpaperscissors(self, ctx):
        '''Challenge the bot to a game of rock, paper, scissors!'''
        choices = ["rock", "paper", "scissors"]
        await self.client.say("Rock, paper or scissors?")
        playerChoice = await self.client.wait_for_message(author=ctx.message.author)
        playerChoice = playerChoice.content.lower()
        botChoice = choices[random.randint(0,2)]

        matchups = {"paper": ["rock", "scissors"], "rock": ["scissors", "paper"], "scissors": ["paper", "rock"]}
        
        if botChoice == playerChoice:
            await self.client.say("I choose.. " + botChoice + "! We both chose the same thing! Oops!")
            return

        if matchups[playerChoice][0] == botChoice:
            await self.client.say("I choose.. " + botChoice + "! You won! Nice!")
        else:
            await self.client.say("I choose.. " + botChoice + "! I won! Better luck next time!")
            return 


    @commands.command(pass_context=True)
    async def blackjack(self, ctx):
        ''' Play Blackjack vs Migaga! '''
        suits  = [":spades:", ":hearts:", ":diamonds:", ":clubs:"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "King", "Queen", "Jack", "Ace"]
        total  = 0
        
        await client.say("Welcome to blackjack! I am your host, I am going to draw my cards and see if you can beat me! But first of all, how much "+Money.CURRENCY_NAME+" would you like to bet?")
        betAmount = await client.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
            
        try:
            betAmount = int(betAmount.content)
            if betAmount > 1000:
                await client.say("Whoa big spender, we can't let you bet more than 1000!")
            elif betAmount < 0:
                await client.say("GASP!**CHEATER!!**")
        except:
            await client.say("A number, please.")
                
        await client.say("Done! Now let's draw your first card. Say anything to draw another card, say `stop` at any time to turn in your total!")
        
        while True:
            suit = suits[random.randint(0, 3)]
            choice = random.randint(0, 13)
            value = values[choice]

            await self.client.say(ctx.message.author.mention + ", you drew the **" + str(value) + " of " + suit + "**!")

            if value in ["King", "Queen", "Jack"]:
                value = 10
            elif value == "Ace":
                okay    = False
                counter = 0
                while not okay and counter < 5:
                    await self.client.say("Would you like that to be worth 11 or 1?")
                    choice = await self.client.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
                    try:
                        if int(choice.content) == 11:
                            value = 11
                            okay = True
                        elif int(choice.content) == 1:
                            value = 1
                            okay = True
                        else:
                            await self.client.say("Either 1 or 11, please.")
                            counter += 1
                    except ValueError:
                        await self.client.say("Could I have that in the form of a number, please?")
                        counter += 1
                    
            total = total + value

            if total <= 21:
                await client.say("**"+ctx.message.author.name+"**, "+"You now have a total of " + str(total) + "!")
            elif total > 21:
                await self.client.say(await self.endBlackjack(2, ctx.message.author, betAmount*-1))
                return
                choice = await client.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        
            if choice.content.lower() == "stop":
                botTotal = random.randint(16, 21)
                await self.client.say("And that's the end of the game! Let's see how we compared.. \n \n I got **" + str(botTotal) + "** and you got **" + str(total) + "**!")
                await self.checkForBlackjackWins(ctx, total, botTotal)
                return

    
    def checkForBlackjackWins(self, player, total, botTotal):
        if total > migagaValue:
            await self.client.say(await self.endBlackjack(1, player, betAmount*2))
        elif total < migagaValue:
            await self.client.say(await self.endBlackjack(1, player, betAmount*-1))
        else:
            await self.client.say(await self.endBlackjack(1, player, 0))

    def endBlackjack(self, win_state, player, money):
        if win_state == 1:
            message = "That means you won **" + player.name + "**!! And your bet has been doubled!"
        elif win_state == 2:
            message = "Oh no! You got **" + str(total) + "** which looks to me like more than 21! Sorry but I'll be keeping your bet money today!"
        elif win_state == 3:
            message = "That means.. ooh you lost, **" + player.name + "**.. Better luck next time, and your bet has been taken!"
        elif win_state == 4:
            message = "That means.. it's a tie **" + player.name + "**?! uhh.. Keep your bet!"
            
        await Money.changeMoney(Money, player.id, winnings)
        return message
        

def setup(client):
    client.add_cog(Games(client))
