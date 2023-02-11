"""
Concrete Item objects
"""
import game_objects as go
import config
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
                         armor=0, armor_skill=config.evasion_skill, armor_stat=config.Dex,
                         evasion_modifier=1, combat_exhaustion=0)


class HideArmor(go.Armor):
    def __init__(self):
        super().__init__(name='hide armor', weight=5, icon='(', color=config.brown_fg_color,
                         description='Armor made from light hide',
                         armor=1, armor_skill=config.light_armor_skill, armor_stat=config.Dex,
                         evasion_modifier=0.9, combat_exhaustion=1)


class LeatherArmor(go.Armor):
    def __init__(self):
        super().__init__(name='leather armor', weight=6, icon='(', color=config.brown_fg_color,
                         description='Armor made from leather',
                         armor=3, armor_skill=config.light_armor_skill, armor_stat=config.Dex,
                         evasion_modifier=0.85, combat_exhaustion=1)


class ChainMail(go.Armor):
    def __init__(self):
        super().__init__(name='chain mail', weight=9, icon='[', color=console.fg.lightblack,
                         description='A shirt of woven iron links.',
                         armor=5, armor_skill=config.heavy_armor_skill, armor_stat=config.End,
                         evasion_modifier=0.6, combat_exhaustion=3)


class PlateArmor(go.Armor):
    def __init__(self):
        super().__init__(name='plate armor', weight=15, icon='[', color=console.fg.default,
                         description='Armor made from metal plates',
                         armor=7, armor_skill=config.heavy_armor_skill, armor_stat=config.End,
                         evasion_modifier=0.3, combat_exhaustion=5)


class Bag(go.Back):
    def __init__(self):
        super().__init__(name='bag', weight=1, width=3, height=1, icon='=',
                         color=console.fg.default, description='A very small bag')


class AcornGun(go.RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='acorn gun', weight=4, icon='{', color=color,
                         description='A gun of dryadic design.',
                         ranged_damage=3, combat_exhaustion=2, ranged_weapon_type=config.acorn_gun_type,
                         ranged_weapon_skill=config.gun_skill, ranged_weapon_stat=config.Per,
                         max_distance=15)


class Fist(go.Tool):
    def __init__(self):
        super().__init__(name="Your fist", description="Useful when you don't have a sword at hand.",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, work_skill=config.scavenging_skill, work_stat=config.Per,
                         melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=1)


class TrollFist(go.Tool):
    def __init__(self):
        super().__init__(name="Your fist", description="You can break rocks for eating with it!",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, work_skill=config.mining_skill, work_stat=config.Str,
                         melee_damage=1, melee_weapon_skill=config.unarmed_combat_skill, combat_exhaustion=1)


class Pickaxe(go.Tool):
    def __init__(self):
        super().__init__(name="a pickaxe", description="Used to extract stone and ores",
                         weight=6, icon='/', color=console.fg.lightblack,
                         work_exhaustion=5, work_skill=config.mining_skill, work_stat=config.Str,
                         melee_damage=1, melee_weapon_skill=config.twohanded_axes_skill,
                         combat_exhaustion=5)


class ShortSword(go.MainHand):
    def __init__(self, color=console.fg.default):
        super().__init__(name='short sword', weight=3, icon='|', color=color,
                         description='Made for stabbing.',
                         melee_damage=3, melee_weapon_skill=config.onehanded_swords_skill, combat_exhaustion=3)


class Buckler(go.Shield):
    def __init__(self):
        super().__init__(name='buckler', weight=3, icon=']', color=console.fg.lightblack,
                         description='A small, round shield made of iron.',
                         evasion_modifier=1.3, combat_exhaustion=1)


class Acorn(go.RangedAmmo):
    def __init__(self):
        super().__init__(name='acorn', weight=1, icon='*', color=config.brown_fg_color,
                         is_stackable=True, description='The seed of an oak tree.',
                         ranged_damage=1, ranged_ammo_type=config.acorn_gun_type)


class Dagger(go.ThrownWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='dagger', weight=2, icon='}', color=color,
                         description='A sharp blade for stabbing or throwing.',
                         melee_damage=2, melee_weapon_skill=config.daggers_skill, melee_weapon_stat=config.Dex,
                         ranged_damage=2, combat_exhaustion=1,
                         ranged_weapon_type=config.throwing_knife_skill, max_distance=5,
                         ranged_ammo_type=config.throwing_knife_skill, ranged_weapon_skill=config.throwing_knife_skill,
                         ranged_weapon_stat=config.Dex)


class ThrowingKnife(go.ThrownWeapon):
    def __init__(self, color=console.fg.white):
        super().__init__(name='throwing knife', weight=1, icon='}', color=color,
                         description='A light knife, balanced for throwing.',
                         melee_damage=1, melee_weapon_skill=config.daggers_skill, melee_weapon_stat=config.Dex,
                         ranged_damage=3, combat_exhaustion=1,
                         ranged_weapon_type=config.throwing_knife_skill, max_distance=7,
                         ranged_ammo_type=config.throwing_knife_skill, ranged_weapon_skill=config.throwing_knife_skill,
                         ranged_weapon_stat=config.Dex)


class GreatSword(go.TwoHandedWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='great sword', weight=8, icon='|', color=color,
                         description='Cutting beasts in half is easy with this one.',
                         melee_damage=7, melee_weapon_skill=config.twohanded_swords_skill, combat_exhaustion=7)


class SmallTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of a small animal', melee_damage=1)


class MediumTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of an animal', melee_damage=3)


class MediumClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='claws', weight=1, icon=',', color=console.fg.lightyellow,
                         description='The claws of an animal', melee_damage=3)


class LargeClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='large claws', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The claws of a large animal', melee_damage=5)


class HugeClaws(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='huge claws', weight=5, icon=',', color=console.fg.lightyellow,
                         description='The claws of a monstrous animal', melee_damage=10)


class LargeTeeth(go.AnimalWeapon):
    def __init__(self):
        super().__init__(name='large teeth', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The teeth of a large animal', melee_damage=5)


class LightHide(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='light hide', weight=5, icon='(', color=config.brown_fg_color,
                         description='The light hide of an animal', armor=1)


class MediumHide(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='medium hide', weight=10, icon='(', color=config.brown_fg_color,
                         description='The thick hide of an animal', armor=2)


class MediumScales(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='medium scaly hide', weight=10, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a lizard', armor=2)


class HeavyScales(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='heavy scaled hide', weight=20, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a monstrous lizard', armor=5)


class Feathers(go.AnimalArmor):
    def __init__(self):
        super().__init__(name='feathers', weight=3, icon=',', color=console.fg.lightblack,
                         description='The feathers of a bird', armor=1)


class RawMeat(go.EdibleAnimalPart):
    def __init__(self):
        super().__init__(name='raw meat', weight=1, icon=',', color=console.fg.red,
                         description="Not fit for eating, unless you're an ork!",
                         effects={config.sick_effect: 10,
                                  config.hunger_meat_effect: 5})


class Rock(go.Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblack,
                         description='Building material and throwing weapon',
                         effects={config.hunger_rock_effect: 10,
                                  config.thirst_rock_effect: 10},
                         is_stackable=True)


class IronOre(go.Item):
    def __init__(self):
        super().__init__(name='iron ore', weight=2, icon='*', color=console.fg.default,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 20,
                                  config.thirst_rock_effect: 5})


class SilverOre(go.Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightwhite,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 5,
                                  config.thirst_rock_effect: 15})


class GoldOre(go.Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.yellow,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 5,
                                  config.thirst_rock_effect: 25})


class IceShard(go.Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblue,
                         description='Can be melted for drinking, or used to cool things')


class StilledWaterShard(go.Item):
    def __init__(self):
        super().__init__(name='stilled water', weight=2, icon='*', color=console.fg.white,
                         description='Used to meld still water equipment')


# Liquids
water_liquid = go.Liquid(name='water', weight=1, icon=',', color=console.fg.blue,
                         description='The one thing everyone needs',
                         effects={config.thirst_water_effect: 20,
                                  config.hunger_water_effect: 0})
wine_liquid = go.Liquid(name='wine', weight=1, icon=',', color=console.fg.red,
                        description='Fermented fruit juice',
                        effects={config.thirst_water_effect: 15, config.drunk_effect: 10})
