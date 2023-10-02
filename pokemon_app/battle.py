"""Pokemon Battle Simulator

This module simulates a battle between two pokenon, given their names
It uses flask to create a local server and routes localhost:5000/battle and localhost:5000/show_previous_battles
It save all battle logs to a mysql database

Functions:
    battle: routes localhost:5000/battle
    show_previous_battles
    store_battle_to_db

"""

from flask import Flask, request, jsonify
import mysql.connector
import copy
import json
from pokemon import Pokemon, connection_error, http_error

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    "host": "mysql_db",  # Docker container name for mysql
    "user": "battle_user",
    "password": "battle_password",
    "database": "battle_db",
}

@app.route('/battle')
def battle():
    """Simulates the battle between two pokemon.
    
    routes localhost:5000/battle?<pokemon1>&<pokemon2>
    Pokemon attack in sequence. A pokemon wins if the other pokemon's hitpoint reach 0.
    After 6 turns (3 attacks from each pokemon) if no pokemon has reach 0 hitpoint, 
    the pokemon with highest remaining hitpoints wins.

    Parameters:
        - pokemon1: Name of the first Pokemon
        in: path
        type:str
        required:true
        - pokemon2: Name of the second Pokemon
        in: path
        type:str
        required:true

    Responses:
        200: Returns a json with the battle logs and the winner
        400: Returns a json with bad request
        404: Return a json being unable to find the pokemon in pokeapi
    """

    try:
        # Get Pokemon names from URL parameters
        pokemon1_name = request.args.get('pokemon1')
        pokemon2_name = request.args.get('pokemon2')

        #Check if any of the pokemon names are None
        if not pokemon1_name or not pokemon2_name:
            raise ValueError("/battle requires two pokemon names")

        # Create Pokemon instances
        pokemon1 = Pokemon(pokemon1_name)
        pokemon2 = Pokemon(pokemon2_name)

        # Create a non memory shared instance if the two pokemons are the same
        if pokemon1_name == pokemon2_name:
            pokemon2 = copy.deepcopy(pokemon1)
            pokemon2.name = f'{pokemon2.name}2'

    except ValueError as e:
        return jsonify({"Error": str(e)}) , 400
    except (connection_error, http_error) as e:
        return jsonify({"Error": str(e)}), 404

    # Perform battle simulation
    battle_log = []
    attacker, defender = Pokemon.select_attacker_defender(pokemon1, pokemon2)
    attacker.current_hp = attacker.stats['hp']
    defender.current_hp = defender.stats['hp']
    for turn in range(6):
        attack_info = attacker.attack(defender)
        battle_log.append(attack_info)

        if defender.current_hp <= 0:
            winner = attacker.name
            break

        attacker, defender = defender, attacker # switch attacker and defender

    # If no pokemon won after 6 turns, check pokemon with highest hp wins
    if pokemon1.current_hp > pokemon2.current_hp:
        winner = f'{pokemon1.name} is the winner by having the highest remaining hp after 6 turns'
    elif pokemon2.current_hp > pokemon1.current_hp:
        winner = f'{pokemon2.name} is the winner by having the highest remaining hp after 6 turns'
    else:
        winner= "It's a draw"

    store_battle_to_db(winner, battle_log)

    battle_result = {
        "pokemon1": Pokemon.get_pokemon_info(pokemon1),
        "pokemon2": Pokemon.get_pokemon_info(pokemon2),
        "winner": winner,
        "battle_log": battle_log
    }

    # Return battle result as JSON response
    return jsonify(battle_result)

@app.route('/show_previous_battles')
def show_previous_battles():
    """Access mysql database and shows all previous battles

    Returns:
        json: A json with all the database logs
    """
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch data from the database
        cursor.execute("SELECT * FROM battles")
        data = cursor.fetchall()

        # Close the database connection
        cursor.close()
        conn.close()

        # Render the HTML template and pass the data
        return jsonify(data)

    except Exception as e:
        return f"An error occurred: {str(e)}"

def store_battle_to_db(winner, battle_log):
    """Stores battle logs to mysql database

    Args:
        winner (str): name of the pokemon that won the battle
        battle_log (dict): battle log with all attacks made during the battle
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Assuming you have a table named "battles"
        cursor.execute(
            "INSERT INTO battles (winner, battle_log) VALUES (%s, %s)",
            (winner, json.dumps(battle_log)),
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        raise ValueError("Could not store in database") from e

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)