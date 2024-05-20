#!/bin/bash

# Function to restart the process
restart_process() {
    # Get the process ID of the running discord bot
    process_id=$(ps aux | grep 'python3 pet_discord_bot/tomita_bot_entrypoint.py' | grep -v 'grep' | awk '{print $2}')

    # If the process ID is found, kill the process
    if [ -n "$process_id" ]; then
        kill $process_id
        echo "Killed process with ID: $process_id"
    else
        echo "Process not found"
    fi

    # Start the bot again
    ./run_tomita_bot.sh
    echo "Started the bot"
}

# Infinite loop to restart the process every 4 hours
while true; do
    restart_process
    # Sleep for 4 hours (14400 seconds)
    sleep 14400
done