from dotenv import load_dotenv
import discord
import os
import random
import subprocess
import sys
import re

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

# Admin permission helper
def is_admin(interaction: discord.Interaction) -> bool:
    """Check if user has administrator permissions"""
    return interaction.user.guild_permissions.administrator

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

@bot.tree.command(name="find", description="Find messages containing keywords in a channel (Admin only)")
async def find(interaction: discord.Interaction, keywords: str, channel: discord.TextChannel):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ This command requires administrator permissions.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        found_messages = []
        keywords_lower = keywords.lower()
        
        async for message in channel.history(limit=1000):
            if keywords_lower in message.content.lower():
                found_messages.append({
                    'author': message.author.display_name,
                    'content': message.content[:100] + ('...' if len(message.content) > 100 else ''),
                    'jump_url': message.jump_url,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
                })
                
                if len(found_messages) >= 10:  # Limit to 10 results
                    break
        
        if not found_messages:
            await interaction.followup.send(f"No messages found containing '{keywords}' in {channel.mention}")
        else:
            embed = discord.Embed(
                title=f"🔍 Found {len(found_messages)} message(s) containing '{keywords}'",
                description=f"In channel: {channel.mention}",
                color=0x3498db
            )
            
            for i, msg in enumerate(found_messages, 1):
                embed.add_field(
                    name=f"{i}. {msg['author']} - {msg['created_at']}",
                    value=f"[{msg['content']}]({msg['jump_url']})",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
    
    except Exception as e:
        await interaction.followup.send(f"❌ Error searching messages: {str(e)}")

@bot.tree.command(name="sync_ign", description="Sync all user nicknames to their IGNs from a channel (Admin only)")
async def sync_ign(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ This command requires administrator permissions.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        ign_pattern = re.compile(r'ign[:\s]+([a-zA-Z0-9_-]+)', re.IGNORECASE)
        synced_users = []
        
        async for message in channel.history(limit=2000):
            match = ign_pattern.search(message.content)
            if match and message.author.id != bot.user.id:
                ign = match.group(1)
                try:
                    await message.author.edit(nick=ign)
                    synced_users.append(f"{message.author.display_name} → {ign}")
                except discord.Forbidden:
                    synced_users.append(f"❌ {message.author.display_name} (permission denied)")
                except Exception as e:
                    synced_users.append(f"❌ {message.author.display_name} (error: {str(e)})")
        
        if not synced_users:
            await interaction.followup.send(f"No IGN patterns found in {channel.mention}")
        else:
            embed = discord.Embed(
                title=f"🔄 IGN Sync Results",
                description=f"Synced nicknames from {channel.mention}",
                color=0x2ecc71
            )
            
            # Split into chunks of 10 to avoid embed limits
            for i in range(0, len(synced_users), 10):
                chunk = synced_users[i:i+10]
                embed.add_field(
                    name=f"Users {i+1}-{min(i+10, len(synced_users))}",
                    value='\n'.join(chunk),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
    
    except Exception as e:
        await interaction.followup.send(f"❌ Error syncing IGNs: {str(e)}")

@bot.tree.command(name="sync_user", description="Sync specific user's nickname to their IGN from a channel (Admin only)")
async def sync_user(interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ This command requires administrator permissions.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        ign_pattern = re.compile(r'ign[:\s]+([a-zA-Z0-9_-]+)', re.IGNORECASE)
        found_ign = None
        
        async for message in channel.history(limit=2000):
            if message.author.id == user.id:
                match = ign_pattern.search(message.content)
                if match:
                    found_ign = match.group(1)
                    break
        
        if not found_ign:
            await interaction.followup.send(f"❌ No IGN found for {user.display_name} in {channel.mention}")
            return
        
        try:
            await user.edit(nick=found_ign)
            embed = discord.Embed(
                title="✅ IGN Sync Successful",
                description=f"{user.mention} → {found_ign}",
                color=0x2ecc71
            )
            await interaction.followup.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ Permission denied: Cannot change nickname for {user.display_name}")
        except Exception as e:
            await interaction.followup.send(f"❌ Error changing nickname: {str(e)}")
    
    except Exception as e:
        await interaction.followup.send(f"❌ Error syncing user IGN: {str(e)}")

# Main
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
