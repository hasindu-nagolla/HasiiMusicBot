from pyrogram import filters
import random
from HasiiMusic import app


def get_random_message(love_percentage):
    if love_percentage <= 30:
        return random.choice([
            "Love? I’ve seen stronger Wi-Fi signals.",
            "Not much spark, maybe just friendship.",
            "This looks weaker than instant noodles."
        ])
    elif love_percentage <= 70:
        return random.choice([
            "Good, but don’t expect a movie ending.",
            "It’s working… kinda like a cheap phone.",
            "Better than nothing, I guess."
        ])
    else:
        return random.choice([
            "Wow, perfect! Until you argue about food.",
            "Great match… let’s see how long it lasts.",
            "True love? Or just today’s mood?"
        ])


@app.on_message(filters.command("love", prefixes="/"))
async def love_command(client, message):
    command, *args = message.text.split(" ")
    if len(args) >= 2:
        name1 = args[0].strip()
        name2 = args[1].strip()

        love_percentage = random.randint(10, 100)
        love_message = get_random_message(love_percentage)

        response = f"{name1}💕 + {name2}💕 = {love_percentage}%\n\n{love_message}"
    else:
        response = "Please enter two names after /love command.\nExample: `/love Alice Bob`"

    await app.send_message(message.chat.id, response)
