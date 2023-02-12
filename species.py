"""
Species define what a creature is physically and how it acts. These are concrete implementations used to create
Creature objects (Humanoid or Animal).
"""
# TODO: Flavor terrain rare creatures?
import console
import game_objects as go
import items
import config
from utils import make_stats
from knowledge import knowledge

# The species define what a creature is physically and how it looks in the game
# This also includes the "equipment" of animal species which is part of the body


human_race = go.HumanoidSpecies(name=config.Human,
                                icon='H',
                                color=config.order_color,
                                description=knowledge[config.Human][0],
                                sort_key=0,
                                base_effect_modifiers={config.travel_energy_loss_modifier: 0},
                                fist_weapon=items.Fist,
                                clothes=items.Clothes)
dwarf_race = go.HumanoidSpecies(name=config.Dwarf,
                                icon='D',
                                color=config.order_color,
                                description=knowledge[config.Dwarf][0],
                                sort_key=1,
                                base_effect_modifiers={config.drunk_effect: -20, config.heavy_armor_skill: 1.5},
                                fist_weapon=items.Fist,
                                clothes=items.Clothes)
gnome_race = go.HumanoidSpecies(name=config.Gnome,
                                icon='G',
                                color=config.order_color,
                                description=knowledge[config.Gnome][0],
                                sort_key=2,
                                fist_weapon=items.Fist,
                                clothes=items.Clothes)
elf_race = go.HumanoidSpecies(name=config.Elf,
                              icon='E',
                              color=config.order_color,
                              description=knowledge[config.Elf][0],
                              sort_key=3,
                              base_effect_modifiers={config.max_mana_modifier: 1.2},
                              fist_weapon=items.Fist,
                              clothes=items.Clothes)
orc_race = go.HumanoidSpecies(name=config.Orc,
                              icon='O',
                              color=config.chaos_color,
                              description=knowledge[config.Orc][0],
                              sort_key=4,
                              base_effect_modifiers={config.sick_effect: -20},
                              fist_weapon=items.Fist,
                              clothes=items.Clothes)
troll_race = go.HumanoidSpecies(name=config.Troll,
                                icon='T',
                                color=config.chaos_color,
                                description=knowledge[config.Troll][0],
                                sort_key=5, consumable_types=[items.Rock],
                                base_effect_modifiers={config.max_hp_modifier: 1.2,
                                                       config.hunger_rock_effect: 10,
                                                       config.thirst_rock_effect: 10
                                                       },
                                fist_weapon=items.TrollFist,
                                clothes=items.Clothes)
goblin_race = go.HumanoidSpecies(name=config.Goblin,
                                 icon='G',
                                 color=config.chaos_color,
                                 description=knowledge[config.Goblin][0],
                                 sort_key=6, base_effect_modifiers={config.max_load_modifier: 1.2,
                                                                    config.scavenging_skill: 1.3},
                                 fist_weapon=items.Fist,
                                 clothes=items.Clothes)
kraken_race = go.HumanoidSpecies(name=config.Kraken,
                                 icon='K',
                                 color=config.chaos_color,
                                 description=knowledge[config.Kraken][0],
                                 sort_key=7,
                                 fist_weapon=items.Fist,
                                 clothes=items.Clothes)
imp_race = go.HumanoidSpecies(name=config.Imp,
                              icon='I',
                              color=config.chaos_color,
                              description=knowledge[config.Imp][0],
                              sort_key=8,
                              fist_weapon=items.Fist,
                              clothes=items.Clothes)
dryad_race = go.HumanoidSpecies(name=config.Dryad,
                                icon='D',
                                color=config.nature_color,
                                description=knowledge[config.Dryad][0],
                                sort_key=9,
                                fist_weapon=items.Fist,
                                clothes=items.Clothes)
shifter_race = go.HumanoidSpecies(name=config.Shifter,
                                  icon='S',
                                  color=config.nature_color,
                                  description=knowledge[config.Shifter][0],
                                  sort_key=10,
                                  active_effects={config.non_rest_hp_regen_effect: 1},
                                  fist_weapon=items.Fist,
                                  clothes=items.Clothes)
water_elemental_race = go.HumanoidSpecies(name=config.WaterElemental,
                                          icon='W',
                                          color=config.nature_color,
                                          description=knowledge[config.WaterElemental][0],
                                          sort_key=11,
                                          base_effect_modifiers={config.hunger_water_effect: 20},
                                          fist_weapon=items.Fist,
                                          clothes=items.Clothes)
fae_race = go.HumanoidSpecies(name=config.Fae,
                              icon='F',
                              color=config.nature_color,
                              description=knowledge[config.Fae][0],
                              sort_key=12,
                              base_effect_modifiers={config.hunger_meat_effect: -20},
                              fist_weapon=items.Fist,
                              clothes=items.Clothes)
field_mouse_species = go.AnimalSpecies(name='field mouse', icon='m', color=config.brown_fg_color,
                                       description='A field mouse.')
rat_species = go.AnimalSpecies(name='rat', icon='r', color=console.fg.lightblack,
                               description='A big rat.', equipment=[items.RawMeat])
snow_hare_species = go.AnimalSpecies(name='snow hare', icon='h', color=console.fg.lightwhite,
                                     description='A snow hare.', equipment=[items.RawMeat])
ash_beetle_species = go.AnimalSpecies(name='ash beetle', icon='b', color=console.fg.lightblack,
                                      description='An ash beetle')
ice_mantis_species = go.AnimalSpecies(name='ice mantis', icon='m', color=console.fg.blue,
                                      description='An ice mantis.')
sand_snake_species = go.AnimalSpecies(name='sand snake', icon='s', color=console.fg.yellow,
                                      description='A desert snake', equipment=[items.RawMeat])
scorpion_species = go.AnimalSpecies(name='scorpion', icon='s', color=console.fg.lightblack,
                                    description='A black scorpion')
fox_species = go.AnimalSpecies(name='fox', icon='f', color=console.fg.lightred,
                               description='A fox.',
                               equipment=[items.RawMeat, items.SmallTeeth, items.LightHide])
jaguar_species = go.AnimalSpecies(name='jaguar', icon='j', color=console.fg.lightyellow,
                                  description='A jaguar.',
                                  base_stats=make_stats(8, {config.Str: 5, config.End: 6, config.Wil: 1}),
                                  equipment=[items.RawMeat, items.MediumTeeth, items.LightHide],
                                  initial_disposition=config.aggressive_disposition)
wolf_species = go.AnimalSpecies(name='wolf', icon='w', color=console.fg.lightblack,
                                description='A wolf.',
                                base_stats=make_stats(4, {config.Dex: 7, config.Per: 8, config.Wil: 1}),
                                equipment=[items.RawMeat, items.MediumTeeth, items.LightHide],
                                initial_disposition=config.aggressive_disposition)
winter_wolf_species = go.AnimalSpecies(name='winter wolf', icon='w', color=console.fg.white,
                                       description='A white wolf.',
                                       base_stats=make_stats(4, {config.Dex: 7, config.Per: 8, config.Wil: 1}),
                                       equipment=[items.RawMeat, items.MediumTeeth, items.LightHide],
                                       initial_disposition=config.aggressive_disposition)
ice_bear_species = go.AnimalSpecies(name='ice bear', icon='b', color=console.fg.lightblue,
                                    description='A polar bear!',
                                    base_stats=make_stats(10, {config.Dex: 3, config.Per: 5, config.Wil: 1}),
                                    equipment=[items.RawMeat, items.LargeClaws, items.MediumHide],
                                    initial_disposition=config.aggressive_disposition)
bear_species = go.AnimalSpecies(name='bear', icon='b', color=config.brown_fg_color,
                                description='A big bear!',
                                base_stats=make_stats(10, {config.Dex: 3, config.Per: 5, config.Wil: 1}),
                                equipment=[items.RawMeat, items.LargeClaws, items.MediumHide],
                                initial_disposition=config.aggressive_disposition)
swamp_dragon_species = go.AnimalSpecies(name='swamp dragon', icon='d', color=console.fg.lightgreen,
                                        description='A swamp dragon!',
                                        base_stats=make_stats(10, {config.Dex: 5, config.Per: 6, config.Wil: 1}),
                                        equipment=[items.RawMeat, items.LargeTeeth, items.MediumScales],
                                        initial_disposition=config.aggressive_disposition)
crocodile_species = go.AnimalSpecies(name='crocodile', icon='c', color=console.fg.lightgreen,
                                     description='A big crocodile!',
                                     base_stats=make_stats(6, {config.Dex: 4, config.Per: 4, config.Wil: 1}),
                                     equipment=[items.RawMeat, items.LargeTeeth, items.MediumScales],
                                     initial_disposition=config.aggressive_disposition)
monkey_species = go.AnimalSpecies(name='monkey', icon='m', color=console.fg.lightred,
                                  description='A monkey.',
                                  equipment=[items.RawMeat, items.SmallTeeth, items.LightHide])
ice_fox_species = go.AnimalSpecies(name='ice fox', icon='f', color=console.fg.blue,
                                   description='An ice fox.',
                                   equipment=[items.RawMeat, items.SmallTeeth, items.LightHide])
eagle_species = go.AnimalSpecies(name='eagle', icon='e', color=config.brown_fg_color,
                                 description='An eagle.',
                                 base_stats=make_stats(4, {config.Dex: 3, config.Per: 15, config.Wil: 1}),
                                 equipment=[items.RawMeat, items.MediumClaws, items.Feathers],
                                 initial_disposition=config.aggressive_disposition)
hydra_species = go.AnimalSpecies(name='hydra', icon='H', color=console.fg.lightgreen,
                                 description='A giant hydra!',
                                 base_stats=make_stats(stats={config.Dex: 15, config.Per: 16, config.Wil: 15,
                                                              config.Str: 18, config.End: 14}),
                                 equipment=[items.RawMeat, items.HugeClaws, items.HeavyScales],
                                 initial_disposition=config.aggressive_disposition)
