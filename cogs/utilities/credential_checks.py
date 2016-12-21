from discord.ext import commands
import discord.utils

def canOverride(message):
    return message.author.id in ['133736489568829440']

def checkPermissions(ctx, **permissions):
    message = ctx.message
    
    if canOverride(message):
        return True

    user_permissions = message.channel.permissions_for(message.author)
    return all(getattr(user_permissions, name, None) == value for name, value in permissions.items())
    
    
def isAdministrator(ctx):
    return ctx.message.channel.permissions_for(message.author).administrator

def hasPermissions(**permissions):
    def check(ctx):
        return checkPermissions(ctx, **permissions)

    return commands.check(check)
