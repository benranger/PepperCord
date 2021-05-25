import discord
from discord.ext import commands
from utils import checks, database, errors


class Messages(commands.Cog, name="Messages", description="Messages displayed when an event takes place."):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await checks.is_admin(ctx)

    async def member_message_processor(self, member: discord.Member, event: str):
        guild_doc = await database.Document.get_from_id(self.bot.database["guild"], member.guild.id)
        messages_dict = guild_doc["messages"][event]
        if messages_dict:
            for channel in messages_dict.keys():
                active_channel = self.bot.get_channel(int(channel))
                message = messages_dict[channel]
                embed = discord.Embed(colour=member.colour, description=message)
                await active_channel.send(member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.member_message_processor(member, "on_member_join")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.member_message_processor(member, "on_member_remove")

    @commands.group(
        invoke_without_command=True,
        case_insensitive=True,
        name="messages",
        aliases=["events"],
        brief="Configures events.",
        description="Configures what is displayed when a certain event occurs.",
    )
    async def events(self, ctx):
        raise errors.SubcommandNotFound()

    @events.command(
        name="disable",
        aliases=["off", "delete"],
        brief="Deletes messages.",
        description="Deletes all messages.",
    )
    async def sdisable(self, ctx):
        try:
            del ctx.guild_doc["reactions"]
        except:
            raise errors.NotConfigured()
        await ctx.guild_doc.replace_db()

    @events.command(
        name="add",
        aliases=["set"],
        brief="Sets message displayed when an action occurs.",
        description="Sets message displayed when an action occursm. Message types include on_member_join and on_member_remove.",
    )
    async def setmessage(self, ctx, message_type: str, channel: discord.TextChannel, *, message: str):
        ctx.guild_doc.setdefault("messages", {}).setdefault(message_type, {})[str(channel.id)] = message
        await ctx.guild_doc.replace_db()


def setup(bot):
    bot.add_cog(Messages(bot))
