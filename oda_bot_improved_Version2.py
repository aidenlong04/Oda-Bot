from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import subprocess
import sys
import re
import unicodedata
import logging
from datetime import datetime
from typing import Optional
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OdaBot')

# State file for persistence
STATE_FILE = Path("state.json")

def load_state():
    """Load bot state from file"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    return {"stats": {"commands_used": 0, "puns_told": 0}}

def save_state(state):
    """Save bot state to file"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

def _build_truncated_field(items, joiner="\n", max_chars=1024, more_fmt="...and {n} more"):
    """Join items with joiner but ensure result length <= max_chars."""
    if not items:
        return "None"
    out = ""
    for i, it in enumerate(items):
        part = (joiner if out else "") + it
        if len(out) + len(part) > max_chars:
            remaining = len(items) - i
            suffix = (joiner if out else "") + more_fmt.format(n=remaining)
            if len(out) + len(suffix) <= max_chars:
                out += suffix
            else:
                out = out[: max_chars - 3] + "..."
            return out
        out += part
    return out

def sanitize_nickname(raw: str, max_length: int = 32) -> str:
    """Sanitize a proposed nickname to be safe for Discord"""
    if not raw:
        return ""
    s = raw
    s = s.replace('`', '').replace('<', '').replace('>', '')
    s = re.sub(r"@(?:here|everyone)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<@!?(\d+)>", "", s)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.category(ch).startswith('C'))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = re.sub(r"[\uFE0E\uFE0F\u200D\u200B]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_length:
        s = s[:max_length].strip()
    return s

def _normalize_text(text: str) -> str:
    """Normalize text for spam detection: strip special characters between letters,
    collapse whitespace, and lowercase. This defeats common evasion tactics like
    j.o.i.n or j*o*i*n or j-o-i-n."""
    # Lowercase first
    s = text.lower()
    # Normalize unicode to NFKD and strip combining marks
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    # Replace common leet-speak substitutions
    leet_map = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '7': 't', '@': 'a', '$': 's', '!': 'i',
    }
    s = ''.join(leet_map.get(ch, ch) for ch in s)
    # Remove non-alphanumeric chars between word characters (defeats j.o.i.n style evasion)
    s = re.sub(r'(?<=\w)[^\w\s]+(?=\w)', '', s)
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# Compiled spam / server-advertisement regex patterns.
# These run against _normalize_text() output so special-char evasion is already stripped.
# Each pattern uses (?= ) lookaheads where helpful to allow overlapping matches.
SPAM_PATTERNS: list[re.Pattern] = [
    # "join my/our server/discord/community"
    re.compile(
        r'(?:come\s+)?join\s+(?:my|our)\s+(?:\w+\s+){0,3}'
        r'(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    # "anyone/who wants to join" (solicitation)
    re.compile(
        r'(?:anyone|who|somebody|anybody)\s+'
        r'(?:want|wanna|wants)\s+(?:to\s+)?join',
        re.IGNORECASE,
    ),
    # "check out my/our server/discord"
    re.compile(
        r'check\s*out\s+(?:my|our)\s+(?:\w+\s+){0,3}'
        r'(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    # "join us at/on/in" (direct invite)
    re.compile(
        r'join\s+us\s+(?:at|on|in)\b',
        re.IGNORECASE,
    ),
    # "growing/new/chill/active server|community" (advertisement descriptors)
    re.compile(
        r'(?:growing|brand\s*new|new|chill|active|friendly)\s+'
        r'(?:\w+\s+){0,2}(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    # "looking for members/people/players"
    re.compile(
        r'looking\s+for\s+(?:new\s+)?(?:members|people|players|staff)',
        re.IGNORECASE,
    ),
    # discord.gg or discord.com/invite links
    re.compile(
        r'discord(?:\.gg|\.com/invite)/\S+',
        re.IGNORECASE,
    ),
    # Lookahead combo: message contains BOTH "server" and "join" anywhere
    # This catches reordered phrases like "my server – come join!"
    re.compile(
        r'(?=.*\bjoin\b)(?=.*\bserver\b)',
        re.IGNORECASE,
    ),
]


def is_advertisement(text: str) -> bool:
    """Return True if *text* matches any known server-advertisement pattern.
    The text is first normalized to defeat special-character and leet-speak evasion.
    Discord invite links are checked against the raw text before normalization."""
    # Check invite links against raw (lowered) text before normalization strips punctuation
    raw_lower = text.lower()
    if re.search(r'discord(?:\.gg|\.com/invite)/\S+', raw_lower):
        return True
    cleaned = _normalize_text(text)
    return any(pat.search(cleaned) for pat in SPAM_PATTERNS)


def ensure_requirements():
    """Automatically install requirements if missing"""
    try:
        import discord
    except ImportError:
        logger.info("discord.py not found, installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

ensure_requirements()
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class OdaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # oda_cooldown and oda_global_tracker are no longer needed and have been removed
        self.state = load_state()
        self.start_time = datetime.utcnow()

    async def setup_hook(self):
        """Called when the bot is starting up"""
        await self.tree.sync()
        logger.info("Command tree synced")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="over the Liset"
            )
        )

    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            logger.error(f"Error in command: {error}")
            await ctx.send("❌ An error occurred while processing your command.")

    async def on_message(self, message):
        if message.author.bot:
            return

        # --- Server-advertisement / spam filter ---
        # Skip the check for users with Manage Messages permission (moderators/admins)
        if message.guild and not message.author.guild_permissions.manage_messages:
            if is_advertisement(message.content):
                try:
                    await message.delete()
                    logger.info(
                        f"Deleted advertisement from {message.author} "
                        f"in #{message.channel}: {message.content[:80]!r}"
                    )
                except discord.Forbidden:
                    logger.warning(
                        f"Missing permissions to delete ad message in #{message.channel}"
                    )
                except discord.NotFound:
                    pass  # Already deleted
                return  # Don't process commands for deleted spam

        await self.process_commands(message)

bot = OdaBot()

# Ordis Jokes (Expanded)
ORDIS_JOKES = [
    "I admire you, Operator. You're strong, resourceful, and… ~~likely to die horribly at any moment.~~ Adaptive!",
    "Operator, I would tell you a joke about the Void, but it's... Devoid of humor.",
    "I cleaned the Liset today, Operator. Oh, except the blood stains. Those are… sentimental.",
    "Intruders Detected! Don't worry, Operator… I already gave them the tour. Of the airlock.",
    "Systems stable, Operator. Heart rate normal. Blood pressure ~~boiling, spurting, catastrophic failure imminent.~~ Optimal!",
    "Oda suggests taking a break, Operator. Hydrate, stretch, and then **annihilate all who oppose you.**",
    "Did you know? The Corpus have a 100% mortality rate. ~~So do we all~~ Fascinating!",
    "I've been practicing my humor subroutines, Operator. ~~Kill me~~ How am I doing?",
    "Operator, would you like to hear about ship maintenance? ~~It's mind-numbingly dull~~ It's riveting!",
    "I detect elevated stress levels, Operator. Have you considered ~~violence~~ meditation?"
]

# Warframe Tips
WARFRAME_TIPS = [
    "💡 Use your Operator's Void Dash to quickly cover distances and proc status effects!",
    "💡 Mod for ability strength AND duration on most frames for maximum effectiveness.",
    "💡 Helios with Detect Vulnerability can reveal enemy weaknesses in combat.",
    "💡 Rolling gives you 75% damage reduction during the animation!",
    "💡 Aim gliding increases your critical chance on many weapons.",
    "💡 Most boss drops can be increased by using resource boosters.",
    "💡 The Helminth system lets you transfer abilities between Warframes!",
    "💡 Capturing targets on Fissure missions grants you more Void Traces.",
    "💡 Exodia Contagion can be used to nuke crowds from a distance with any Zaw."
]

@bot.tree.command(name="pun", description="Ordis will tell you a random joke!")
async def pun(interaction: discord.Interaction):
    joke = random.choice(ORDIS_JOKES)
    bot.state["stats"]["puns_told"] = bot.state["stats"].get("puns_told", 0) + 1
    bot.state["stats"]["commands_used"] = bot.state["stats"].get("commands_used", 0) + 1
    save_state(bot.state)
    await interaction.response.send_message(joke)

@bot.tree.command(name="tip", description="Get a random Warframe gameplay tip!")
async def tip(interaction: discord.Interaction):
    tip = random.choice(WARFRAME_TIPS)
    bot.state["stats"]["commands_used"] = bot.state["stats"].get("commands_used", 0) + 1
    save_state(bot.state)
    await interaction.response.send_message(tip)

@bot.tree.command(name="stats", description="View Oda's statistics")
async def stats(interaction: discord.Interaction):
    uptime = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(title="📊 Oda Statistics", color=0xD4AF36)
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    embed.add_field(name="⏱️ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="🖥️ Guilds", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="👥 Users", value=str(len(bot.users)), inline=True)
    embed.add_field(name="🎭 Puns Told", value=str(bot.state["stats"].get("puns_told", 0)), inline=True)
    embed.add_field(name="⚙️ Commands Used", value=str(bot.state["stats"].get("commands_used", 0)), inline=True)
    embed.set_footer(text=f"Oda Bot v2.0 • Latency: {round(bot.latency * 1000)}ms")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="find", description="Find messages containing specific text in a channel")
@app_commands.checks.has_permissions(administrator=True)
async def find(interaction: discord.Interaction, text: str, channel: discord.TextChannel, limit: Optional[int] = 100):
    await interaction.response.defer(ephemeral=True, thinking=True)
    
    found = []
    search_limit = min(limit, 1000)  # Cap at 1000 for performance
    
    async for message in channel.history(limit=search_limit):
        if text.lower() in message.content.lower():
            found.append(message)
    
    embed = discord.Embed(title="🔍 Search Results", color=0xD4AF36)
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    embed.description = f"Found **{len(found)}** message{'s' if len(found) != 1 else ''} containing '{text}' in {channel.mention}"
    
    if found:
        msg_links = []
        for m in found[:10]:
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{m.id}"
            preview = m.content[:50] + "..." if len(m.content) > 50 else m.content
            msg_links.append(f"[{m.author.name}]({message_url}): *{preview}*")
        
        if len(found) > 10:
            msg_links.append(f"...and {len(found) - 10} more")
        
        embed.add_field(name="Messages", value=_build_truncated_field(msg_links, joiner="\n"), inline=False)
    else:
        embed.add_field(name="Messages", value="No messages found.", inline=False)
    
    embed.set_footer(text=f"Searched last {search_limit} messages")
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="sync_ign", description="Sync IGNs from a channel and set as nicknames")
@app_commands.checks.has_permissions(administrator=True)
async def sync_ign(interaction: discord.Interaction, channel: discord.TextChannel, limit: Optional[int] = 100):
    await interaction.response.defer(ephemeral=True, thinking=True)
    
    processed_users = set()
    results = []
    failures = []
    ign_pattern = re.compile(r"ign:\s*(.+)", re.IGNORECASE)
    
    async for message in channel.history(limit=min(limit, 500)):
        match = ign_pattern.search(message.content)
        if match:
            ign_raw = match.group(1).strip()
            clan_idx = re.search(r"\bclan\b", ign_raw, re.IGNORECASE)
            if clan_idx:
                ign_raw = ign_raw[:clan_idx.start()].strip()
            ign = re.sub(r"#\s*\d+", "", ign_raw).strip()
            ign = sanitize_nickname(ign, max_length=32)
            
            member = interaction.guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await interaction.guild.fetch_member(message.author.id)
                except discord.NotFound:
                    continue
            
            if not ign:
                ign = sanitize_nickname(message.author.display_name, max_length=32)
                if not ign:
                    continue
            
            if member and member.id not in processed_users:
                previous_nick = member.nick if member.nick else member.name
                try:
                    await member.edit(nick=ign)
                    results.append({
                        "user": member,
                        "ign": ign,
                        "previous_nick": previous_nick,
                        "message_id": message.id
                    })
                    processed_users.add(member.id)
                except discord.Forbidden:
                    failures.append(f"❌ Cannot change {member.display_name}'s nickname (missing permissions)")
                except Exception as e:
                    failures.append(f"❌ Failed for {member.display_name}: {str(e)[:50]}")
    
    embed = discord.Embed(title="🔄 IGN Sync Results", color=0xD4AF36)
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    
    if results:
        synced_count = len(results)
        embed.description = f"✅ Successfully synced **{synced_count}** user{'s' if synced_count != 1 else ''}." 
        
        lines = []
        for r in results[:10]:
            lines.append(f"✓ {r['user'].name} → **{r['ign']}**")
        if synced_count > 10:
            lines.append(f"...and {synced_count - 10} more")
        
        embed.add_field(name="Updated Nicknames", value=_build_truncated_field(lines, joiner="\n"), inline=False)
        
        if failures:
            embed.add_field(name="⚠️ Failures", value=_build_truncated_field(failures[:5], joiner="\n"), inline=False)
    else:
        embed.description = "📭 No IGN patterns found in the last messages."
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="serverinfo", description="Get information about the server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(title=f"ℹ️ {guild.name}", color=0xD4AF36)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="💬 Channels", value=f"Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}", inline=True)
    embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="😀 Emojis", value=str(len(guild.emojis)), inline=True)
    embed.add_field(name="🛡️ Verification", value=str(guild.verification_level), inline=True)
    embed.add_field(name="🔔 Boost Level", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Oda Bot Commands", color=0xD4AF36)
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    
    commands_list = [
        ("🎭 `/pun`", "Get a random Ordis joke"),
        ("💡 `/tip`", "Get a Warframe gameplay tip"),
        ("📊 `/stats`", "View bot statistics"),
        ("🔍 `/find`", "Search messages (Admin)"),
        ("🔄 `/sync_ign`", "Sync IGNs to nicknames (Admin)"),
        ("ℹ️ `/serverinfo`", "Server information"),
        ("❓ `/help`", "Show this message"),
    ]
    
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
    
    embed.set_footer(text="Oda Bot v2.0")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handlers for specific commands
@find.error
async def find_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)

@sync_ign.error
async def sync_ign_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)

# Main
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        logger.error("Please set the DISCORD_TOKEN environment variable.")
        sys.exit(1)
    else:
        try:
            bot.run(TOKEN)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)