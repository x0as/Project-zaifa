import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# In-memory storage for assigned channel
assigned_channel_id = None

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

# /owner command
@tree.command(name="owner", description="Shows the owner of the bot")
async def owner_command(interaction: discord.Interaction):
    await interaction.response.send_message("The owner of this bot is xcho_ (حذيفة)", ephemeral=True)

# /channel assign command
@tree.command(name="channel", description="Channel management")
@app_commands.describe(action="Choose an action: assign")
@app_commands.choices(action=[
    app_commands.Choice(name="assign", value="assign"),
])
async def channel_command(interaction: discord.Interaction, action: app_commands.Choice[str]):
    global assigned_channel_id
    if action.value == "assign":
        assigned_channel_id = interaction.channel.id
        await interaction.response.send_message(f"This channel has been assigned for friendly replies 💬", ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    global assigned_channel_id

    if message.author == bot.user or assigned_channel_id is None:
        return

    if message.channel.id != assigned_channel_id:
        return

    prompt = f"Reply as a close, supportive, and casual friend would. Here's what they said: \"{message.content}\""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
        await message.channel.send(reply)
    except Exception as e:
        print(f"Error: {e}")
        await message.channel.send("Oops, I had a small brain freeze 😅")

bot.run(DISCORD_TOKEN)
