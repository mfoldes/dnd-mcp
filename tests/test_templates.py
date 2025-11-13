#!/usr/bin/env python3
"""Unit tests for the template formatting helpers."""

import unittest
from unittest.mock import patch

from src.templates import (
    format_dnd_data,
    format_search_results,
)


SAMPLE_MONSTER = {
    "name": "Adult Red Dragon",
    "size": "Huge",
    "type": "dragon",
    "alignment": "chaotic evil",
    "armor_class": 19,
    "hit_points": 256,
    "hit_dice": "19d12",
    "speed": {"walk": 40, "fly": 80},
    "strength": 27,
    "dexterity": 10,
    "constitution": 25,
    "intelligence": 16,
    "wisdom": 13,
    "charisma": 21,
    "challenge_rating": 17,
    "proficiencies": [
        {
            "proficiency": {"index": "saving-throw-str", "name": "Saving Throw: STR"},
            "value": 9,
        },
        {
            "proficiency": {"index": "skill-perception", "name": "Skill: Perception"},
            "value": 8,
        },
    ],
    "senses": {"darkvision": "120 ft."},
    "languages": "Common, Draconic",
    "special_abilities": [
        {"name": "Legendary Resistance", "desc": "If the dragon fails a saving throw, it can choose to succeed instead."}
    ],
    "actions": [
        {"name": "Multiattack", "desc": "The dragon makes three attacks: one with its bite and two with its claws."}
    ],
    "legendary_desc": "The dragon can take 3 legendary actions, choosing from the options below.",
    "legendary_actions": [
        {"name": "Detect", "desc": "The dragon makes a Wisdom (Perception) check."}
    ],
}


SAMPLE_SPELL = {
    "name": "Fireball",
    "level": 3,
    "school": {"name": "Evocation"},
    "casting_time": "1 action",
    "range": "150 feet",
    "components": ["V", "S", "M"],
    "material": "A tiny ball of bat guano and sulfur.",
    "duration": "Instantaneous",
    "concentration": False,
    "desc": [
        "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame.",
    ],
    "higher_level": [
        "The fire deals an extra 1d6 damage for each slot level above 3rd.",
    ],
    "classes": [
        {"name": "Wizard"},
        {"name": "Sorcerer"},
    ],
}


SAMPLE_EQUIPMENT = {
    "name": "Plate Armor",
    "equipment_category": {"name": "Armor"},
    "armor_category": "Heavy",
    "cost": {"quantity": 1500, "unit": "gp"},
    "weight": 65,
    "armor_class": {"base": 18, "dex_bonus": False},
    "str_minimum": 15,
    "stealth_disadvantage": True,
    "desc": ["Plate consists of shaped, interlocking metal plates to cover the entire body."],
}


MOCK_RESULTS = {
    "query": "dragon",
    "results": {
        "monsters": {
            "items": [
                {
                    "name": "Adult Red Dragon",
                    "desc": "A massive fire-breathing dragon with crimson scales.",
                },
                {
                    "name": "Young Black Dragon",
                    "desc": "A sleek acid-spitting dragon with ebony scales.",
                },
            ]
        },
        "spells": {
            "items": [
                {
                    "name": "Dragon's Breath",
                    "desc": "You imbue a creature with the power to exhale destructive energy.",
                }
            ]
        },
    },
    "total_count": 3,
    "formatted_attribution": (
        "\n\n---\n\n**Source Information:**\n\n* **Source:** D&D 5e API\n* **Confidence:** High\n"
    ),
}


class TestTemplates(unittest.TestCase):
    """Validate that templates render expected markdown snippets."""

    def test_monster_template_includes_core_sections(self) -> None:
        rendered = format_dnd_data(SAMPLE_MONSTER, "monster")
        self.assertIn("# Adult Red Dragon", rendered)
        self.assertIn("**Challenge:** 17", rendered)
        self.assertIn("## Actions", rendered)

    def test_spell_template_formats_components(self) -> None:
        rendered = format_dnd_data(SAMPLE_SPELL, "spell")
        self.assertIn("# Fireball", rendered)
        self.assertIn("**Components:** V, S, M", rendered)
        self.assertIn("**Classes:** Wizard, Sorcerer", rendered)

    def test_equipment_template_describes_armor(self) -> None:
        rendered = format_dnd_data(SAMPLE_EQUIPMENT, "equipment")
        self.assertIn("# Plate Armor", rendered)
        self.assertIn("**Cost:** 1500 gp", rendered)
        self.assertIn("**Armor Class:** 18", rendered)

    def test_search_results_template_summarizes_items(self) -> None:
        rendered = format_search_results(MOCK_RESULTS)
        self.assertIn("Search Results for \"dragon\"", rendered)
        self.assertIn("Adult Red Dragon", rendered)
        self.assertIn("**Source:** D&D 5e API", rendered)

    @patch("src.templates.formatter.TEMPLATES_ENABLED", new=False)
    def test_plain_formatting_when_templates_disabled(self) -> None:
        rendered = format_dnd_data(SAMPLE_MONSTER, "monster")
        header = rendered.splitlines()[0]
        self.assertEqual(header, "Adult Red Dragon")
        self.assertNotIn("#", header)


if __name__ == "__main__":
    unittest.main()
