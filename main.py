import csv
import random
import discord
from discord import app_commands
from discord.ext import commands, tasks
import pytz
import logging
from datetime import datetime, time
from dotenv import load_dotenv
import os

print(f"Discord.py version: {discord.__version__}")
est = pytz.timezone('America/New_York')
trigger_time = time(hour=17, minute=40)

# Debug token loading
print("=== DEBUGGING TOKEN LOADING ===")
load_dotenv()
token1 = os.getenv('DISCORD_TOKEN')
token2 = os.environ.get('DISCORD_TOKEN')

print(f"Method 1 (load_dotenv): {token1 is not None}")
print(f"Method 1 length: {len(token1) if token1 else 0}")
print(f"Method 2 (direct): {token2 is not None}")
print(f"Method 2 length: {len(token2) if token2 else 0}")
print(f"Tokens match: {token1 == token2}")

# Print all environment variables that contain 'DISCORD' or 'TOKEN'
print("Environment variables containing 'DISCORD' or 'TOKEN':")
for key, value in os.environ.items():
    if 'DISCORD' in key.upper() or 'TOKEN' in key.upper():
        print(f"  {key}: {value[:10] if value else 'None'}...")

# Use whichever token exists
token = token1 or token2

print(f"Final token: {token is not None}")
print(f"Final token type: {type(token)}")
print(f"Final token length: {len(token) if token else 0}")

if not token:
    print("ERROR: No token found in environment variables!")
    print("Available environment variables:")
    for key in sorted(os.environ.keys()):
        print(f"  {key}")
    exit(1)
else:
    print(f"✅ Using token of length: {len(token)}")

print("=== END DEBUG ===")

handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')

intents = discord.Intents.default()
intents.message_content = True

# Channel configuration - Double-checked IDs
ALLOWED_CHANNEL_ID = 1405231456577523832  # Commands only work here
DAILY_UPDATE_CHANNEL_ID = 1405231456577523832  # Daily messages go here (confirmed)

class RestrictedBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        self.allowed_channel_id = ALLOWED_CHANNEL_ID

bot = RestrictedBot()

#############################################################################
def initalInvestment(investment):
  data=[["Total Money invested", "Party investment","Favorability"],
    [investment*2, investment,.001]]
  with open("data.csv", mode="w", newline="") as file:
    write=csv.writer(file)
    write.writerows(data)
#############################################################################
def resetInvestment():
  investment=0
  data=[["Total Money invested", "Party investment","Favorability"],
    [investment*2, investment,.001]]
  with open("data.csv", mode="w", newline="") as file:
    write=csv.writer(file)
    write.writerows(data)
#############################################################################
def rollDay():
  change = 1
  totalInvestment = float(companyValue())
  favorability = float(Favorability())
  partyInvestment = float(partyValue())
  result = random.randrange(1,7,1)
  match result:
    case 1:
      change = .98
    case 2:
      change = .99
    case 3:
      change = .995
    case 4:
      change = 1.005
    case 5:
      change = 1.01
    case 6:
      change = 1.02
  change = change + favorability 
  totalInvestment = round(totalInvestment * change,2)
  partyInvestment = round(partyInvestment * change,2)
  data = [["Total Money invested", "Party investment","Favorability"],
    [totalInvestment, partyInvestment,favorability]]
  with open("data.csv", mode="w", newline="") as file:
    write = csv.writer(file)
    write.writerows(data)
#############################################################################
def companyValue():
    with open("data.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            totalInvestment = float(row["Total Money invested"])
    return(round(totalInvestment,2))
#############################################################################
def partyValue():
    with open("data.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            partyInvestment = float(row["Party investment"])
    return(round(partyInvestment,2))
#############################################################################
def Favorability():
    with open("data.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            Favorability = float(row["Favorability"])
    return((Favorability))
#############################################################################
def changeValue(type,value):
    totalInvestment = companyValue()
    partyInvestment = partyValue()
    favorability = Favorability()
    match type:
        case "Total":
            totalInvestment = value
        case "Party":
            partyInvestment = value
        case "Favor":
            favorability = value
        case _:
            raise ValueError(f"Invalid parameter '{type}'. Use 'Total', 'Party', or 'Favor'")
    data = [["Total Money invested", "Party investment", "Favorability"],
    [totalInvestment, partyInvestment, favorability]]
    with open("data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)
#############################################################################
def payRoll(money):
    string = "You have earned "
    income = round(money * 0.01, 2)
    parts = str(income).split('.')
    gold = int(parts[0])
    
    # Handle cases where there might not be decimal places or only one decimal place
    if len(parts) > 1:
        decimal_part = parts[1]
        silver = int(decimal_part[0]) if len(decimal_part) > 0 else 0
        copper = int(decimal_part[1]) if len(decimal_part) > 1 else 0
    else:
        silver = 0
        copper = 0
    
    parts_added = []
    
    if gold > 0:
        parts_added.append(f"{gold} Gold")
    if silver > 0:
        parts_added.append(f"{silver} Silver")
    if copper > 0:
        parts_added.append(f"{copper} Copper")
    
    if len(parts_added) == 0:
        string += "nothing"
    elif len(parts_added) == 1:
        string += parts_added[0]
    elif len(parts_added) == 2:
        string += f"{parts_added[0]} and {parts_added[1]}"
    else:
        string += f"{', '.join(parts_added[:-1])}, and {parts_added[-1]}"
    
    string += "."
    return string

#############################################################################
last_update_date = None

@tasks.loop(minutes=1)
async def dailyUpdate():
    global last_update_date
    now = datetime.now()
    current_date = now.date()
    
    if now.hour == 0 and now.minute == 0 and current_date != last_update_date:
        print(f"Daily update triggered at {datetime.now(est)}")
        last_update_date = current_date
        channel = bot.get_channel(DAILY_UPDATE_CHANNEL_ID)  # Still uses original channel
        print(channel)
        if channel:
            rollDay()
            await channel.send(f"Daily update! New values: Total: {companyValue()}, Party: {partyValue()}.")
        else:
            print("Channel not found!")

@dailyUpdate.before_loop
async def before_daily_update():
    print("Daily update task is starting...")
    await bot.wait_until_ready()
    print("Bot is ready, daily update task will begin")

# Interaction check to restrict commands to specific channel
@bot.check
async def globally_block_dms(interaction: discord.Interaction):
    # Allow commands only in the specific channel
    if hasattr(interaction, 'channel') and interaction.channel and interaction.channel.id == ALLOWED_CHANNEL_ID:
        return True
    # Silently fail for other channels (no error message)
    return False

@bot.event
async def on_ready():
    print(f"Bot is now online")
    dailyUpdate.start()
    print("Daily update task started")
    
    # Debug: Print all guilds and channels the bot can see
    print(f"Bot is in {len(bot.guilds)} guild(s):")
    for guild in bot.guilds:
        print(f"  Guild: {guild.name} (ID: {guild.id})")
        text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
        print(f"    Text channels: {len(text_channels)}")
        for ch in text_channels[:10]:  # Show first 10 text channels
            print(f"      {ch.name} (ID: {ch.id})")
    
    # Try to find channels by ID across all guilds
    allowed_channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    daily_channel = bot.get_channel(DAILY_UPDATE_CHANNEL_ID)
    
    print(f"Allowed channel search result: {allowed_channel}")
    print(f"Daily channel search result: {daily_channel}")
    
    # Determine which guild to sync to
    target_guild = None
    if allowed_channel:
        target_guild = allowed_channel.guild
        print(f"Using guild from allowed channel: {target_guild.name}")
    elif daily_channel:
        target_guild = daily_channel.guild
        print(f"Using guild from daily channel: {target_guild.name}")
    elif bot.guilds:
        # Fallback: use the first guild
        target_guild = bot.guilds[0]
        print(f"Fallback: using first guild: {target_guild.name}")
    
    if target_guild:
        try:
            # Sync commands to the guild
            synced = await bot.tree.sync(guild=target_guild)
            print(f"✅ Synced {len(synced)} command(s) to guild: {target_guild.name}")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
            # Fallback: try global sync
            try:
                synced = await bot.tree.sync()
                print(f"✅ Fallback: Synced {len(synced)} command(s) globally")
            except Exception as e2:
                print(f"❌ Global sync also failed: {e2}")
    else:
        print("❌ No guilds found!")

@bot.tree.command(name="firstinvestment", description="Set the initial investment amount")
@app_commands.describe(amount="The initial investment amount")
async def firstInvestment(interaction: discord.Interaction, amount: float):
    try:
        await interaction.response.send_message(f"You set the initial investment to {amount}", ephemeral=True)
        initalInvestment(amount)
    except Exception as e:
        await interaction.response.send_message("Please send a valid number!", ephemeral=True)

@bot.tree.command(name="info", description="Get current investment information")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(f"Total investment: {companyValue()}, Party investment: {partyValue()}, Favorability: {Favorability()}", ephemeral=True)

@bot.tree.command(name="reset", description="Reset all investments")
async def reset(interaction: discord.Interaction):
    resetInvestment()
    await interaction.response.send_message("Investment has been reset.", ephemeral=True)

@bot.tree.command(name="change", description="Change a specific value")
@app_commands.describe(
    type="Type of value to change (Total, Party, or Favor)",
    value="New value to set"
)
@app_commands.choices(type=[
    app_commands.Choice(name="Total", value="Total"),
    app_commands.Choice(name="Party", value="Party"),
    app_commands.Choice(name="Favor", value="Favor")
])
async def change(interaction: discord.Interaction, type: app_commands.Choice[str], value: float):
    try:
        changeValue(type.value, value)
        await interaction.response.send_message(f"{type.name}'s value has been changed to {value}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("There was an error processing this request.", ephemeral=True)

@bot.tree.command(name="payroll", description="Shows your payroll (1% of company's value)")
async def payroll(interaction: discord.Interaction):
    company_val = companyValue()
    payroll_message = payRoll(company_val)
    await interaction.response.send_message(f"{payroll_message} (1% of company value: ${company_val:,.2f})", ephemeral=True)

@bot.tree.command(name="sync", description="Manually sync commands (admin only)")
async def sync_commands(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        try:
            synced = await bot.tree.sync(guild=interaction.guild)
            await interaction.response.send_message(f"✅ Synced {len(synced)} commands!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to sync: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)

@bot.tree.command(name="testupdate", description="Manually trigger daily update (admin only)")
async def test_update(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        try:
            await interaction.response.defer(ephemeral=True)
            
            print(f"🧪 TEST UPDATE called by {interaction.user.name}")
            print(f"🔍 Searching for channel ID: {DAILY_UPDATE_CHANNEL_ID}")
            
            channel = bot.get_channel(DAILY_UPDATE_CHANNEL_ID)
            if channel:
                print(f"✅ Found channel: '{channel.name}' in guild '{channel.guild.name}'")
                
                # Check permissions
                permissions = channel.permissions_for(channel.guild.me)
                print(f"🔐 Bot permissions in #{channel.name}:")
                print(f"   - Send Messages: {permissions.send_messages}")
                print(f"   - View Channel: {permissions.view_channel}")
                
                if not permissions.send_messages:
                    await interaction.followup.send(f"❌ Bot doesn't have Send Messages permission in {channel.mention}", ephemeral=True)
                    return
                
                print(f"🎲 Running rollDay()...")
                rollDay()
                print(f"✅ rollDay() completed")
                
                # Get values
                total_val = companyValue()
                party_val = partyValue()
                print(f"📊 New values - Total: {total_val}, Party: {party_val}")
                
                message = f"🧪 TEST Daily update! New values: Total: {total_val}, Party: {party_val}."
                print(f"📤 Sending message: '{message}'")
                
                sent_message = await channel.send(message)  # This is NOT ephemeral - public message
                print(f"✅ Test message sent successfully! Message ID: {sent_message.id}")
                
                await interaction.followup.send(f"✅ Test update sent to {channel.mention}\nMessage: {message}", ephemeral=True)
            else:
                print(f"❌ Channel {DAILY_UPDATE_CHANNEL_ID} not found!")
                
                # List available channels for debugging
                debug_info = "Available channels:\n"
                for guild in bot.guilds:
                    debug_info += f"**{guild.name}:**\n"
                    for ch in guild.text_channels[:10]:  # Limit to 10 to avoid message length issues
                        debug_info += f"  #{ch.name} (ID: {ch.id})\n"
                
                await interaction.followup.send(f"❌ Could not find channel with ID {DAILY_UPDATE_CHANNEL_ID}\n\n{debug_info}", ephemeral=True)
        except Exception as e:
            print(f"❌ Test update error: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)

# Final check before running bot
print("=== FINAL TOKEN CHECK ===")
print(f"About to run bot with token: {token is not None}")
print(f"Token type: {type(token)}")
if token:
    print(f"Token length: {len(token)}")
    print(f"Token starts with: {token[:5]}...")
else:
    print("❌ TOKEN IS NONE - BOT WILL FAIL!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)