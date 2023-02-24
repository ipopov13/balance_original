"""
Concrete Item objects
"""
import game_objects as go
import config
import commands
import random
import console


class JunkItem(go.Item):
    def __init__(self):
        name = 'some junk'
        weight = random.randint(1, 4)
        icon = random.choice('*{}()[]|,')
        description = 'an unidentifiable piece of junk'
        color = random.choice([console.fg.purple, console.fg.red, console.fg.yellow, console.fg.blue])
        super().__init__(name=name, weight=weight, icon=icon, description=description, color=color)


class WaterSkin(go.LiquidContainer):
    def __init__(self):
        super().__init__(name="an empty waterskin/skin of {}", max_volume=2, weight=1, icon=',',
                         color=config.brown_fg_color)


class Clothes(go.Armor):
    def __init__(self):
        super().__init__(name='simple clothes', weight=0, icon='.', color=console.fg.lightblack,
                         description="Commoner's shirt and pants.",
                         armor_skill=config.light_armor_skill, armor_stat=config.Dex, combat_exhaustion=0)


class HideArmor(go.Armor):
    def __init__(self):
        super().__init__(name='hide armor', weight=5, icon='(', color=config.brown_fg_color,
                         description='Armor made from light hide',
                         effects={config.resistances_and_affinities: {config.physical_damage: -1}},
                         armor_skill=config.light_armor_skill, armor_stat=config.Dex, combat_exhaustion=1)


class LeatherArmor(go.Armor):
    def __init__(self):
        super().__init__(name='leather armor', weight=6, icon='(', color=config.brown_fg_color,
                         description='Armor made from leather',
                         effects={config.resistances_and_affinities: {config.physical_damage: -3}},
                         armor_skill=config.light_armor_skill, armor_stat=config.Dex, combat_exhaustion=1)


class ChainMail(go.Armor):
    def __init__(self):
        super().__init__(name='chain mail', weight=9, icon='[', color=console.fg.lightblack,
                         description='A shirt of woven iron links.',
                         effects={config.resistances_and_affinities: {config.physical_damage: -5}},
                         armor_skill=config.heavy_armor_skill, armor_stat=config.End, combat_exhaustion=3)


class PlateArmor(go.Armor):
    def __init__(self):
        super().__init__(name='plate armor', weight=15, icon='[', color=console.fg.default,
                         description='Armor made from metal plates',
                         effects={config.resistances_and_affinities: {config.physical_damage: -7}},
                         armor_skill=config.heavy_armor_skill, armor_stat=config.End, combat_exhaustion=5)


class Bag(go.Back):
    def __init__(self):
        super().__init__(name='bag', weight=1, width=3, height=1, icon='=',
                         color=console.fg.default, description='A very small bag')


class SpikedBoots(go.Boots):
    # TODO: Add to items spreadsheet
    def __init__(self):
        super().__init__(name='spiked boots', weight=4, icon=']',
                         color=console.fg.default, description='Spiked boots for walking on slippery ice.',
                         effects={config.effect_modifiers: {config.ice_climbing_cost: 0.05,
                                                            config.ice_passage_cost: 0.5}})


class SnowShoes(go.Boots):
    # TODO: Add to items spreadsheet
    def __init__(self):
        super().__init__(name='snowshoes', weight=2, icon=')',
                         color=config.brown_fg_color, description='Wide wooden frames to keep you above the snow.',
                         effects={config.effect_modifiers: {config.snow_passage_cost: 0.5}})


class Fist(go.Tool, go.RangedWeapon):
    def __init__(self):
        super().__init__(name="Your fist", description="Useful when you don't have a sword at hand.",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, work_skill=config.scavenging_skill, work_stat=config.Per,
                         melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=1,
                         ranged_weapon_stat=config.Str, ranged_weapon_skill=config.grenades_skill,
                         ranged_weapon_type=config.hand_thrown_type, max_distance=5,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 1},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class TrollFist(go.Tool, go.RangedWeapon):
    def __init__(self):
        super().__init__(name="Your fist", description="You can break rocks for eating with it!",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, work_skill=config.mining_skill, work_stat=config.Str,
                         melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=1,
                         ranged_weapon_stat=config.Str, ranged_weapon_skill=config.grenades_skill,
                         ranged_weapon_type=config.hand_thrown_type, max_distance=8,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 4},
                                                          config.melee_combat: {config.physical_damage: 1}}})


class ImpFist(go.Tool, go.RangedWeapon):
    def __init__(self):
        super().__init__(name="Your fist", description="Joyful flames dance over your fingers",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, work_skill=config.scavenging_skill, work_stat=config.Per,
                         melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=1,
                         ranged_weapon_stat=config.Str, ranged_weapon_skill=config.grenades_skill,
                         ranged_weapon_type=config.hand_thrown_type, max_distance=5,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 1},
                                                          config.melee_combat: {config.fire_damage: 3,
                                                                                config.physical_damage: 0}},
                                  config.tool_tag: config.fire_lighter_tool})


class Pickaxe(go.Tool):
    def __init__(self):
        super().__init__(name="a pickaxe", description="Used to extract stone and ores",
                         weight=6, icon='/', color=console.fg.lightblack,
                         work_exhaustion=5, work_skill=config.mining_skill, work_stat=config.Str,
                         melee_weapon_skill=config.twohanded_axes_skill, combat_exhaustion=5,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 1}}})


class FlintAndSteel(go.Item):
    def __init__(self):
        super().__init__(name="flint and steel", description="Strike to light a fire",
                         weight=1, icon=';', color=console.fg.lightblack,
                         effects={config.tool_tag: config.fire_lighter_tool})


class LongSword(go.LargeWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='long sword', weight=5, icon='|', color=color,
                         description="The soldier's weapon of choice.",
                         melee_weapon_skill=config.onehanded_swords_skill, combat_exhaustion=4,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 5}}})


class Machete(go.LargeWeapon):
    # TODO: Add to items spreadsheet
    def __init__(self, color=console.fg.lightwhite):
        super().__init__(name='machete', weight=7, icon='|', color=color,
                         description="Passing through a thick jungle is easy with this heavy blade.",
                         melee_weapon_skill=config.onehanded_swords_skill, combat_exhaustion=6,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 4}},
                                  config.effect_modifiers: {config.plant_passage_cost: 0.1}})


class BattleAxe(go.LargeWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='battle axe', weight=5, icon='|', color=color,
                         description='Often considered barbaric, but also very effective.',
                         melee_weapon_skill=config.onehanded_axes_skill, combat_exhaustion=5,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 6}}})


class Morningstar(go.LargeWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='morningstar', weight=6, icon='|', color=color,
                         description='Metal handle and a wicked-looking ball with spikes.',
                         melee_weapon_skill=config.onehanded_hammers_skill, combat_exhaustion=6,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 6}}})


class Spear(go.LargeWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='spear', weight=5, icon='|', color=color,
                         description='A long pole with a sharp metal head.',
                         melee_weapon_skill=config.spear_skill, combat_exhaustion=4,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 4}}})


class IcePick(go.SmallWeapon):
    # TODO: Add to items spreadsheet
    def __init__(self, color=console.fg.default):
        super().__init__(name='ice pick', weight=3, icon='|', color=color,
                         description='Too small to mine, but great for climbing icy surfaces.',
                         melee_weapon_skill=config.onehanded_hammers_skill,
                         melee_weapon_stat=config.Str, combat_exhaustion=2,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 2}},
                                  config.resistances_and_affinities: {config.ice_climbing_cost: -20}})


class ShortSword(go.SmallWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='short sword', weight=3, icon='|', color=color,
                         description='Made for stabbing.',
                         melee_weapon_skill=config.onehanded_swords_skill, combat_exhaustion=3,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 3}}})


class Hatchet(go.SmallWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='hatchet', weight=2, icon='|', color=color,
                         description="Cut wood or chop limbs, it's your choice.",
                         melee_weapon_skill=config.onehanded_axes_skill, combat_exhaustion=2,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 2}}})


class Mace(go.SmallWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='mace', weight=4, icon='|', color=color,
                         description='A wooden handle with a metal ball on one end.',
                         melee_weapon_skill=config.onehanded_hammers_skill, combat_exhaustion=4,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 4}}})


class PunchKnife(go.SmallWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='punch knife', weight=1, icon='|', color=color,
                         description='A blade with a cross handle, made for punching through armor.',
                         melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=2,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 2}}})


class Claws(go.SmallWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='claws', weight=1, icon='|', color=color,
                         description='Metal claws that can be gripped in a fist.',
                         melee_weapon_skill=config.unarmed_combat_skill,
                         melee_weapon_stat=config.Dex, combat_exhaustion=4,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 2}}})


class Buckler(go.Shield):
    def __init__(self):
        super().__init__(name='buckler', weight=3, icon=']', color=console.fg.lightblack,
                         description='A small, round shield made of iron.',
                         effects={config.effect_modifiers: {config.evasion_modifier: 1.3}}, combat_exhaustion=1)


class RoundShield(go.Shield):
    def __init__(self):
        super().__init__(name='round shield', weight=4, icon=']', color=config.brown_fg_color,
                         description='A round, wooden shield. Can carry a coat of arms.',
                         effects={config.effect_modifiers: {config.evasion_modifier: 1.6}}, combat_exhaustion=2)


class TowerShield(go.Shield):
    def __init__(self):
        super().__init__(name='tower shield', weight=7, icon=']', color=console.fg.lightblack,
                         description='A tall, rectangular metal shield.',
                         effects={config.effect_modifiers: {config.evasion_modifier: 2.1}}, combat_exhaustion=4)


class AcornGun(go.RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='acorn gun', weight=4, icon='{', color=color,
                         description='A gun of dryadic design.',
                         combat_exhaustion=2, ranged_weapon_type=config.acorn_gun_type,
                         ranged_weapon_skill=config.gun_skill, ranged_weapon_stat=config.Per,
                         max_distance=15,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 3},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class Acorn(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='acorn', weight=1, icon='*', color=config.brown_fg_color,
                         is_stackable=True, description='The seed of an oak tree.',
                         ranged_ammo_type=config.acorn_gun_type,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 1}}})


class ShortBow(go.RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='short bow', weight=2, icon='{', color=color,
                         description='A wooden bow stringed with tendon.',
                         combat_exhaustion=3, ranged_weapon_type=config.bow_type,
                         ranged_weapon_skill=config.bow_skill, ranged_weapon_stat=config.Dex,
                         max_distance=10,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 1},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class LongBow(go.RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='long bow', weight=4, icon='{', color=color,
                         description='A combat-ready bow.',
                         combat_exhaustion=4, ranged_weapon_type=config.bow_type,
                         ranged_weapon_skill=config.bow_skill, ranged_weapon_stat=config.Dex,
                         max_distance=20,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 3},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class Arrow(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='arrow', weight=1, icon='-', color=config.brown_fg_color,
                         is_stackable=True, description='Tipped with iron and stabilized with bird feathers.',
                         ranged_ammo_type=config.bow_type,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 2}}})


class Handgun(go.RangedWeapon):
    def __init__(self, color=console.fg.lightblack):
        super().__init__(name='hand gun', weight=3, icon='{', color=color,
                         description='A mechanical contraption that fires combustible ammunition.',
                         combat_exhaustion=1, ranged_weapon_type=config.gun_type,
                         ranged_weapon_skill=config.gun_skill, ranged_weapon_stat=config.Per,
                         max_distance=10,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 2},
                                                          config.melee_combat: {config.physical_damage: 1}}})


class Rifle(go.RangedWeapon):
    def __init__(self, color=console.fg.lightblack):
        super().__init__(name='rifle', weight=6, icon='{', color=color,
                         description='A gun with a long barrel. Hunters and assassins love them.',
                         combat_exhaustion=1, ranged_weapon_type=config.gun_type,
                         ranged_weapon_skill=config.gun_skill, ranged_weapon_stat=config.Per,
                         max_distance=25,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 4},
                                                          config.melee_combat: {config.physical_damage: 1}}})


class GunRound(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='gun round', weight=1, icon='*', color=console.fg.lightblack,
                         is_stackable=True, ranged_ammo_type=config.gun_type,
                         description='A metal casing with alchemical powders inside. Keep away from fire!',
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 3}}})


class CrossBow(go.RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='crossbow', weight=4, icon='{', color=color,
                         description='A wood and metal contraption made to fire short bolts.',
                         combat_exhaustion=1, ranged_weapon_type=config.crossbow_type,
                         ranged_weapon_skill=config.crossbow_skill, ranged_weapon_stat=config.Per,
                         max_distance=14,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 2},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class Bolt(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='bolt', weight=1, icon='-', color=console.fg.default,
                         is_stackable=True, description='An iron crossbow bolt.',
                         ranged_ammo_type=config.crossbow_type,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 2}}})


class Ballista(go.RangedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='ballista', weight=9, icon='{', color=color,
                         description='A small siege engine. Some mercenaries lug these around.',
                         combat_exhaustion=12, ranged_weapon_type=config.ballista_type,
                         ranged_weapon_skill=config.crossbow_skill, ranged_weapon_stat=config.Str,
                         max_distance=25,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 6},
                                                          config.melee_combat: {config.physical_damage: 1}}})


class BallistaBolt(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='large bolt', weight=2, icon='|', color=config.brown_fg_color,
                         is_stackable=True, description='Two-fingers thick, and long as your arm.',
                         ranged_ammo_type=config.ballista_type,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 4}}})


class Sling(go.RangedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='sling', weight=1, icon='{', color=color,
                         description='A couple of straps with a leather piece in the middle.',
                         combat_exhaustion=2, ranged_weapon_type=config.sling_type,
                         ranged_weapon_skill=config.sling_skill, ranged_weapon_stat=config.Dex,
                         max_distance=8,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 1},
                                                          config.melee_combat: {config.physical_damage: 0}}})


class SlingBullet(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='sling bullet', weight=1, icon='*', color=console.fg.lightblack,
                         description="A metal or rock piece inscribed with the word 'Catch!'",
                         is_stackable=True, ranged_ammo_type=config.sling_type,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 3}}})


class Dagger(go.ThrownWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='dagger', weight=2, icon='}', color=color,
                         description='A sharp blade for stabbing or throwing.',
                         melee_weapon_skill=config.daggers_skill, melee_weapon_stat=config.Dex, combat_exhaustion=1,
                         ranged_weapon_type=config.throwing_knife_skill, max_distance=5,
                         ranged_ammo_type=config.throwing_knife_skill, ranged_weapon_skill=config.throwing_knife_skill,
                         ranged_weapon_stat=config.Dex,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 2},
                                                          config.melee_combat: {config.physical_damage: 2}}})


class ThrowingKnife(go.ThrownWeapon):
    def __init__(self, color=console.fg.white):
        super().__init__(name='throwing knife', weight=1, icon='}', color=color,
                         description='A light knife, balanced for throwing.',
                         melee_weapon_skill=config.daggers_skill, melee_weapon_stat=config.Dex, combat_exhaustion=1,
                         ranged_weapon_type=config.throwing_knife_skill, max_distance=7,
                         ranged_ammo_type=config.throwing_knife_skill, ranged_weapon_skill=config.throwing_knife_skill,
                         ranged_weapon_stat=config.Dex,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 3},
                                                          config.melee_combat: {config.physical_damage: 1}}})


class HuntingSpear(go.ThrownWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='hunting spear', weight=2, icon='}', color=color,
                         description='A light spear, perfect for hunting animals.',
                         melee_weapon_skill=config.spear_skill, melee_weapon_stat=config.Dex, combat_exhaustion=3,
                         ranged_weapon_type=config.throwing_spear_skill, max_distance=10,
                         ranged_ammo_type=config.throwing_spear_skill, ranged_weapon_skill=config.throwing_spear_skill,
                         ranged_weapon_stat=config.Str,
                         effects={config.combat_effects: {config.ranged_combat: {config.physical_damage: 5},
                                                          config.melee_combat: {config.physical_damage: 2}}})


class RopeAndHook(go.TwoHandedWeapon):
    # TODO: Add to items spreadsheet
    def __init__(self, color=console.fg.lightblack):
        super().__init__(name='rope and hook', weight=6, icon='^', color=color,
                         description='For scaling mountains.',
                         melee_weapon_skill=config.sling_skill,
                         melee_weapon_stat=config.Dex, combat_exhaustion=7,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 2}},
                                  config.effect_modifiers: {config.rock_climbing_cost: 0.01}})


class GreatSword(go.TwoHandedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='great sword', weight=8, icon='/', color=color,
                         description='Cutting beasts in half is easy with this one.',
                         melee_weapon_skill=config.twohanded_swords_skill, combat_exhaustion=7,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 8}}})


class Staff(go.TwoHandedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='staff', weight=4, icon='/', color=color,
                         description='A long stick is better than nothing.',
                         melee_weapon_skill=config.staves_skill, combat_exhaustion=2,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 3}},
                                  config.effect_modifiers: {config.evasion_modifier: 1.3}})


class BattleStaff(go.TwoHandedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='battle staff', weight=7, icon='/', color=color,
                         description='The ends are capped with metal.',
                         melee_weapon_skill=config.staves_skill, combat_exhaustion=5,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 6}},
                                  config.effect_modifiers: {config.evasion_modifier: 1.1}})


class TravellerStaff(go.TwoHandedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name="traveller's staff", weight=2, icon='/', color=color,
                         description='A stick to make walking easier.',
                         melee_weapon_skill=config.staves_skill, combat_exhaustion=1,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 1}},
                                  config.effect_modifiers: {config.evasion_modifier: 1.2}})


class GiantAxe(go.TwoHandedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name="giant axe", weight=10, icon='/', color=color,
                         description='A huge axe with twin crescent blades.',
                         melee_weapon_skill=config.twohanded_axes_skill, combat_exhaustion=12,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 10}}})


class WarHammer(go.TwoHandedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name="war hammer", weight=11, icon='/', color=color,
                         description='The head has a claw on one side and a plate on the other.',
                         melee_weapon_skill=config.twohanded_hammers_skill, combat_exhaustion=14,
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 12}}})


class SmallTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of a small animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 1}}})


class MediumTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of an animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 3}}})


class MediumClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='claws', weight=1, icon=',', color=console.fg.lightyellow,
                         description='The claws of an animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 3}}})


class LargeClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='large claws', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The claws of a large animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 5}}})


class HugeClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='huge claws', weight=5, icon=',', color=console.fg.lightyellow,
                         description='The claws of a monstrous animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 10}}})


class LargeTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='large teeth', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The teeth of a large animal',
                         effects={config.combat_effects: {config.melee_combat: {config.physical_damage: 5}}})


class LightHide(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='light hide', weight=5, icon='(', color=config.brown_fg_color,
                         description='The light hide of an animal',
                         effects={config.resistances_and_affinities: {config.physical_damage: -1}}, )


class MediumHide(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='medium hide', weight=10, icon='(', color=config.brown_fg_color,
                         description='The thick hide of an animal',
                         effects={config.resistances_and_affinities: {config.physical_damage: -2}}, )


class MediumScales(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='medium scaly hide', weight=10, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a lizard',
                         effects={config.resistances_and_affinities: {config.physical_damage: -2}}, )


class HeavyScales(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='heavy scaled hide', weight=20, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a monstrous lizard',
                         effects={config.resistances_and_affinities: {config.physical_damage: -5}}, )


class Feathers(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='feathers', weight=3, icon=',', color=console.fg.lightblack,
                         description='The feathers of a bird',
                         effects={config.resistances_and_affinities: {config.physical_damage: -1}}, )


class RawMeat(go.EdibleAnimalPart):
    def __init__(self):
        super().__init__(name='raw meat', weight=1, icon=',', color=console.fg.red,
                         description="Not fit for eating, unless you're an ork!",
                         effects={config.consumable_effects: {config.sick_effect: 10, config.hunger_meat_effect: 5}})


class Rock(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblack,
                         description='Building material and throwing weapon',
                         effects={config.consumable_effects: {config.hunger_rock_effect: 5,
                                                              config.thirst_rock_effect: 5},
                                  config.combat_effects: {config.ranged_combat: {config.physical_damage: 1}}},
                         is_stackable=True, ranged_ammo_type=config.hand_thrown_type)


class Firewood(go.Item):
    def __init__(self):
        super().__init__(name='firewood', weight=1, icon='-', color=config.brown_fg_color,
                         description='Can be used to light a fire')


class IronOre(go.Item):
    def __init__(self):
        super().__init__(name='iron ore', weight=2, icon='*', color=console.fg.default,
                         description='Can be smelted and turned into metal bars',
                         effects={config.consumable_effects: {config.hunger_rock_effect: 10,
                                                              config.thirst_rock_effect: -5}})


class SilverOre(go.Item):
    def __init__(self):
        super().__init__(name='silver ore', weight=2, icon='*', color=console.fg.lightwhite,
                         description='Can be smelted and turned into metal bars',
                         effects={config.consumable_effects: {config.hunger_rock_effect: -5,
                                                              config.thirst_rock_effect: 5}})


class GoldOre(go.Item):
    def __init__(self):
        super().__init__(name='gold ore', weight=2, icon='*', color=console.fg.yellow,
                         description='Can be smelted and turned into metal bars',
                         effects={config.consumable_effects: {config.hunger_rock_effect: -5,
                                                              config.thirst_rock_effect: 15}})


class IceShard(go.Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblue,
                         description='Can be melted for drinking, or used to cool things')


class StilledWaterShard(go.Item):
    def __init__(self):
        super().__init__(name='stilled water', weight=2, icon='*', color=console.fg.white,
                         description='Used to meld still water equipment')


# Resource singletons
#  Powers
fire_power = go.Power(name='fire', color=console.fg.lightred, icon='*', description='It heats and burns')
#  Liquids
water_liquid = go.Liquid(name='water', weight=1, icon=',', color=console.fg.blue,
                         description='The one thing everyone needs',
                         effects={config.consumable_effects: {config.thirst_water_effect: 20,
                                                              config.hunger_water_effect: 0}})
wine_liquid = go.Liquid(name='wine', weight=1, icon=',', color=console.fg.red,
                        description='Fermented fruit juice',
                        effects={config.consumable_effects: {config.thirst_water_effect: 15,
                                                             config.drunk_effect: 10}})

# Item transformations
# NOTE: The order of transformations matters, as the Game takes the first matching one!
item_transformations = {
    Firewood: {config.burning_fire_tool: {config.transformation_effects: {config.light_a_fire: 15},
                                          config.transformation_command: commands.AddToFire},
               config.fire_lighter_tool: {config.transformation_effects: {config.light_a_fire: 15},
                                          config.transformation_command: commands.LightAFire}}
}
