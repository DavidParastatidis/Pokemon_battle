"""Unnitest for pokemon.py

Functions:
    setUp: unnitest method called before each test
    test_fetch_data: unittest for fetch_data
    test_parse_data: unittest for parse_data
    test_parse_moves: unittest for parse_moves
    test_select_attacker_defender: unittest for select_attacker_defender
    test_attack: unittest for attack
    test_get_damage_multiplier_by_type: unittest for get_damage_multiplier_by_type
    test_get_pokemon_info: unittest for get_pokemon_info
"""

import unittest
from pokemon import Pokemon

class TestPokemon(unittest.TestCase):
    def setUp(self):
        self.Electrode = Pokemon("Electrode")
        self.Diglett = Pokemon("Diglett")

    def test_fetch_data(self):
        self.Electrode.fetch_data()
        self.assertEqual(len(self.Electrode.types), 1)
        self.assertEqual(len(self.Electrode.stats), 8)
        self.assertEqual(self.Electrode.current_hp, 0)

    def test_parse_data(self):
        data = {
            'height': 12,
            'weight': 666,
            'types': [{'type': {'name': 'electric'}}],
            'stats': [
                {'stat': {'name': 'hp'}, 'base_stat': 60},
                {'stat': {'name': 'attack'}, 'base_stat': 50},
                {'stat': {'name': 'defense'}, 'base_stat': 70},
                {'stat': {'name': 'special-attack'}, 'base_stat': 80},
                {'stat': {'name': 'special-defense'}, 'base_stat': 80},
                {'stat': {'name': 'speed'}, 'base_stat': 150}],
            'moves': [
                {'move': {'name': 'headbutt', 'url': 'https://pokeapi.co/api/v2/move/29/'}},
                {'move': {'name': 'tackle', 'url': 'https://pokeapi.co/api/v2/move/33/'}},
                {'move': {'name': 'take-down', 'url': 'https://pokeapi.co/api/v2/move/36/'}},
                {'move': {'name': 'hyper-beam', 'url': 'https://pokeapi.co/api/v2/move/63/'}}]
        }
        self.Electrode.parse_data(data)
        self.assertEqual(self.Electrode.stats['Height'], 1.2)
        self.assertEqual(self.Electrode.stats['Weight'], 66.6)
        self.assertEqual(self.Electrode.stats['hp'], 60)
        self.assertEqual(self.Electrode.stats['attack'], 50)
        self.assertEqual(self.Electrode.stats['defense'], 70)
        self.assertEqual(self.Electrode.stats['special-attack'], 80)
        self.assertEqual(self.Electrode.stats['special-defense'], 80)
        self.assertEqual(self.Electrode.stats['speed'], 150)
        self.assertEqual(self.Electrode.types, ['electric'])

    def test_parse_moves(self):
        data = [{"move": {"name": "headbutt", "url": "https://pokeapi.co/api/v2/move/29/"}},
                {"move": {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/33/"}},
                {"move": {"name": "sonic-boom", "url": "https://pokeapi.co/api/v2/move/49/"}},
                {"move": {"name": "hyper-beam", "url": "https://pokeapi.co/api/v2/move/63/"}},
                {"move": {"name": "thunderbolt","url": "https://pokeapi.co/api/v2/move/85/"}},
                {"move": {"name": "take-down","url": "https://pokeapi.co/api/v2/move/36/"}}]
        self.Electrode.parse_moves(data)

        expected_result = {'headbutt': {'damage_class': {'name': 'physical', 'url': 'https://pokeapi.co/api/v2/move-damage-class/2/'}, 'type': {'name': 'normal', 'url': 'https://pokeapi.co/api/v2/type/1/'}, 'power': 70},
                  'tackle': {'damage_class': {'name': 'physical', 'url': 'https://pokeapi.co/api/v2/move-damage-class/2/'}, 'type': {'name': 'normal', 'url': 'https://pokeapi.co/api/v2/type/1/'}, 'power': 40}, 
                  'take-down': {'damage_class': {'name': 'physical', 'url': 'https://pokeapi.co/api/v2/move-damage-class/2/'}, 'type': {'name': 'normal', 'url': 'https://pokeapi.co/api/v2/type/1/'}, 'power': 90}, 
                  'hyper-beam': {'damage_class': {'name': 'special', 'url': 'https://pokeapi.co/api/v2/move-damage-class/3/'}, 'type': {'name': 'normal', 'url': 'https://pokeapi.co/api/v2/type/1/'}, 'power': 150}}

        self.assertEqual(self.Electrode.moves, expected_result)

    def test_select_attacker_defender(self):
        # Test when self (pokemon1) has higher speed
        attacker, defender = self.Electrode.select_attacker_defender(self.Diglett)
        # Check if attacker is pokemon1 and defender is pokemon2
        self.assertEqual(attacker, self.Electrode)
        self.assertEqual(defender, self.Diglett)

        # Test when pokemon2 has higher speed
        self.Electrode.stats['speed'] = 10
        attacker, defender = self.Electrode.select_attacker_defender(self.Diglett)

        # Check if attacker is pokemon2 and defender is pokemon1
        self.assertEqual(attacker, self.Diglett)
        self.assertEqual(defender, self.Electrode)

        # Test when both Pokemon have equal speed
        self.Electrode.stats['speed'] = 95
        attacker, defender = self.Electrode.select_attacker_defender(self.Diglett)
        # Check if attacker and defender are randomly chosen from pokemon1 and pokemon2
        self.assertTrue(attacker in [self.Electrode, self.Diglett])
        self.assertTrue(defender in [self.Electrode, self.Diglett])

    def test_attack(self):
        self.Electrode.moves = {'headbutt': {'damage_class': {'name': 'physical', 'url': 'https://pokeapi.co/api/v2/move-damage-class/2/'}, 'type': {'name': 'normal', 'url': 'https://pokeapi.co/api/v2/type/1/'}, 'power': 70}}
        self.Electrode.stats['attack'] = 50

        self.Diglett.stats['defense'] = 20
        self.Diglett.current_hp = 10

        self.Electrode.attack(self.Diglett)
        self.assertAlmostEqual(self.Diglett.current_hp, 0, delta=1)

    def test_get_pokemon_info(self):
        excpected_outcome = {
            "name":"Electrode",
            'types':["electric"],
            "stats":{'Height': 1.2, 'Weight': 66.6, 'hp': 60, 'attack': 50, 'defense': 70, 'special-attack': 80, 'special-defense': 80, 'speed': 150},
        }
        self.assertEqual(self.Electrode.get_pokemon_info(), excpected_outcome)

if __name__ == "__main__":
    unittest.main()
    