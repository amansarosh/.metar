import asyncio
import discord
import requests
from bs4 import BeautifulSoup
# import config
import datetime

import config

client = discord.Client(intents=discord.Intents.all())

# Zulu Day in time in DDHHMMZ Format
now_utc = datetime.datetime.utcnow() # Get current UTC time
day = now_utc.strftime('%d') # Get day of the month as a string
hour = now_utc.strftime('%H') # Get hour as a string
minute = now_utc.strftime('%M') # Get minute as a string
zulu_time = day + hour + minute + 'Z' # Concatenate strings to form the desired format


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('.metar'):
        airport_code = message.content.split()[1].upper()
        url = f'https://www.checkwx.com/weather/{airport_code}/metar'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            metar = soup.find('p', class_='font-mono')
            airport_name = soup.find_all("h2")[0].get_text()

            # Check if the message contains "-f"
            if '-f' in message.content:
                altimeter_p = soup.find('p', string='Altimeter')
                altimeter = altimeter_p.find_next_sibling('p').text if altimeter_p else "Not available"

                pressure_p = soup.find('p', string='Pressure')
                pressure = pressure_p.find_next_sibling('p').text if pressure_p else "Not available"

                wind_p = soup.find('p', string='Wind')
                wind = wind_p.find_next_sibling('p').text if wind_p else "Not available"
                wind1 = wind.split("\n")[2].strip()
                wind2 = wind.split("\n")[4].strip()
                wind = f"{wind1} {wind2}"

                temperature_p = soup.find('p', string='Temperature')
                temperature = temperature_p.find_next_sibling('p').text if temperature_p else "Not available"
                temperature1 = temperature.split("\n")[0 ].strip()
                temperature2 = temperature.split("\n")[ 1].strip()
                temperature = f"{temperature1} {temperature2}"

                weather_data = f"Altimeter: {altimeter}\nPressure: {pressure}\nWind: {wind}\nTemperature: {temperature}\n"
                await message.channel.send(f"The current Zulu time is {zulu_time}")
                await message.channel.send(content=f'```METAR for {airport_code} - {airport_name}:'
                                                   f'\n\n{metar.text}\n\n{weather_data}```')
            else:
                await message.channel.send(content=f'```METAR for {airport_code} - {airport_name}:\n\n{metar.text}```')
        else:
            await message.channel.send(f'Error getting METAR for {airport_code}')


client.run(config.discord_token)