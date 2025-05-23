import os
import threading
import traceback
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
from flask import Flask
import asyncio

# Environment variables
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Select the first available model that supports text generation
def get_first_available_model():
    for m in genai.list_models():
        # Try to find a model that supports 'generateContent'
        if getattr(m, "generation_methods", None):
            if "generateContent" in m.generation_methods:
                return m.name
    raise RuntimeError("No Gemini models with text generation capability found for your API key.")

MODEL_NAME = get_first_available_model()
model = genai.GenerativeModel(MODEL_NAME)

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
intents.message_content = True  # Ensure this is enabled in the Discord developer portal!
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

# /owner command
@tree.command(name="owner", description="Shows the owner of the bot")
async def owner_command(interaction: discord.Interaction):
    await interaction.response.send_message("The owner of this bot is xcho_ (حذيفة)", ephemeral=True)

# Listen for messages and reply only if bot is mentioned
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        prompt = f"Reply as a close, supportive, and chill friend. Here's what they said: \"{message.content}\""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, model.generate_content, prompt)
            reply = response.text.strip()
            await message.channel.send(reply)
        except Exception as e:
            print(f"Error from Gemini API: {e}")
            traceback.print_exc()
            await message.channel.send("Oops, I had a small brain freeze💔💔")
    # Allow commands to be processed
    await bot.process_commands(message)

if __name__ == "__main__":
    # Run Flask in a thread
    threading.Thread(target=run_flask, daemon=True).start()
    # Run Discord bot
    bot.run(DISCORD_TOKEN)
