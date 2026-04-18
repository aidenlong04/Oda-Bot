from dotenv import load_dotenv
import discord
import os
import random
import subprocess
import sys
import re
import unicodedata


def _build_truncated_field(items, joiner="\n", max_chars=1024, more_fmt="...and {n} more"):
    """Join items with joiner but ensure result length <= max_chars.
    If truncated, append a short "...and N more" suffix.
    """
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
                # fallback: trim to max_chars
                out = out[: max_chars - 3] + "..."
            return out
        out += part
    return out


def sanitize_nickname(raw: str, max_length: int = 32) -> str:
    """Sanitize a proposed nickname to be safe for Discord:
    - Strip control characters and zero-width joiners
    - Remove Discord-style mentions/backticks
    - Remove common emoji by filtering some unicode categories and combining marks
    - Collapse whitespace
    - Trim to max_length
    Returns an empty string if nothing usable remains.
    """
    if not raw:
        return ""
    s = raw
    # Remove common markdown/backtick chars and angle brackets used in mentions
    s = s.replace('`', '')
    s = s.replace('<', '')
    s = s.replace('>', '')
    # Remove Discord mention-like sequences (e.g., @here, @everyone)
    s = re.sub(r"@(?:here|everyone)", "", s, flags=re.IGNORECASE)
    # Remove nick mention patterns like <@!1234567890>
    s = re.sub(r"<@!?(\d+)>", "", s)
    # Normalize to NFKD and drop combining marks (this removes many emoji variants)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.category(ch).startswith('C'))
    # Remove combining marks
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    # Remove leftover variation selectors and zero-width joiners
    s = re.sub(r"[\uFE0E\uFE0F\u200D\u200B]", "", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Trim to max_length
    if len(s) > max_length:
        s = s[:max_length].strip()
    return s

def _normalize_text(text: str) -> str:
    """Normalize text for spam detection: strip special characters between letters,
    collapse whitespace, and lowercase. This defeats common evasion tactics like
    j.o.i.n or j*o*i*n or j-o-i-n."""
    s = text.lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    leet_map = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '7': 't', '@': 'a', '$': 's', '!': 'i',
    }
    s = ''.join(leet_map.get(ch, ch) for ch in s)
    s = re.sub(r'(?<=\w)[^\w\s]+(?=\w)', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# Compiled spam / server-advertisement regex patterns.
SPAM_PATTERNS: list[re.Pattern] = [
    re.compile(
        r'(?:come\s+)?join\s+(?:my|our)\s+(?:\w+\s+){0,3}'
        r'(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    re.compile(
        r'(?:anyone|who|somebody|anybody)\s+'
        r'(?:want|wanna|wants)\s+(?:to\s+)?join',
        re.IGNORECASE,
    ),
    re.compile(
        r'check\s*out\s+(?:my|our)\s+(?:\w+\s+){0,3}'
        r'(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    re.compile(
        r'join\s+us\s+(?:at|on|in)\b',
        re.IGNORECASE,
    ),
    re.compile(
        r'(?:growing|brand\s*new|new|chill|active|friendly)\s+'
        r'(?:\w+\s+){0,2}(?:server|discord|community|guild)',
        re.IGNORECASE,
    ),
    re.compile(
        r'looking\s+for\s+(?:new\s+)?(?:members|people|players|staff)',
        re.IGNORECASE,
    ),
    re.compile(
        r'\bjoin\b.{0,30}\bserver\b|\bserver\b.{0,30}\bjoin\b',
        re.IGNORECASE,
    ),
]


def is_advertisement(text: str) -> bool:
    """Return True if *text* matches any known server-advertisement pattern.
    Discord invite links are checked against the raw text before normalization."""
    raw_lower = text.lower()
    if re.search(r'discord(?:\.gg|\.com/invite)/\S+', raw_lower):
        return True
    cleaned = _normalize_text(text)
    return any(pat.search(cleaned) for pat in SPAM_PATTERNS)


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

        # --- Server-advertisement / spam filter ---
        if message.guild and not message.author.guild_permissions.manage_messages:
            if is_advertisement(message.content):
                try:
                    await message.delete()
                    print(
                        f"Deleted advertisement from {message.author} "
                        f"in #{message.channel}: {message.content[:80]!r}"
                    )
                except discord.Forbidden:
                    print(
                        f"Missing permissions to delete ad message in #{message.channel}"
                    )
                except discord.NotFound:
                    pass
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

@bot.tree.command(name="find", description="Find messages containing specific text in a channel.")
async def find(interaction: discord.Interaction, text: str, channel: discord.TextChannel):
    # Permission check: only users with Administrator may run this command
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)
        return
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except (discord.NotFound, discord.HTTPException):
        pass
    found = []
    async for message in channel.history(limit=100):
        if text.lower() in message.content.lower():
            found.append(message)
    embed = discord.Embed(title="Results", color=0xD4AF36)
    embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
    embed.description = f"Found {len(found)} message{'s' if len(found) != 1 else ''} containing '{text}'."
    if found:
        msg_links = []
        for m in found[:10]:
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{m.id}"
            msg_links.append(f"[Message by {m.author.name}]({message_url})")
        if len(found) > 10:
            msg_links.append(f"...and {len(found) - 10} more")
        embed.add_field(name="Messages", value=_build_truncated_field(msg_links, joiner="\n"), inline=False)
    else:
        embed.add_field(name="Messages", value="None found.", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="sync_ign", description="Sync IGNs from a channel and set as nicknames for all found users.")
async def sync_ign(interaction: discord.Interaction, channel: discord.TextChannel):
    # Permission check: only users with Administrator may run this command
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)
        return
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except (discord.NotFound, discord.HTTPException):
        # Interaction can't be deferred (unknown or already responded). Continue without deferring.
        pass
    messages = []
    processed_users = set()
    results = []
    ign_pattern = re.compile(r"ign:\s*(.+)", re.IGNORECASE)
    async for message in channel.history(limit=100):
        match = ign_pattern.search(message.content)
        if match:
            # Preserve IGN exactly as posted, but remove trailing 'CLAN' section and any '#' discriminator
            ign_raw = match.group(1).strip()
            # Remove anything after 'CLAN' (case-insensitive)
            clan_idx = re.search(r"\bclan\b", ign_raw, re.IGNORECASE)
            if clan_idx:
                ign_raw = ign_raw[:clan_idx.start()].strip()
            # Remove '#' discriminator (e.g., '#1234') and any trailing digits after it
            ign = re.sub(r"#\s*\d+", "", ign_raw).strip()
            # Sanitize and trim to Discord nickname limit (32 chars)
            ign = sanitize_nickname(ign, max_length=32)

            # Try to get the Member from cache, otherwise fetch from API
            member = interaction.guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await interaction.guild.fetch_member(message.author.id)
                except discord.NotFound:
                    # member not found in this guild
                    continue

            # If IGN is empty after cleaning, fallback to author's display name
            if not ign:
                ign = message.author.display_name
                # still sanitize the fallback
                ign = sanitize_nickname(ign, max_length=32)
                if not ign:
                    # nothing usable; skip
                    continue

            if member and member.id not in processed_users:
                previous_nick = member.nick if member.nick else member.name
                try:
                    await member.edit(nick=ign)
                    results.append({
                        "user": member,
                        "ign": ign,
                        "previous_nick": previous_nick,
                        "avatar_url": member.display_avatar.url,
                        "message_id": message.id
                    })
                    processed_users.add(member.id)
                except Exception as e:
                    messages.append(f"Failed to set nickname for {member.display_name}: {e}")
        else:
            continue
    if results:
        # Build a single concise embed summarizing synced users
        embed = discord.Embed(title="IGN Sync Results", color=0xD4AF36)
        # set branded thumbnail at right corner
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        synced_count = len(results)
        embed.description = f"Synced {synced_count} user{'s' if synced_count != 1 else ''}."
        # List up to 10 entries in compact "User - IGN" lines
        lines = []
        for r in results[:10]:
            # show username (not mention/ID) and their new IGN
            lines.append(f"{r['user'].name} - {r['ign']}")
        if synced_count > 10:
            # show a compact summary rather than listing every remaining username
            lines.append(f"...and {synced_count - 10} more")
        embed.add_field(name="Updates", value=_build_truncated_field(lines, joiner="\n"), inline=False)
        # Add compact message links block
        msg_links = []
        for r in results[:5]:
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{r['message_id']}"
            msg_links.append(f"[Message for {r['user'].name}]({message_url})")
        if msg_links:
            embed.add_field(name="Source Messages", value=_build_truncated_field(msg_links, joiner=" | "), inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)
        # Send short error summary if any failures occurred
        if messages:
            await interaction.followup.send(f"Failed to update {len(messages)} user(s).", ephemeral=True)
    else:
        embed = discord.Embed(title="IGN Sync Results", description="No IGN found in the last 100 messages.", color=0xD4AF36)
        # set branded thumbnail at right corner
        embed.set_thumbnail(url="https://ik.imagekit.io/qcxbyrkgu/Golden_Pagoda_Emblem-clear.png?updatedAt=1752791247987")
        await interaction.followup.send(embed=embed, ephemeral=True)

# Main
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
