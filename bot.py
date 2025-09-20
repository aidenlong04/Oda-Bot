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

@bot.tree.command(name="find", description="Find messages with keywords in a channel (Admin only)")
async def find(interaction: discord.Interaction, keywords: str, channel: discord.TextChannel):
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        found_messages = []
        keywords_lower = keywords.lower()
        
        # Search through recent messages (limit to avoid rate limits)
        async for message in channel.history(limit=1000):
            if keywords_lower in message.content.lower():
                found_messages.append(f"**{message.author.display_name}**: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
                if len(found_messages) >= 10:  # Limit results
                    break
        
        if found_messages:
            result = f"🔍 Found {len(found_messages)} message(s) containing '{keywords}' in {channel.mention}:\n\n"
            result += "\n".join(found_messages)
            if len(result) > 2000:
                result = result[:1900] + "...\n\n*Results truncated*"
        else:
            result = f"🔍 No messages found containing '{keywords}' in {channel.mention}"
        
        await interaction.followup.send(result)
    except Exception as e:
        await interaction.followup.send(f"❌ Error searching messages: {str(e)}")

@bot.tree.command(name="sync_ign", description="Sync all user nicknames to their IGNs from a channel (Admin only)")
async def sync_ign(interaction: discord.Interaction, channel: discord.TextChannel):
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        synced_count = 0
        errors = []
        
        # Look for IGN patterns in recent messages (format: "IGN: username" or "username" at start of message)
        async for message in channel.history(limit=1000):
            if message.author.bot:
                continue
                
            content = message.content.strip()
            ign = None
            
            # Try to extract IGN from common patterns
            if content.lower().startswith("ign:"):
                ign = content[4:].strip()
            elif content.lower().startswith("ign "):
                ign = content[4:].strip()
            elif len(content.split()) == 1 and content.isalnum():
                ign = content
            
            if ign and len(ign) > 2 and len(ign) < 32:  # Reasonable IGN length
                try:
                    member = message.author
                    if member.display_name != ign:
                        await member.edit(nick=ign)
                        synced_count += 1
                except Exception as e:
                    errors.append(f"{message.author.display_name}: {str(e)}")
        
        result = f"✅ Synced {synced_count} nicknames from {channel.mention}"
        if errors:
            result += f"\n\n❌ Errors ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result += f"\n... and {len(errors) - 5} more"
        
        await interaction.followup.send(result)
    except Exception as e:
        await interaction.followup.send(f"❌ Error syncing nicknames: {str(e)}")

@bot.tree.command(name="sync_user", description="Sync specific user's nickname to their IGN from a channel (Admin only)")
async def sync_user(interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Look for this user's IGN in the specified channel
        async for message in channel.history(limit=1000):
            if message.author.id != user.id or message.author.bot:
                continue
                
            content = message.content.strip()
            ign = None
            
            # Try to extract IGN from common patterns
            if content.lower().startswith("ign:"):
                ign = content[4:].strip()
            elif content.lower().startswith("ign "):
                ign = content[4:].strip()
            elif len(content.split()) == 1 and content.isalnum():
                ign = content
            
            if ign and len(ign) > 2 and len(ign) < 32:  # Reasonable IGN length
                try:
                    if user.display_name != ign:
                        await user.edit(nick=ign)
                        await interaction.followup.send(f"✅ Updated {user.mention}'s nickname to `{ign}`")
                    else:
                        await interaction.followup.send(f"ℹ️ {user.mention}'s nickname is already `{ign}`")
                    return
                except Exception as e:
                    await interaction.followup.send(f"❌ Error updating {user.mention}'s nickname: {str(e)}")
                    return
        
        await interaction.followup.send(f"❌ No IGN found for {user.mention} in {channel.mention}")
    except Exception as e:
        await interaction.followup.send(f"❌ Error syncing nickname: {str(e)}")

# Main
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
