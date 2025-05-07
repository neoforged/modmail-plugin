from os import truncate

import discord
from discord import app_commands
from discord.ext import commands

class NeoPlugin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.content)

    @app_commands.command(name="set-config", description="Set config value")
    @app_commands.describe(key="The config key", value="The config value")
    @app_commands.default_permissions(moderate_members=True)
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