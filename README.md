# Pokemon_battle
This Python applicatication simulates a battle between two Pokemon using a formula basen on Generation 1 and takes into consideration
the type advantage of each attack against the types of the enemy pokemon. The battle has 6 turns meaning each pokemon attacks 3 times
If no Pokemon hp has reached 0 then the Pokemon with the highest remaining hp wins. 

## Technologies used:
  - Requests to [PokeAPI](https://pokeapi.co/) to gather information for each Pokemon
  - Cache memory to store each Pokemon's info so the application will not make unnecessary API calls for the same Pokemons
  - Flask to set up a local server which allows the user to communicate with the application via routing
  - MySQL database to store the battle logs
  - Docker for dockerization of the MySQL database and main Python application in seperate containers

## How to run:

### Requirments:
  - [Docker](https://www.docker.com/) should be installed
  
  From inside the directory where the docker-compose.yaml is run the command:
  ```shell
  docker-compose up
  ```
  This will use the docker-compose.yml file and take instruction to set up a container battle_app main application and the MySQL database.
  When you see that both pokemon_app and mysql_db containers are running you can open a browser window and access them with the following URLs:
  #### Make Pokemon battle
  
    http://localhost:5000/battle?pokemon1=<pokemon_name_1>&pokemon2=<pokemon_name_2> 
    
  Where <pokemon_name_1> is the name of the first pokemon and <pokemon_name_2> is the name of the second pokemon
  After entering the URL, a json response should appear displaying the winner, the battle log with each attack and both Pokemon IDs containing
  their name, stats and types

  #### Show previous battle logs from database

    http://localhost:5000/[get_previous_battles](http://localhost:5000/show_previous_battles)

  This returns all previous winners and battle logs that where stored in the database. Note that after shutting the db container all entries are deleted

  To shut down the containers use the command:

    docker-compose down

  This will only delete the deocker containers. If you want to delete the volumes as well use the '-v' argument.
  To delete the docker images use the '--rmi all' argument
