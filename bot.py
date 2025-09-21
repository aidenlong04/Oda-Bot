from dotenv import load_dotenv
import discord
import os
import random
import subprocess
import sys

# Automatically install requirements if missing
def ensure_requirements():
    try:
        import discord
    except ImportError:
        print("discord.py not found, installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        import discord

ensure_requirements()

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class OdaBot(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.oda_cooldown = {3000: 0}
        self.oda_global_tracker = None
        self.oda_tracker = {}

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.tree.sync()

    async def on_message(self, message):
        if message.author.bot:
            return
        import time
        now = time.time()
        cooldown_key = 'global'
        if cooldown_key in self.oda_cooldown:
            last_trigger = self.oda_cooldown[cooldown_key]
            if now - last_trigger < 3600:
                return
        if "oda" in message.content.lower():
            if isinstance(self.oda_global_tracker, tuple) and len(self.oda_global_tracker) == 2:
                count, first_time = self.oda_global_tracker
                if now - first_time <= 60:
                    if count == 1:
                        await message.reply("https://tenor.com/view/breaking-bad-walter-white-youre-goddamn-right-gif-14600753")
                        self.oda_global_tracker = (2, first_time)
                        self.oda_cooldown[cooldown_key] = now
                    elif count == 0:
                        await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                        self.oda_global_tracker = (1, first_time)
                else:
                    await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                    self.oda_global_tracker = (1, now)
            else:
                await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                self.oda_global_tracker = (1, now)

bot = OdaBot(intents=intents)

# Ordis Jokes
ORDIS_JOKES = [
    "I admire you, Operator. You're strong, resourceful, and… ~~likely to die horribly at any moment.~~ Adaptive!",
    "Operator, I would tell you a joke about the Void, but it's... Devoid of humor.",
    "I cleaned the Liset today, Operator. Oh, except the blood stains. Those are… sentimental.",
    "Intruders Detected! Don't worry, Operator… I already gave them the tour. Of the airlock.",
    "Systems stable, Operator. Heart rate normal. Blood pressure ~~boiling, spurting, catastrophic failure imminent.~~ Optimal!",
    "Oda suggests taking a break, Operator. Hydrate, stretch, and then **annihilate all who oppose you.**"
]

@bot.tree.command(name="pun", description="Ordis will tell you a random joke!")
async def pun(interaction: discord.Interaction):
    joke = random.choice(ORDIS_JOKES)
    await interaction.response.send_message(joke)

# Main
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
