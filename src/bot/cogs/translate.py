from deep_translator import GoogleTranslator
import discord
from discord.ext import commands
from discord import app_commands

class translate(commands.Cog):
    """Contains translation related methods"""
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Translate',
            callback=self.translate_message_to_english
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def translate_message_to_english(self, ctx: discord.Interaction, message: discord.Message):
        """Translates the selected message to english"""
        translated = GoogleTranslator(source='auto', target='en').translate(message.content)
        response = (
        '`Ah! I once knew every spell in all the tongues of Elves, Men and Orcs.`\n\n' # Code block
        
        '__**Translated message :**__\n\n' # Bold, Underline

        f'**{message.author.display_name}:** {translated}\n\n' # Bold
        
        f'__*Go back to message:*__ {message.jump_url}') # Italic, Underline

        await ctx.response.send_message(response, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    """Adds cog to bot"""
    await bot.add_cog(translate(bot))
