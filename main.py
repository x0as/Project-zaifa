import os
import threading
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
from flask import Flask

# Environment variables
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Flask app to keep Render happy
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

assigned_channel_id = None  # In-memory channel ID storage

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

# Slash command: /owner
@tree.command(name="owner", description="Shows the owner of the bot")
async def owner_command(interaction: discord.Interaction):
    await interaction.response.send_message("The owner of this bot is xcho_ (حذيفة)", ephemeral=True)

# Slash command: /channel assign
@tree.command(name="channel", description="Channel management")
@app_commands.describe(action="Choose an action: assign")
@app_commands.choices(action=[
    app_commands.Choice(name="assign", value="assign"),
])
async def channel_command(interaction: discord.Interaction, action: app_commands.Choice[str]):
    global assigned_channel_id
    if action.value == "assign":
        assigned_channel_id = interaction.channel.id
        await interaction.response.send_message("This channel has been assigned for friendly replies 💬", ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    global assigned_channel_id

    if message.author == bot.user or assigned_channel_id is None:
        return

    if message.channel.id != assigned_channel_id:
        return

    prompt = f"Reply as a close, supportive, and chill friend. Here's what they said: \"{message.content}\""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
        await message.channel.send(reply)
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        await message.channel.send("Oops, I had a small brain freeze 😅")

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=run_flask).start()
    # Run Discord bot
    bot.run(DISCORD_TOKEN)
