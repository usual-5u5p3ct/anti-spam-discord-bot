import string
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import joblib
import dill
import nltk
import asyncio
import random
import datetime
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download the 'punkt' resource
nltk.download('punkt')

# Remove punctuation and stopwords using a preprocessing function
class PreProcessText(object):
    def __init__(self):
        pass
    
    def __remove_punctuation(self, text):
        """
        Takes a String 
        return : Return a String 
        """
        message = []
        for x in text:
            if x in string.punctuation:
                pass
            else:
                message.append(x)
        message = ''.join(message)
        
        return message
    
    def __remove_stopwords(self, text):
        """
        Takes a String
        return List
        """
        words= []
        for x in text.split():
            if x.lower() in stopwords.words('english'):
                pass
            else:
                words.append(x)
        return words
    
    def token_words(self,text=''):
        """
        Takes String
        Return Token also called  list of words that is used to 
        Train the Model 
        """
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words
    

# creates an instance of the class PreProcessText
obj = PreProcessText()

# Load the trained model
model = joblib.load("spam.joblib")

# Load the vectorizer using dill
with open("text_vectorizer.joblib", "rb") as f:
    vectorizer = dill.load(f)

# Regular expression pattern to match suspicious links
suspicious_link_pattern = r"(http[s]?:\/\/[^\s]+)"

cat_images = [
    "https://i.pinimg.com/564x/23/86/e3/2386e3023848e6754b8f0ad9597676a7.jpg",
    "https://i.pinimg.com/564x/ba/e1/8e/bae18e221015efbfe6b26953f414cc05.jpg",
    "https://i.pinimg.com/736x/e4/18/e2/e418e22729bd7a202c563e08463b6ad9.jpg",
    "https://i.pinimg.com/564x/89/35/b5/8935b508b4d0f41d1b92700e4d57e363.jpg",
    "https://i.pinimg.com/564x/10/aa/66/10aa66b15e1c2308d9d371f51d919121.jpg",
    "https://i.pinimg.com/736x/46/4c/bc/464cbcdc578945d91bb7ed9d2ec70198.jpg"
]

# Create the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='.', activity=discord.Game(name='minding my own business :D'), intents=intents)

# Define the spam detection threshold (number of messages within a certain time frame)
SPAM_THRESHOLD = 3
SPAM_TIMEFRAME = 3  # in seconds

# Dictionary to keep track of user message counts, warnings, and kicks
user_message_counts = {}
user_warnings = {}
user_kicks = {}

@bot.event
# Tells you when the bot is ready
async def on_ready():
    print('Bot is ready!')
    print('------------------')


@bot.event
async def on_guild_join(guild):
    join_channel = guild.system_channel
    smiley = "\U0001F604"  # smiley emoji using unicode
    speaker = "\U000025B6"  # play emoji
    embed = discord.Embed(
        title=f'Thanks for using me for your server! {smiley}',
        description=f'Removes spam-related messages for better management of the server. '
                    f'\nAlso provides settings for admins to configure. '
                    f'\n\n{speaker} List of available commands are listed below: ',
        color=discord.Color.random()
    )
    embed.add_field(name='Name', value='value', inline=False)
    await join_channel.send(embed=embed)


@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)

        # Check if the user is banned but has joined again
        if member.id in user_kicks:
            # Ban the user if they join again and have previously been kicked multiple times
            kick_count = user_kicks[member.id]
            if kick_count >= 3:
                ban_reason = "Continued spamming after being kicked multiple times"
                await guild.ban(member, reason=ban_reason)
                ban_channel = discord.utils.get(guild.text_channels, name="borak2")  # Adjust the channel name if necessary
                if ban_channel:
                    await ban_channel.send(f"{member.mention} has been banned. Reason: {ban_reason}")


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself or other bots
    if message.author == bot.user or message.author.bot:
        return

    # Check if the message is a bot command
    if message.content.startswith(bot.command_prefix):
        # Check if the author is an admin or the owner
        if message.author.guild_permissions.administrator or message.author.id == "294478798152269824":
            await bot.process_commands(message)  # Allow the admin/owner to use commands in any channel
        else:
            # Check if the command is being sent in the correct channel (tally with your channel name)
            if message.channel.name != "bot-commands":
                # Delete the command message
                await message.delete()

                # Issue a warning to the user
                warning_message = await message.channel.send(f"{message.author.mention} Bot commands should be sent in the #bot-commands channel.")

                # Wait for 3 seconds
                await asyncio.sleep(10)

                # Delete the warning message
                await warning_message.delete()

            return  # Return after handling the command

    # Check if the user is sending images in the general chatroom (tally with your channel name)
    if message.channel.name == "borak2" and len(message.attachments) > 0:
        # Delete the message
        await message.delete()

        # Warn the user
        warning_message = await message.channel.send(f"{message.author.mention} Sending images in the general chatroom is not allowed.")

        # Delete the warning message after 3 seconds
        await asyncio.sleep(3)
        await warning_message.delete()

        # Delete the user's messages (excluding bot commands) from the general chatroom
        async for user_message in message.channel.history(limit=100):
            if user_message.author == message.author and not user_message.content.startswith(bot.command_prefix):
                await user_message.delete()

        return

    # Check if the user is sending suspicious links
    if re.search(suspicious_link_pattern, message.content):
        # Delete the message
        await message.delete()

        # Issue a warning to the user
        warning_message = await message.channel.send(f"{message.author.mention} Sending suspicious links is not allowed.")

        # Wait for 3 seconds
        await asyncio.sleep(3)

        # Delete the warning message
        await warning_message.delete()

        # Kick the user after 3 warnings
        warnings = 1
        while warnings < 3:
            await asyncio.sleep(3)
            if not re.search(suspicious_link_pattern, message.content):
                break  # Break the loop if user stops sending suspicious links
            warnings += 1
            if re.search(suspicious_link_pattern, message.content):
                warning_message = await message.channel.send(f"{message.author.mention} Final warning! Sending suspicious links is not allowed.")
                await asyncio.sleep(3)
                await warning_message.delete()
            else:
                break
        else:
            # Kick the user
            await message.author.kick(reason="Sending suspicious links")

   # Check if the user has been previously kicked or banned
    author_id = message.author.id
    if author_id in user_kicks:
        kick_count = user_kicks[author_id]

        if kick_count == 3:
            guild = message.guild
            ban_reason = "Received 3 kicks and continued spamming"
            await guild.ban(message.author, reason=ban_reason)
            ban_channel = discord.utils.get(guild.text_channels, name="borak2")  # Adjust the channel name if necessary
            if ban_channel:
                await ban_channel.send(f"{message.author.mention} has been banned. Reason: {ban_reason}")
            return  # Return after banning the user to avoid duplicate actions

    # Check for spamming by the user
    author_id = message.author.id
    current_time = message.created_at.timestamp()

    if author_id not in user_message_counts:
        # First message from the user
        user_message_counts[author_id] = [(current_time, 1)]
    else:
        # User has sent messages before
        message_times = user_message_counts[author_id]
        # Remove old messages outside of the timeframe
        message_times = [(t, count) for t, count in message_times if current_time - t <= SPAM_TIMEFRAME]
        # Add current message timestamp
        message_times.append((current_time, len(message_times) + 1))
        user_message_counts[author_id] = message_times

        if len(message_times) >= SPAM_THRESHOLD:
            # User has sent more messages than the threshold within the timeframe
            await message.channel.send(f"{message.author.mention} Stop spamming!")

            # Check if the user has reached the warning limit
            if author_id in user_warnings and user_warnings[author_id] >= SPAM_THRESHOLD:
                # Increase the kick count for the user
                if author_id not in user_kicks:
                    user_kicks[author_id] = 1
                else:
                    user_kicks[author_id] += 1

                # Kick the user after their 3rd warning
                if user_kicks[author_id] == 4:
                    guild = message.guild
                    kick_reason = "Received 3 warnings and continued spamming."
                    await guild.kick(message.author, reason=kick_reason)
                    kick_channel = discord.utils.get(guild.text_channels, name="borak2")  # Adjust the channel name if necessary
                    if kick_channel:
                        await kick_channel.send(f"{message.author.mention} has been kicked. Reason: {kick_reason}")

                    del user_kicks[author_id]  # Remove the user from the kicks dictionary upon kicking

            else:
                # Increase the warning count for the user
                if author_id not in user_warnings:
                    user_warnings[author_id] = 1
                else:
                    user_warnings[author_id] += 1

                # Kick the user after their 3rd warning
                if user_warnings[author_id] == 4:
                    guild = message.guild
                    kick_reason = "Received 3 warnings."
                    await guild.kick(message.author, reason=kick_reason)
                    kick_channel = discord.utils.get(guild.text_channels, name="borak2")  # Adjust the channel name if necessary
                    if kick_channel:
                        await kick_channel.send(f"{message.author.mention} has been kicked. Reason: {kick_reason}")
                    return  # Return after kicking the user to avoid duplicate actions
                

                await message.channel.send(f"{message.author.mention} Warning {user_warnings[author_id]}!")

    # Preprocess the text
    processed_text = obj.token_words(message.content)

    # Transform the text using the vectorizer
    text_vector = vectorizer.transform([processed_text])

    # Make the prediction
    prediction = model.predict(text_vector)

    # Get the predicted label
    predicted_label = prediction[0]

    # Send the prediction label as a reply
    if predicted_label == "spam":
        # Warn the user for spamming
        await message.channel.send(f"Warning: {message.author.mention} Your message has been flagged as spam. Please refrain from spamming.")
    else:
        await message.channel.send(f"Original message: {message.content}\nPredicted label: {predicted_label}")

    # Process bot commands
    await bot.process_commands(message)


@bot.command(name='hello')
async def hello_command(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')


@bot.command()
async def cat(ctx):
    # Select a random cat image URL
    random_cat_image = random.choice(cat_images)

    # Send the cat image to the channel
    await ctx.send(random_cat_image)


@bot.command()
async def commands(ctx):
    # Create an embedded message
    embed = discord.Embed(title="List of Available Commands")
    
    # Add command descriptions
    embed.add_field(name=".hello", value="Reply with 'Hello!'", inline=False)
    embed.add_field(name=".cat", value="Send a random cat image", inline=False)
    embed.add_field(name=".commands", value="Display this list of available commands", inline=False)
    
    # Send the embedded message to the channel
    await ctx.send(embed=embed)


@bot.command()
@has_permissions(administrator=True)
async def userdata(ctx, member: discord.Member):
    # Get current time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)

    # Get user's join duration
    join_duration = now - member.joined_at
    join_days = join_duration.days
    join_hours = join_duration.seconds // 3600
    join_minutes = (join_duration.seconds // 60) % 60

    # Get user's message count
    user_message_count = user_message_counts.get(member.id, 0)

    # Get user's kick count
    user_kick_count = user_kicks.get(member.id, 0)

    # Check if user is banned
    user_banned = False
    if member.id in user_kicks and user_kicks[member.id] > 0:
        user_banned = True

    # Create an embedded message
    embed = discord.Embed(title="User Data", color=discord.Color.blue())
    embed.add_field(name="Username", value=member.name, inline=False)
    embed.add_field(name="Join Duration", value=f"{join_days} days, {join_hours} hours, {join_minutes} minutes", inline=False)
    embed.add_field(name="Message Count", value=user_message_count, inline=False)
    embed.add_field(name="Kick Count", value=user_kick_count, inline=False)
    embed.add_field(name="Banned", value=user_banned, inline=False)

    # Send the embedded message to the channel
    await ctx.send(embed=embed)


@bot.command()
async def clear(ctx):
    # Calculate the time threshold for clearing messages
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=1)

    # Get all messages in the channel within the time threshold
    messages = []
    async for message in ctx.channel.history(after=time_threshold):
        messages.append(message)
    await ctx.channel.delete_messages(messages)
    clear_message = await ctx.send(f"All messages within the last 1 hour have been cleared.")

    # Wait for 3 seconds
    await asyncio.sleep(3)

    await clear_message.delete()

    return



bot.run('INSERT BOT TOKEN HERE')
