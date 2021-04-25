from loguru import logger
from discord.ext import commands
import discord

class ServerStats(commands.Cog):
    """
    Server status, and server information.
    """

    def __init__(self, client):
        self.client = client

    @commands.command(name="member-count")
    @logger.catch
    async def member_count(self, ctx):
        """
        Get server member count stats.
        """
        role_member = discord.utils.get(ctx.guild.roles, name="Member")
        role_unverified = discord.utils.get(ctx.guild.roles, name="unverified")
        
        embed=discord.Embed(title="Member Count", description="Count of members in this server", color=0x2f92d0)
        embed.set_author(name="Saranda House Stats")
        embed.add_field(name="Total Users", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Members", value=len(role_member.members), inline=True)
        embed.add_field(name="unverified", value=len(role_unverified.members), inline=True)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(ServerStats(client))