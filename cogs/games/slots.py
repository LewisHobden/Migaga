from discord.ext import commands
from cogs.utilities import credential_checks

import discord
import datetime
import logging
import pymysql
import time


class Games(commands.Cog):
    @client.command(pass_context=True)
    async def slots(ctx):
        """ A slot machine, pay in 100 gold, you might get 200, or more out! """
        # Slots
        player = ctx.message.author
        playerID = player.id
        # Check to make sure they haven't done it recently
        messagetime = ctx.message.timestamp
        minutes = messagetime.minute
        seconds = messagetime.second

        try:
            indexThing = lastPlays.index(playerID)
            if minutes == lastPlays[indexThing + 1]:
                if seconds < lastPlays[indexThing + 2] + 10:
                    canPlay = False
                else:
                    canPlay = True
                    lastPlays[indexThing] = playerID
                    lastPlays[indexThing] = minutes
                    lastPlays[indexThing] = seconds
            else:
                canPlay = True
                lastPlays[indexThing] = playerID
                lastPlays[indexThing] = minutes
                lastPlays[indexThing] = seconds
        except:
            canPlay = True
            lastPlays.append(playerID)
            lastPlays.append(minutes)
            lastPlays.append(seconds)

        if canPlay:
            fruits = [emoji.emojize(":cat:"), emoji.emojize(":dog:"), emoji.emojize(":honeybee:"), emoji.emojize(":baby_chick:"), emoji.emojize(":rabbit:")]

            # Create Board
            board = []
            for i in range(0,3):
                board.append([])
                for j in range(0,3):
                        board[i].append(" ")

            # Initialise Board
            for rowNumber in range(0, 3):
                for columnNumber in range (0, 3):
                    board[rowNumber][columnNumber] = fruits[random.randint(0, len(fruits) - 1)]

            # Load/Add Progress
            gameCredits = await countRupees(playerID)

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

            totalCredits = int(gameCredits) + int(winnings)

            if winnings > 0:
                playerWinnings = player.mention + " has won **" + str(winnings) + "** and now has **" + str(totalCredits) + "** Gold!"
            elif winnings < 0:
                playerWinnings = player.mention + " has lost **" + str(abs(winnings)) + "** and now has **" + str(totalCredits) + "** Gold!"

            # Save new progress
            # await addRupees(playerID, totalCredits)

            # Print Board
            line1 = board[0][0] + board[0][1] + board[0][2]
            line2 = board[1][0] + board[1][1] + board[1][2]
            line3 = board[2][0] + board[2][1] + board[2][2]

            printedMessage = line1 + "\n" + line2 + "\n" + line3 + "\n" + playerWinnings
            await client.send(printedMessage)
