from os import truncate

import discord
from discord import app_commands
from discord.ext import commands

class NeoPlugin(commands.Cog):
    config_group = app_commands.Group(name = "config", description="Config commands")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def config_option_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        keys = self.bot.config.public_keys
        return [app_commands.Choice(name=option, value=option) for option in keys if
                option.lower().startswith(current.lower())].sort(key=lambda a : a.value)[:25]

    @app_commands.guild_only()
    @app_commands.describe(key="The config key", value="The config value")
    @app_commands.autocomplete(key=config_option_autocomplete)
    @app_commands.default_permissions(moderate_members=True)
    @config_group.command(name="set", description="Set a config value")
    async def set_config(self, interaction: discord.Interaction, key: str, value: str) -> None:
        keys = self.bot.config.public_keys

        if key in keys:
            await self.bot.config.set(key, value)
            await self.bot.config.update()
            embed = discord.Embed(
                title="Success",
                color=self.bot.main_color,
                description=f"Set `{key}` to `{self.bot.config[key]}`.",
            )
        else:
            embed = discord.Embed(
                title="Error", color=self.bot.error_color, description=f"{key} is an invalid key."
            )
            valid_keys = [f"`{k}`" for k in sorted(keys)]
            embed.add_field(name="Valid keys", value=truncate(", ".join(valid_keys), 1024))

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(NeoPlugin(bot))
    await bot.tree.sync()