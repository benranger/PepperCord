from discord.ext import commands

from utils import errors


class ErrorHandling(commands.Cog):
    """Tools to assist with the handling of errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        # Reaction
        await ctx.message.add_reaction(emoji="❌")
        # Weirdness
        if isinstance(e, commands.CommandInvokeError):
            e = e.original
        # Owner reinvoke
        if isinstance(e, (commands.CheckFailure, commands.CommandOnCooldown)) and await ctx.bot.is_owner(ctx.author):
            await ctx.message.add_reaction(emoji="🔁")
            try:
                await ctx.reinvoke()
            except Exception as e:
                if len(str(e)) > 0:
                    await ctx.send(
                        f"During the attempt to reinvoke your command, `{e.__class__.__name__}` raised an exception. "
                        f"See: ```{e}``` "
                    )
                else:
                    await ctx.send(
                        f"During the attempt to reinvoke your command, `{e.__class__.__name__}` raised an exception. "
                    )
        # Bulk
        if isinstance(e, errors.NotInVoiceChannel):
            await ctx.send("You must be in a voice channel to execute this command.")
        elif isinstance(e, errors.NotAlone):
            await ctx.send("You must be alone or privileged to execute this command.")
        elif isinstance(e, errors.AlreadyPinned):
            await ctx.send("This message is already pinned to the starboard.")
        elif isinstance(e, errors.TooManyMembers):
            await ctx.send("This command doesn't work very well in large servers and has been disabled there. Sorry!")
        elif isinstance(e, errors.Blacklisted):
            await ctx.send("You have been blacklisted from utilizing this instance of the bot.")
        elif isinstance(e, commands.BotMissingPermissions):
            await ctx.send(f"I'm missing permissions I need to function. To re-invite me, see `{ctx.prefix}invite`.")
        elif isinstance(e, commands.NoPrivateMessage):
            await ctx.send(f"This commands can only be executed in a server.")
        elif isinstance(e, commands.NSFWChannelRequired):
            await ctx.send("No horny! A NSFW channel is required to execute this command.")
        elif isinstance(e, commands.CommandOnCooldown):
            await ctx.send(
                f"Slow the brakes, speed racer! We don't want any rate limiting... Try executing your command again in "
                f"`{round(e.retry_after, 1)}` seconds. "
            )
        elif isinstance(e, errors.NotSharded):
            await ctx.send("This bot is not sharded.")
        elif isinstance(e, commands.UserInputError):
            await ctx.send(f"Command is valid, but input is invalid. Try `{ctx.prefix}help {ctx.command}`.")
        elif isinstance(e, errors.LowPrivilege):
            await ctx.send(f"You are missing required permissions. {e}")
        elif isinstance(e, commands.MissingPermissions):
            await ctx.send("You are missing required permissions.")
        elif isinstance(e, commands.CheckFailure):
            await ctx.send("You cannot run this command.")
        elif isinstance(e, errors.SubcommandNotFound):
            await ctx.send(f"You need to specify a subcommand. Try `{ctx.prefix}help`.")
        elif isinstance(e, errors.NotConfigured):
            await ctx.send("This command must be configured first. Ask an admin.")
        elif isinstance(e, commands.CommandNotFound):
            await ctx.send(f"{e}. Try `{ctx.prefix}help`.")
        else:
            await ctx.send(
                f"Something went very wrong while processing your command. This can be caused by bad arguments or "
                f"something worse. Exception: ```{e}``` You can contact support with `{ctx.prefix}support`. "
            )


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
