from os import truncate

import discord
from discord import app_commands, TextStyle, AppCommandType
from discord.ext import commands

from bot import ModmailBot
from core.models import InvalidConfigError
from core.thread import Thread


class NeoPlugin(commands.Cog):
    config_group = app_commands.Group(name = "config", description="Config commands")

    def __init__(self, bot: ModmailBot):
        self.bot = bot

        self.bot.tree.add_command(app_commands.ContextMenu(
            name="Report",
            callback=self.report
        ))

    async def config_option_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        keys = sorted(self.bot.config.public_keys)
        return [app_commands.Choice(name=option, value=option) for option in keys if
                option.lower().startswith(current.lower())][:25]

    @app_commands.guild_only
    @app_commands.describe(key="The config key", value="The config value")
    @app_commands.autocomplete(key=config_option_autocomplete)
    @app_commands.default_permissions(moderate_members=True)
    @config_group.command(name="set", description="Set a config value")
    async def set_config(self, interaction: discord.Interaction, key: str, value: str) -> None:
        keys = self.bot.config.public_keys

        if key in keys:
            try:
                await self.bot.config.set(key, value)
                await self.bot.config.update()
                embed = discord.Embed(
                    title="Success",
                    color=self.bot.main_color,
                    description=f"Set `{key}` to `{self.bot.config[key]}`.",
                )
            except InvalidConfigError as exc:
                embed = exc.embed
        else:
            embed = discord.Embed(
                title="Error", color=self.bot.error_color, description=f"{key} is an invalid key."
            )
            valid_keys = [f"`{k}`" for k in sorted(keys)]
            embed.add_field(name="Valid keys", value=truncate(", ".join(valid_keys), 1024))

        await interaction.response.send_message(embed=embed)

    async def report(self, interaction: discord.Interaction, message: discord.Message):
        class Form(discord.ui.Modal, title='Submit report'):
            def __init__(self, bot: ModmailBot):
                super().__init__()
                self.bot = bot

            reason = discord.ui.TextInput(
                label='Why are you reporting this message?',
                style=TextStyle.paragraph,
                placeholder='Type the reason for this report here...'
            )

            async def on_submit(self, int: discord.Interaction):
                thread = await self.bot.threads.find_or_create(interaction.user)
                embed = discord.Embed(
                    title="Received report from user",
                    description=self.reason.value
                )
                embed.add_field(name="Message", value=message.jump_url)
                self.bot.loop.create_task(self.submit_report(int, thread, embed))

            async def submit_report(self, int: discord.Interaction, thread: Thread, embed: discord.Embed):
                await thread.channel.send(embed=embed)
                await int.response.send_message('Your report has been submitted. Moderators will contact you via DMs received through this bot.', ephemeral=True)

        await interaction.response.send_modal(Form(self.bot))

async def setup(bot: ModmailBot):
    await bot.add_cog(NeoPlugin(bot))
    await bot.tree.sync()