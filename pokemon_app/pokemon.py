"""Pokemon Class

This module simulates a pokkemoon
Tt retrives their data from PokeAPI. 
It calculates the damage of each attack damage based on a version of the Generation 1 formula
It uses cache memory to load pokemon that were search before in order to reduce the API call

Classes:
    Pokemon: A class representing a pokemon with its attributes

Functions:
    fetch_data: Fetched pokemon data from pokeapi given a pokemon name
    parse_data: parses data and fills the pokemoon class attributes
    parse_moves: parse pokemon moves and retains 4 that do damage
    select_attacker_defender: decides who attacks and who defends based on speed
    attack: simulates a pokemon attack to another pokemon
    get_damage_multiplier_by_type: calculates the damage multiplier based on pokemon types
    get_pokemon_info: returns pokemon info
"""

import random
from functools import lru_cache
import requests

class connection_error(Exception):
    """Class handling connection errors when fetching data from pokepi. pass the error to flask

    Args:
        Exception (str): Error description
    """

class http_error(Exception):
    """Class handling http errors when fetching data from pokepi. pass the error to flask

    Args:
        Exception (str): Error description
    """

@lru_cache(maxsize=100)
class Pokemon:
    """A class representing a pokemon with its attributes

    Atribues:
        name(str): name of the pokemon
        type(list<str>): list with the types of the pokemon
        stats(dict): dictionary with pokemon's info
        moves(dict): dictionary with pokemon's moves
        current_hp(int): pokemon's current hitpoints

    Functions:
        fetch_data()
        parse_data(dict)
        parse_moves(dict)
        attack(object)
        attack_type_advantage(str) -> int
        display_stats()
    """

    def __init__(self, name):
        self.name = name
        self.types = []
        self.stats = {}
        self.moves = {}
        self.current_hp = 0
        self.fetch_data()

    def fetch_data(self):
        """Fetches data from PokeAPI given a pokemon name"""

        try:
            url = f"https://pokeapi.co/api/v2/pokemon/{self.name.lower()}"
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for HTTP errors

            data = response.json()
            #Check if no data were returned
            self.parse_data(data)

        except requests.exceptions.ConnectionError as e:
            raise connection_error(f'Connection error when requesting data for pokemon {self.name}: {e}') from e
        except requests.exceptions.HTTPError as e:
            raise http_error(f'Pokemon {self.name} was not found. Probably the name is written incorectly') from e


    def parse_data(self, data):
        """Parses pokemon information to pokemon instance

        Args:
            data (dict): dictionary with pokemon information
        """

        self.stats['Height'] = data['height'] / 10.0
        self.stats['Weight'] = data['weight'] / 10.0
        # Get all element tupes
        self.types= [
            type['type']['name']
            for type in data['types']
        ]
        #Get hitpoints, attack, defense, special-attack, special-defense and speed
        for stat in data['stats']:
            name = stat['stat']['name']
            value = stat['base_stat']
            self.stats[name] = value
        self.parse_moves(data['moves'])

    def parse_moves(self, moves_dictionary):
        """Parses the moves dictionary to find moves with attacking power

        It finds the first 4 moves with power to fill pokemon moves
        If a pokemon has no attacking moves it takes the move struggle


        Args:
            moves_dictionary (dict): dictionary with all pokemon's available moves
        """

        for move in moves_dictionary:
            move_name = move['move']['name']
            move_url = move['move']['url']
            try:
                response = requests.get(move_url)
                response.raise_for_status() # Raise an exception for HTTP errors
                move_info = response.json()

                if move_info['power'] is not None and  move_info['power']> 0:
                    self.moves[move_name] = {
                        'damage_class': move_info['damage_class'],
                        'type': move_info['type'],
                        'power': move_info['power'],
                    }
                    if len(self.moves) == 4:
                        break  # Stop fetching moves after finding four

            except requests.exceptions.ConnectionError as e:
                raise connection_error(f'Connection error when searching for pokemon moves: {e}') from e
            except requests.exceptions.HTTPError as e:
                raise http_error(f'HTTP error when searching for pokemon moves: {e}') from e

        if len(self.moves) == 0:
            self.moves['struggle'] = {
                'damage_class': {
                    'name': "physical",
                    'url': "https://pokeapi.co/api/v2/move-damage-class/2/"
                },
                'type': {
                    'name': "normal",
                    'url': "https://pokeapi.co/api/v2/type/1/"
                },
                'power': 50
            }

    def select_attacker_defender(self, pokemon2):
        """Decides who is the attacker and who is the defender between two pokemon based on their speed

        Args:
            self (Pokemon): The first Pokemon
            pokemon2 (Pokemon): The Second Pokemon

        Returns:
            tuple: A tuple with the attacker and defender
        """

        if self.stats['speed'] > pokemon2.stats['speed']:
            attacker = self
            defender = pokemon2
        elif self.stats['speed'] < pokemon2.stats['speed']:
            attacker = pokemon2
            defender = self
        else:
            # If speeds are equal, randomly select the attacker
            attacker, defender = random.choice([(self, pokemon2), (pokemon2, self)])
        return attacker, defender

    def attack(self, defender):
        """Simulates an attack of pokemon to another. 
        
        The damage of the attack is calculated based on simplified formula from generation 1
        The damage calculation takes into account the type advantages
        The defending pokemon loses hitpoint based on the calculated damage

        Args:
            defender (Pokemon): the pokemon defending the attack

        Returns:
            str: Description with damage done to the defending pokemon and its remaining hitpoints
        """

        move_name = random.choice(list(self.moves.keys()))
        move = self.moves[move_name]

        # Calculate damage using Generation 1 formula
        LEVEL = 1
        CRITICAL = 1
        damage = ((2 * LEVEL * CRITICAL) / 5) + 2 # assuming pokemon are level 1 and no critical
        damage *= move['power'] * (self.stats['attack'] / defender.stats['defense']) / 50
        damage += 2
        damage *= random.uniform(0.85, 1.00)  # Apply random damage variation

        # Check for type advantage
        type_advantage_modifier = self.get_damage_multiplier_by_type(move['type']['url'], defender)
        damage =  round(damage * type_advantage_modifier)

        # Subtract damage from defender's hitpoint
        defender.current_hp -= int(damage)

        attack_info = f"{self.name} attacks {defender.name} with {move_name}. It does {damage} damage and {defender.name} has {defender.current_hp} hitpoints remaining"
        return attack_info

    def get_damage_multiplier_by_type(self, move_type_url, defender):
        """Calculates if an attack has type advantage over defending pokemon types

        Args:
            move_type_url (str): url pointing to move type advantages over other pokemon types
            defender (Pokemon): Pokemon defending the attack

        Returns:
            int: damage multiplier
        """

        try:
            response = requests.get(move_type_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            move_type_data = response.json()
            type_advantage = 1.0

            for defender_type in defender.types:
                if defender_type in move_type_data['damage_relations']['double_damage_to']:
                    type_advantage *= 2.0
                elif defender_type in move_type_data['damage_relations']['half_damage_to']:
                    type_advantage *= 0.5
                elif defender_type in move_type_data['damage_relations']['no_damage_to']:
                    type_advantage *= 0.0
            return type_advantage

        except requests.exceptions.ConnectionError as e:
            raise connection_error(f'HTTP error when searching for damage multiplier by type: {e}') from e
        except requests.exceptions.HTTPError as e:
            raise http_error(f'HTTP error when searching for damage multiplier by type: {e}') from e

    def get_pokemon_info(self):
        """Creates a pokemon ID with the pokemon information

        Args:
            pokemon (Pokemon): Pokemon instance

        Returns:
            dict: dict with pokemon info
        """
        pokemon_info = {
            "name":self.name,
            'types':self.types,
            "stats":self.stats,
        }
        return pokemon_info
