__author__ = 'parsons'

from datetime import datetime
import requests
import json
import logging
from time import sleep
import os
import smtplib


DEFAULT_LIST = ['Dragonite', 'Snorlax', 'Aerodactyl', 'Venusaur', 'Charizard', 'Clefable', 'Omastar', 'Ditto', 'Articuno', 'Zapdos', 'Moltres', 'Mewtwo', 'Mew']
SENT_ALERTS = []
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
CUR_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    with open('{0}/config.json'.format(CUR_DIR), 'r') as f:
        config = json.load(f)

    for name in config.keys():
        url = config[name]['url']
        email = config[name]['email']
        poke_list = config[name]['list']
        fromemail = config[name]['from_email']
        if len(poke_list) == 0:
            poke_list = DEFAULT_LIST

        response = requests.get(url)

        try:
            raw_data = json.loads(response.content)
        except:
            raw_data = []

        for pokemon in raw_data['pokemons']:
            pokemon['trainer'] = name
            if check_for_pokemon(pokemon, poke_list):
                if email != '':
                    if not quiet_time(config[name]):
                        send_notification(pokemon, email, fromemail)


def check_for_pokemon(pokemon, poke_list):
    if pokemon['pokemon_name'] in poke_list:
        return pokemon not in SENT_ALERTS
    else:
        return False


def quiet_time(config):
    start = config['quiet_start']
    end = config['quiet_end']
    nowhour = datetime.now().hour
    logging.info('{0} -- {1} -- {2}'.format(start, nowhour, end))
    return nowhour >= start and nowhour < end


def send_notification(pokemon, email, fromaddr):
    datestr = datetime.fromtimestamp(pokemon['disappear_time'] / 1000).strftime("%H:%M:%S")
    with open('{0}/gmailcreds.json'.format(CUR_DIR), 'r') as f:
        gmailcreds = json.load(f)

    logging.info('Sending alert to {0}'.format(email))
    msg = "\r\n".join([
        "From: {0}".format(fromaddr),
        "To: {0}".format(email),
        "Subject: A {0} has been spotted!".format(pokemon['pokemon_name']),
        "",
        "{0} Disapears at {1}. https://www.google.com/maps/dir/Current+Location/{2},{3}".format(pokemon['pokemon_name'], datestr, pokemon['latitude'], pokemon['longitude'])
        ])
    server.starttls()
    server.login(fromaddr, gmailcreds['password'])
    server.sendmail(fromaddr, email, msg)
    server.quit()
    SENT_ALERTS.append(pokemon)

if __name__ == '__main__':
    logging.info('Starting PokemonGo-Map-Notify')
    while 1:
        try:
            main()
            sleep(15)
        except:
            logging.error('Error running app.', exc_info=True)
            sleep(45)
            pass
