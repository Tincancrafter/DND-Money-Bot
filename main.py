# -*- coding: utf-8 -*-
import sys
import io
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

# Fix encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("Discord.py version:", discord.__version__)
est = pytz.timezone('America/New_York')
trigger_time = time(hour=17, minute=40)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Debug: Check if token is loaded
if not token:
    print("❌ ERROR: DISCORD_TOKEN not found in environment variables!")
    print("Make sure you have a .env file with DISCORD_TOKEN=your_token_here")
    exit(1)
else:
    print("✅ Token loaded successfully")
    print(f"Token length: {len(token)} characters")

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

# Custom check function for specific role only
AUTHORIZED_ROLE_ID = 1177986158324613151

def authorized_role_only():
    def predicate(interaction: discord.Interaction) -> bool:
        # Check if user has the specific role
        if interaction.guild is None:
            return False
        user_roles = [role.id for role in interaction.user.roles]
        return AUTHORIZED_ROLE_ID in user_roles
    return app_commands.check(predicate)

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
    try:
        with open("data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                totalInvestment = float(row["Total Money invested"])
        return(round(totalInvestment,2))
    except (FileNotFoundError, KeyError):
        # If file doesn't exist or headers are wrong, create default file
        print("⚠️ data.csv not found or invalid, creating default file...")
        initalInvestment(100)  # Create with default investment of 100
        return 100.0

#############################################################################
def partyValue():
    try:
        with open("data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                partyInvestment = float(row["Party investment"])
        return(round(partyInvestment,2))
    except (FileNotFoundError, KeyError):
        # If file doesn't exist or headers are wrong, create default file
        print("⚠️ data.csv not found or invalid, creating default file...")
        initalInvestment(100)  # Create with default investment of 100
        return 100.0

#############################################################################
def Favorability():
    try:
        with open("data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Favorability = float(row["Favorability"])
        return((Favorability))
    except (FileNotFoundError, KeyError):
        # If file doesn't exist or headers are wrong, create default file
        print("⚠️ data.csv not found or invalid, creating default file...")
        initalInvestment(100)  # Create with default investment of 100
        return 0.001

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
    
    if now.hour == 4 and now.minute == 0 and current_date != last_update_date:
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
    
    # Initialize data.csv if it doesn't exist
    try:
        companyValue()  # This will create the file if it doesn't exist
        print("✅ Data file loaded successfully")
    except Exception as e:
        print(f"⚠️ Creating default data file: {e}")
        initalInvestment(100)
    
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
            # Clear existing commands first
            bot.tree.clear_commands(guild=target_guild)
            
            # Sync commands to the guild
            synced = await bot.tree.sync(guild=target_guild)
            print(f"✅ Synced {len(synced)} command(s) to guild: {target_guild.name}")
            
            # List all synced commands for debugging
            print("📋 Synced commands:")
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")
                
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
@authorized_role_only()
async def firstInvestment(interaction: discord.Interaction, amount: float):
    try:
        await interaction.response.send_message(f"You set the initial investment to {amount}", ephemeral=True)
        initalInvestment(amount)
    except Exception as e:
        await interaction.response.send_message("Please send a valid number!", ephemeral=True)

# INFO command - accessible to everyone (no role restriction)
@bot.tree.command(name="info", description="Get current investment information")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(f"Total investment: {companyValue()}, Party investment: {partyValue()}, Favorability: {Favorability()}", ephemeral=True)

# DEBUG command - accessible to everyone to test if commands are working
@bot.tree.command(name="ping", description="Test if the bot is responding")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot is working!", ephemeral=True)

@bot.tree.command(name="reset", description="Reset all investments")
@authorized_role_only()
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
@authorized_role_only()
async def change(interaction: discord.Interaction, type: app_commands.Choice[str], value: float):
    try:
        changeValue(type.value, value)
        await interaction.response.send_message(f"{type.name}'s value has been changed to {value}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("There was an error processing this request.", ephemeral=True)

@bot.tree.command(name="payroll", description="Shows your payroll (1% of company's value)")
@authorized_role_only()
async def payroll(interaction: discord.Interaction):
    company_val = companyValue()
    payroll_message = payRoll(company_val)
    await interaction.response.send_message(f"{payroll_message} (1% of company value: ${company_val:,.2f})", ephemeral=True)

@bot.tree.command(name="sync", description="Manually sync commands (authorized role only)")
@authorized_role_only()
async def sync_commands(interaction: discord.Interaction):
    try:
        synced = await bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"✅ Synced {len(synced)} commands!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to sync: {e}", ephemeral=True)

@bot.tree.command(name="testupdate", description="Manually trigger daily update (authorized role only)")
@authorized_role_only()
async def test_update(interaction: discord.Interaction):
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

# NEW COMMAND: Manual roll for authorized role only
@bot.tree.command(name="manualroll", description="Manually roll the daily investment changes (authorized role only)")
@authorized_role_only()
async def manual_roll(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        
        print(f"🎲 MANUAL ROLL called by {interaction.user.name}")
        
        # Store old values for comparison
        old_total = companyValue()
        old_party = partyValue()
        old_favor = Favorability()
        
        # Perform the roll
        rollDay()
        
        # Get new values
        new_total = companyValue()
        new_party = partyValue()
        new_favor = Favorability()
        
        # Calculate changes
        total_change = new_total - old_total
        party_change = new_party - old_party
        total_percent = ((new_total / old_total) - 1) * 100 if old_total != 0 else 0
        party_percent = ((new_party / old_party) - 1) * 100 if old_party != 0 else 0
        
        # Format the response
        response = f"🎲 **Manual Roll Complete!**\n\n"
        response += f"**Total Investment:**\n"
        response += f"  Old: ${old_total:,.2f}\n"
        response += f"  New: ${new_total:,.2f}\n"
        response += f"  Change: ${total_change:+,.2f} ({total_percent:+.2f}%)\n\n"
        response += f"**Party Investment:**\n"
        response += f"  Old: ${old_party:,.2f}\n"
        response += f"  New: ${new_party:,.2f}\n"
        response += f"  Change: ${party_change:+,.2f} ({party_percent:+.2f}%)\n\n"
        response += f"**Favorability:** {new_favor}"
        
        print(f"✅ Manual roll completed - Total: {old_total} -> {new_total}, Party: {old_party} -> {new_party}")
        
        await interaction.followup.send(response, ephemeral=True)
        
    except Exception as e:
        print(f"❌ Manual roll error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        await interaction.followup.send(f"❌ Error during manual roll: {e}", ephemeral=True)

# Error handler for role-restricted commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        # This will catch role permission failures
        await interaction.response.send_message("❌ You need the required role to use this command.", ephemeral=True)
    else:
        # Handle other errors
        print(f"Command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An error occurred while processing the command.", ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)