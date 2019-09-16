from discord.ext import commands


def can_override(message):
    return message.author.id in ['133736489568829440']


def _check_permissions(ctx, **permissions):
    message = ctx.message

    if can_override(message):
        return True

    user_permissions = message.channel.permissions_for(message.author)
    return all(getattr(user_permissions, name, None) == value for name, value in permissions.items())


def is_administrator(ctx):
    return ctx.message.channel.permissions_for(ctx.message.author).administrator


def has_permissions(**permissions):
    def check(ctx):
        return _check_permissions(ctx, **permissions)

    return commands.check(check)
