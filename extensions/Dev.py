import typing
from io import StringIO

import discord
from discord.ext import commands, menus

from utils import checks


class ShardNotFound(Exception):
    pass


class ShardMenu(menus.Menu):
    def __init__(
        self,
        shard_info,
        *,
        timeout=180.0,
        delete_message_after=False,
        clear_reactions_after=False,
        check_embeds=False,
        message=None,
    ):
        self.shard_info = shard_info

        super().__init__(
            timeout=timeout,
            delete_message_after=delete_message_after,
            clear_reactions_after=clear_reactions_after,
            check_embeds=check_embeds,
            message=message,
        )

    async def send_initial_message(self, ctx, channel):
        embed = (
            discord.Embed(
                title=f"Info for shard {self.shard_info.id}/{self.shard_info.shard_count}",
            )
            .add_field(name="Online:", value=not self.shard_info.is_closed())
            .add_field(name="Latency:", value=f"{round(self.shard_info.latency * 1000)} ms")
        )
        return await ctx.send(embed=embed)

    @menus.button("🔄")
    async def reconnect(self, payload):
        return await self.shard_info.reconnect()


class Dev(commands.Cog):
    """Tools to be used by the bots developer to operate the bots."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(
        name="nick",
        aliases=["nickname"],
        brief="Change nickname.",
        description="Change the bots's nickname, for situations where you do not have privileges to.",
    )
    @commands.guild_only()
    async def nick(self, ctx, *, name: typing.Optional[str]):
        await ctx.guild.me.edit(nick=name)

    @commands.command(
        name="raw",
        aliases=["document"],
        brief="Get raw document for an entity.",
        description="Prints an entity's raw document. Be careful! It can contain sensitive information.",
    )
    async def raw(self, ctx, entity: typing.Optional[typing.Union[discord.Guild, discord.Member, discord.User]]):
        entity = entity or ctx.guild
        document = await ctx.bot.get_document(entity)
        buffer = StringIO()
        buffer.write(str(document))
        buffer.seek(0)
        file = discord.File(buffer, f"{entity.id}.json")
        await ctx.send(file=file)

    @commands.command(
        name="shardinfo",
        aliases=["si"],
        brief="Gets info on a shard.",
        description="Gets info on a shard and presents a menu which can be used to manage the shard.",
    )
    @commands.check(checks.bot_is_sharded)
    async def shard_info(self, ctx, *, shard_id: typing.Optional[typing.Union[discord.Guild, int]]):
        shard_id = shard_id or ctx.guild

        if isinstance(shard_id, discord.Guild):
            shard_id = shard_id.shard_id  # If the argument is a guild, replace shard_id with the shard_id of the guild

        shard_info = ctx.bot.get_shard(shard_id)

        if shard_info is None:
            raise ShardNotFound

        await ShardMenu(shard_info=shard_info).start(ctx)


def setup(bot):
    bot.add_cog(Dev(bot))
