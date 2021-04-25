import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from loguru import logger
import os


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
token = os.getenv("DISCORD_BOT_TOKEN")
print("token", token)

DEFAULT_COGS = [
    'verify'
]

async def _load_cog(ctx, cog_name: str):
    try:
        client.load_extension(f"cogs.{cog_name}")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f"Cog `{cog_name}` already loaded")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog `{cog_name}` not found")
    except Exception as e:
        await ctx.send(f"Cog `{cog_name}` load failed with an error: ```\n{str(e)}\n```")
    else:
        await ctx.send(f"Cog `{cog_name}` loaded successfully")


async def _unload_cog(ctx, cog_name: str):
    try:
        client.unload_extension(f"cogs.{cog_name}")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog `{cog_name}` not found")
    except Exception as e:
        await ctx.send(f"Cog `{cog_name}` unload failed with an error: ```\n{str(e)}\n```")
    else:
        await ctx.send(f"Cog `{cog_name}` unloaded successfully")


async def _reload_cog(ctx, cog_name: str):
    try:
        await _unload_cog(ctx, cog_name)
    except:
        pass

    try:
        await _load_cog(ctx, cog_name)
    except:
        pass


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Listening to !help"))
    logger.info("Saranda is alive and breathing...")
    logger.info(f"Loading default cogs: {', '.join(DEFAULT_COGS)}")

    _cogs_loaded = []
    for cog_name in DEFAULT_COGS:
        try:
            client.load_extension(f"cogs.{cog_name}")
            _cogs_loaded.append(cog_name)
        except Exception as e:
            logger.opt(exception=True).error(f"Failed loading cog `{cog_name}`", e, exc_info=True)
    
    logger.info(f"Loaded {len(_cogs_loaded)} cog(s): {', '.join(_cogs_loaded)}")


@client.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")


@client.command(name='load-cog')
@commands.has_permissions(administrator=True)
async def load_cog(ctx, *cog_names: str):
    """
    Load cog with given name
    """

    logger.debug(f"Command load-cog: `{ctx.author.name}`")

    for name in cog_names:
        await _load_cog(ctx, name)
    
    await ctx.send(f"{ctx.author.mention} cog load complete")


@client.command(name='unload-cog')
@commands.has_permissions(administrator=True)
async def unload_cog(ctx, *cog_names: str):
    """
    Unload cog with given name
    """

    logger.debug(f"Command unload-cog: `{ctx.author.name}`")

    for name in cog_names:
        await _unload_cog(ctx, name)

    await ctx.send(f"{ctx.author.mention} cog unload complete")


@client.command(name='reload-cog')
@commands.has_permissions(administrator=True)
async def reload_cog(ctx, *cog_names: str):
    """
    Reload cog with given name
    """

    logger.debug(f"Command reload-cog: `{ctx.author.name}`")

    for name in cog_names:
        await _reload_cog(ctx, name)

    await ctx.send(f"{ctx.author.mention} cog reload complete")


logger.add("Saranda-bot.log", retention="7 days") 

help_menu = DefaultMenu(page_left="⬅️", page_right="➡️", remove="❌", active_time=60)
help_footer = "Use `!help command` for more info on a command. React below to move between page."

client.help_command = PrettyHelp(menu=help_menu, ending_note=help_footer, no_category="Default")
client.run(token)
