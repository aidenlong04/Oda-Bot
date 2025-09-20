

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
        self.oda_cooldown = {3000: 0}  # key: last_trigger_time
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
            # Global tracking: count and first_time
            if isinstance(self.oda_global_tracker, tuple) and len(self.oda_global_tracker) == 2:
                count, first_time = self.oda_global_tracker
                if now - first_time <= 60:
                    if count == 1:
                        # Second mention, start cooldown
                        await message.reply("https://tenor.com/view/breaking-bad-walter-white-youre-goddamn-right-gif-14600753")
                        self.oda_global_tracker = (2, first_time)
                        self.oda_cooldown[cooldown_key] = now
                    elif count == 0:
                        # First mention in window, send first GIF
                        await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                        self.oda_global_tracker = (1, first_time)
                else:
                    # Reset if outside 60s window
                    await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                    self.oda_global_tracker = (1, now)
            else:
                # First mention, only once per cycle
                await message.reply("https://tenor.com/view/waltwhite-breakingbad-say-my-name-gif-7259290")
                self.oda_global_tracker = (1, now)

bot = OdaBot(intents=intents)

# --- Ordis Jokes ---
ORDIS_JOKES = [
    "I admire you, Operator. You’re strong, resourceful, and… ~~likely to die horribly at any moment.~~ Adaptive!",
    "Operator, I would tell you a joke about the Void, but it's... Devoid of humor.",
    "I cleaned the Liset today, Operator. Oh, except the blood stains. Those are… sentimental.",
    "Intruders Detected! Don’t worry, Operator… I already gave them the tour. Of the airlock.",
    "Systems stable, Operator. Heart rate normal. Blood pressure ~~boiling, spurting, catastrophic failure imminent.~~ Optimal!",
    "Oda suggests taking a break, Operator. Hydrate, stretch, and then **annihilate all who oppose you.**"
]

# --- Commands ---
@bot.tree.command(name="pun", description="Ordis will tell you a random joke!")
async def pun(interaction: discord.Interaction):
    joke = random.choice(ORDIS_JOKES)
    await interaction.response.send_message(joke)

@bot.tree.command(
    name="find",
    description="Find a message with a keyword in a channel and return its link."
)
@discord.app_commands.describe(keywords="Keywords to search for", channel="Channel to search in")
async def find(interaction: discord.Interaction, keywords: str, channel: discord.TextChannel):
    member = interaction.user if isinstance(interaction.user, discord.Member) else None
    if not member or not (member.guild_permissions.manage_messages or member.guild_permissions.administrator):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Message Found:",
        color=discord.Color.from_str("#D4AF36")
    )
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    async for message in channel.history(limit=100):
        if keywords.lower() in message.content.lower():
            link = f"https://discord.com/channels/{message.guild.id}/{channel.id}/{message.id}"
            embed.description = f"[Jump to message]({link})"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    embed.description = f"No messages containing '{keywords}' found in {channel.mention}."
    await interaction.response.send_message(embed=embed, ephemeral=True)

@discord.app_commands.command(name="sync_ign", description="Sync server nicknames to IGN from a channel.")
@discord.app_commands.describe(channel="Channel to read IGNs from")
async def sync_ign(interaction: discord.Interaction, channel: discord.TextChannel):
    member = interaction.user if isinstance(interaction.user, discord.Member) else None
    if not member or not member.guild_permissions.administrator:
        embed = discord.Embed(
            title="Permission Denied",
            description="You must have administrator permission to use this command.",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    updated = 0
    guild = interaction.guild
    async for message in channel.history(limit=200):
        if message.author.bot:
            continue
        content = message.content
        ign = None
        print(f"Scanning message from {message.author}: {content}")
        # Ignore text after any variation of 'clan:' until next IGN/in-game name
        lines = content.splitlines()
        filtered_lines = []
        skip = False
        for line in lines:
            lower_line = line.lower()
            if any(tag in lower_line for tag in ["clan:", "clan -", "clan ", "clan:", "clan:"]):
                skip = True
                continue
            if ("ign:" in lower_line or "ign" in lower_line or "in-game name:" in lower_line or "in-game name" in lower_line):
                skip = False
            if not skip:
                filtered_lines.append(line)
        filtered_content = "\n".join(filtered_lines)
        # Now extract IGN from filtered_content
        if "ign:" in filtered_content.lower():
            idx = filtered_content.lower().index("ign:")
            ign = filtered_content[idx+4:].split("\n")[0].strip()
        elif "ign" in filtered_content.lower():
            idx = filtered_content.lower().index("ign")
            ign = filtered_content[idx+3:].split("\n")[0].strip()
        elif "IGN:" in filtered_content:
            idx = filtered_content.index("IGN:")
            ign = filtered_content[idx+4:].split("\n")[0].strip()
        elif "IGN" in filtered_content:
            idx = filtered_content.index("IGN")
            ign = filtered_content[idx+3:].split("\n")[0].strip()
        elif "in-game name:" in filtered_content.lower():
            idx = filtered_content.lower().index("in-game name:")
            ign = filtered_content[idx+14:].split("\n")[0].strip()
        elif "IN-GAME NAME:" in filtered_content:
            idx = filtered_content.index("IN-GAME NAME:")
            ign = filtered_content[idx+14:].split("\n")[0].strip()
        print(f"Extracted IGN: {ign}")
        embed = discord.Embed(
            title="IGN Scan",
            description=f"Scanned message from {message.author.mention}:\n{content}\n\nExtracted IGN: '{ign}'",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.followup.send(embed=embed, ephemeral=True)
        if ign:
            # Remove '#' and numerals after it
            import re
            ign_clean = re.sub(r"#\d+$", "", ign)
            try:
                member_obj = guild.get_member(message.author.id)
                if member_obj is None:
                    member_obj = await guild.fetch_member(message.author.id)
            except Exception:
                member_obj = None
            if member_obj:
                # Ignore admins, mods, and Clan Head role
                clan_head_role_id = 1361846841934610564
                has_clan_head = any(role.id == clan_head_role_id for role in member_obj.roles)
                if (member_obj.guild_permissions.administrator or
                    member_obj.guild_permissions.manage_guild or
                    member_obj.guild_permissions.manage_roles or
                    has_clan_head):
                    print(f"Skipping {message.author} (admin/mod/Clan Head)")
                    embed = discord.Embed(
                        title="IGN Sync Skipped",
                        description=f"Skipped {message.author.mention} (admin/mod/Clan Head)",
                        color=discord.Color.from_str("#D4AF36")
                    )
                    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    continue
                try:
                    await member_obj.edit(nick=ign_clean)
                    updated += 1
                    print(f"Updated nickname for {message.author} to '{ign_clean}'")
                    embed = discord.Embed(
                        title="Nickname Updated",
                        description=f"Updated nickname for {message.author.mention} to '{ign_clean}'",
                        color=discord.Color.from_str("#D4AF36")
                    )
                    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                except Exception as e:
                    print(f"Failed to update nickname for {message.author} to '{ign_clean}': {e}")
                    embed = discord.Embed(
                        title="Nickname Update Failed",
                        description=f"Failed to update nickname for {message.author.mention} to '{ign_clean}': {e}",
                        color=discord.Color.from_str("#D4AF36")
                    )
                    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                print(f"User {message.author} is not a member of this guild.")
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"User {message.author.mention} is not a member of this server.",
                    color=discord.Color.from_str("#D4AF36")
                )
                embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
                await interaction.followup.send(embed=embed, ephemeral=True)
    embed = discord.Embed(
        title="IGN Sync Complete",
        description=f"Updated {updated} user nicknames from channel {channel.mention}.",
        color=discord.Color.from_str("#D4AF36")
    )
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    await interaction.followup.send(embed=embed, ephemeral=True)

bot.tree.add_command(sync_ign)

# --- Sync User Command ---
@discord.app_commands.command(name="sync_user", description="Sync a single user's nickname to their IGN from a channel.")
@discord.app_commands.describe(user="User to update", channel="Channel to read IGN from")
async def sync_user(interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
    member = interaction.user if isinstance(interaction.user, discord.Member) else None
    if not member or not member.guild_permissions.administrator:
        embed = discord.Embed(
            title="Permission Denied",
            description="You must have administrator permission to use this command.",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    ign = None
    async for message in channel.history(limit=200):
        if message.author.id == user.id and not message.author.bot:
            content = message.content
            # IGN extraction logic (copied from /sync_ign)
            lines = content.splitlines()
            filtered_lines = []
            skip = False
            for line in lines:
                lower_line = line.lower()
                if any(tag in lower_line for tag in ["clan:", "clan -", "clan ", "clan:", "clan:"]):
                    skip = True
                    continue
                if ("ign:" in lower_line or "ign" in lower_line or "in-game name:" in lower_line or "in-game name" in lower_line):
                    skip = False
                if not skip:
                    filtered_lines.append(line)
            filtered_content = "\n".join(filtered_lines)
            if "ign:" in filtered_content.lower():
                idx = filtered_content.lower().index("ign:")
                ign = filtered_content[idx+4:].split("\n")[0].strip()
            elif "ign" in filtered_content.lower():
                idx = filtered_content.lower().index("ign")
                ign = filtered_content[idx+3:].split("\n")[0].strip()
            elif "IGN:" in filtered_content:
                idx = filtered_content.index("IGN:")
                ign = filtered_content[idx+4:].split("\n")[0].strip()
            elif "IGN" in filtered_content:
                idx = filtered_content.index("IGN")
                ign = filtered_content[idx+3:].split("\n")[0].strip()
            elif "in-game name:" in filtered_content.lower():
                idx = filtered_content.lower().index("in-game name:")
                ign = filtered_content[idx+14:].split("\n")[0].strip()
            elif "IN-GAME NAME:" in filtered_content:
                idx = filtered_content.index("IN-GAME NAME:")
                ign = filtered_content[idx+14:].split("\n")[0].strip()
            break
    if ign:
        import re
        ign_clean = re.sub(r"#\d+$", "", ign)
        clan_head_role_id = 1361846841934610564
        has_clan_head = any(role.id == clan_head_role_id for role in user.roles)
        if (user.guild_permissions.administrator or
            user.guild_permissions.manage_guild or
            user.guild_permissions.manage_roles or
            has_clan_head):
            embed = discord.Embed(
                title="IGN Sync Skipped",
                description=f"Skipped {user.mention} (admin/mod/Clan Head)",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            await user.edit(nick=ign_clean)
            embed = discord.Embed(
                title="Nickname Updated",
                description=f"Updated nickname for {user.mention} to '{ign_clean}'",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Nickname Update Failed",
                description=f"Failed to update nickname for {user.mention} to '{ign_clean}': {e}",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="IGN Not Found",
            description=f"No IGN found for {user.mention} in {channel.mention}.",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.followup.send(embed=embed, ephemeral=True)

# --- Sync User Command ---
@discord.app_commands.command(name="sync_user", description="Sync a single user's nickname to their IGN from a channel.")
@discord.app_commands.describe(user="User to update", channel="Channel to read IGN from")
async def sync_user(interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
    member = interaction.user if isinstance(interaction.user, discord.Member) else None
    if not member or not member.guild_permissions.administrator:
        embed = discord.Embed(
            title="Permission Denied",
            description="You must have administrator permission to use this command.",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    ign = None
    async for message in channel.history(limit=200):
        if message.author.id == user.id and not message.author.bot:
            content = message.content
            # IGN extraction logic (copied from /sync_ign)
            lines = content.splitlines()
            filtered_lines = []
            skip = False
            for line in lines:
                lower_line = line.lower()
                if any(tag in lower_line for tag in ["clan:", "clan -", "clan ", "clan:", "clan:"]):
                    skip = True
                    continue
                if ("ign:" in lower_line or "ign" in lower_line or "in-game name:" in lower_line or "in-game name" in lower_line):
                    skip = False
                if not skip:
                    filtered_lines.append(line)
            filtered_content = "\n".join(filtered_lines)
            if "ign:" in filtered_content.lower():
                idx = filtered_content.lower().index("ign:")
                ign = filtered_content[idx+4:].split("\n")[0].strip()
            elif "ign" in filtered_content.lower():
                idx = filtered_content.lower().index("ign")
                ign = filtered_content[idx+3:].split("\n")[0].strip()
            elif "IGN:" in filtered_content:
                idx = filtered_content.index("IGN:")
                ign = filtered_content[idx+4:].split("\n")[0].strip()
            elif "IGN" in filtered_content:
                idx = filtered_content.index("IGN")
                ign = filtered_content[idx+3:].split("\n")[0].strip()
            elif "in-game name:" in filtered_content.lower():
                idx = filtered_content.lower().index("in-game name:")
                ign = filtered_content[idx+14:].split("\n")[0].strip()
            elif "IN-GAME NAME:" in filtered_content:
                idx = filtered_content.index("IN-GAME NAME:")
                ign = filtered_content[idx+14:].split("\n")[0].strip()
            break
    if ign:
        import re
        ign_clean = re.sub(r"#\d+$", "", ign)
        clan_head_role_id = 1361846841934610564
        has_clan_head = any(role.id == clan_head_role_id for role in user.roles)
        if (user.guild_permissions.administrator or
            user.guild_permissions.manage_guild or
            user.guild_permissions.manage_roles or
            has_clan_head):
            embed = discord.Embed(
                title="IGN Sync Skipped",
                description=f"Skipped {user.mention} (admin/mod/Clan Head)",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            await user.edit(nick=ign_clean)
            embed = discord.Embed(
                title="Nickname Updated",
                description=f"Updated nickname for {user.mention} to '{ign_clean}'",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Nickname Update Failed",
                description=f"Failed to update nickname for {user.mention} to '{ign_clean}': {e}",
                color=discord.Color.from_str("#D4AF36")
            )
            embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
            await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="IGN Not Found",
            description=f"No IGN found for {user.mention} in {channel.mention}.",
            color=discord.Color.from_str("#D4AF36")
        )
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.followup.send(embed=embed, ephemeral=True)

bot.tree.add_command(sync_user)
# --- Main ---
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)