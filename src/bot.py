import discord
import requests
import io
import os
from time import sleep
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from spond import spond
from logins import logins

intents = discord.Intents.default()
intents.message_content = True  # Må aktiveres under Privileged Gateway Intents på https://discord.com/developers/applications/
                                # (Message Content Intent)
client = discord.Client(intents=intents)

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

"""
Under her legger du til events og kommandoer som botten skal kunne utføre.
on_message er den mest brukte eventen, og kjøres hver gang botten mottar en melding.
"""

async def main():
    s = spond.Spond(username=logins.get("username"), password=logins.get("password"))
    groups = await s.get_groups()
    print("Getting all spond groups:")
    print(groups)
    await s.clientsession.close()

def get_weather():
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": "Hommersåk",
        "days": 1,
        "aqi": "no",
        "alerts": "no"
    }
    return requests.get(url, params=params).json()
  
async def weather_current(message):
    print('Henter værdata...')
    r = get_weather()

    location = r["location"]
    current = r["current"]
    condition = current["condition"]

    name = location["name"]
    temp = current["temp_c"]
    desc = condition["text"]
    icon = "https:" + condition["icon"]

    path = os.path.join(os.path.dirname(__file__), "minecraft_poster.webp")
    print(f"Path: {path}")

    res = requests.get(icon)
    file = discord.File(io.BytesIO(res.content), filename="weather_icon.png")

    await message.author.send(f"The weather in {name} is currently:\nTemperature: {temp}°C\nDescription: {desc}\n")
    await message.author.send(file=file)

    print(f"Message: {message}")
    print(f"Hentet og sendte været i {name}")

    return

async def weather_sun(message):
    print('Henter værdata...')
    r = get_weather()

    location = r["location"]['name']
    astro = r['forecast']['forecastday'][0]['astro']
    sunrise = astro['sunrise']
    sunset = astro['sunset']

    sr = datetime.strptime(sunrise, '%I:%M %p')
    print(sr.strftime('%H:%M:%S'))

    ss = datetime.strptime(sunset, '%I:%M %p')
    print(ss.strftime('%H:%M:%S'))

    await message.author.send(f"The sun in {location}, today:")
    await message.author.send(f"Sunrise: {sr.strftime('%H:%M')}")
    await message.author.send(f"Sunset: {ss.strftime('%H:%M')}")

@client.event
async def on_ready():
    """on_ready kjøres når botten er klar til å brukes."""
    print(f"Logget inn som {client.user}")


@client.event
async def on_message(message):
    """on_message kjøres når botten mottar en melding."""
    text = message.content
    user = message.author

    normalized = text.strip().lower()
    # Sjekker om meldingen er fra boten selv, for å unngå at den svarer på seg selv.
    if user == client.user:
        return

    if text == "ping":
        await message.channel.send("pong")

    # Samme syntaks kan repeteres for flere kommandoer
    if text.lower() == "hei":
        await message.channel.send(f"Hei {user.mention}!")

    # DM testing
    if normalized == "weather" or normalized == "weather current":
        await weather_current(message)

    if normalized == "weather sun" or normalized == "sun":
        await weather_sun(message)

    else:
        await main()

# Til slutt; kjør botten med token fra token.txt (med litt tips og feilsøking)
# Du kan ignorere dette.
if __name__ == '__main__':
    print('Starter botten.')
    try:
        client.run(open("src/token.txt", "r").read())
    except discord.errors.PrivilegedIntentsRequired:
        print('OBS! Din bot mangler "Message Content Intent", legg til denne \n'
              'på https://discord.com/developers/applications/ (Under Privileged Gateway Intents)')
    except discord.errors.LoginFailure:
        print('Kunne ikke logge på botten, bruker du riktig token i token.txt?')
    except FileNotFoundError:
        print('Finner ikke token.txt, har du kjørt setup.py og limt inn din token?')
    finally:
        # Vent 5 sekunder før EventLoop lukkes, som gir en større og mindre lesbar feilmelding.
        sleep(5)
