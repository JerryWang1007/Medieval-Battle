#* ***********************************************************************
# Jerry Wang
# Medieval Battle
# Computer Science 30 IB
# 6/12/24

#This program is my own work - (JW) */

# Pygame required
# This game is probably very imbalanced, too lazy to make the game fair
'''
Extensions / Game Mechanics:

- Playable character against waves of randomly generated enemies
- Movement: WASD, Attack: SPACE, Abilities: QER
- Command Keys to test/mark the game easier
    - b: sets player health to 0 (ends game)
    - m: kills all enemies (test death animations, cycles enemies)
    - n: add points (push to 10 to see new enemy)
    - v: max health (if bad at game)

- Graphics - 30 fps - Stolen assets - Animations
    - Health displays
- Abilities, Custom attacks for enemies and player
- Enemies spawn in a random order in a pool of 6 enemies, each enemy must spawn once before an enemy can spawn a second time
- Starting at round 10, an additional enemy is added to increase difficulty
- Starting at round 15, every attack does and extra (round-15) damage
- Red rings appear below the player, signifying danger
- A set of 3 minions chosen from 2 different pools of minions accompany the "main" enemy
    - Bandits: heavy bandit always in middle, light bandits on the sides
    - Other: Random selection of 3 between skeleton, mushroom, and flying eye

Player: 
- 3 different animations for basic attack
- 3 Abilities:
    - Q: Basic ability - does damage - ignores defence
    - E: Basic heal - does damage, heals small amount
    - R: Large heal ability - Drains enemy health, heals you for that health

Enemies:
Bringer of Death:
- Basic attack in a cone shape
- Spell cast that creates 3 floating projectiles above the player
Light/Heavy Bandit:
- Generic minions, attacks a random position
Cultist Priest:
- Has massive defence and health
- Attacks slowly in two random columns
Medieval King: 
- Has 3 different attack animations
    - 3 different attack patterns
Evil Wizard:
- Attacks have vampirism, drain health from player and heals themself
Wind Hashashin:
- 4 different attack patterns
    - 1: attacks 2 random columns very fast
    - 2: attack pattern 1 + barrage of random attacks
    - 3: attack pattern 1 + 2 + tornado attack
    - 4: teleports to player side and attacks player's position
NightBorne: 
- Appears after at round 10
- Very strong attacks in a singular row, attacks based on player's position
Skeleton:
- Generic minions, attacks a random position
Mushroom:
- Generic minion, attacks a random position
- Attacks give a "poison" effect, dealing damage over time, ignoring defense
Flying Eye:
- Generic minion, attacks a random position
- Attacks have vampirism, heals for the amount of damage dealt
Necromancer:
- Spawns skeleton minions over time
'''

import pygame
import random

pygame.init()
pygame.font.init()

fps = 30
animationSpeed = 3 # animation speed is slowed by x times

WIDTH, HEIGHT = 1500, 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.font.Font(r'CS30\MedievalBattle\assets\slkscr.ttf', 75)
font2 = pygame.font.Font(r'CS30\MedievalBattle\assets\slkscr.ttf', 30)

moving = False

gridx = [ # derive middle points from self.dangerArea
    [414, 511, 608], # eg. (380 + 475 + 450 + 350)/4
    [372, 483, 590], # opposite side is WIDTH-gridx[][]+10
    [333, 454, 575]
]
gridy = [515, 553, 603]
originalweightedindex = [8, 9, 10, 11, 12, 13]
weightedindex = [8, 9, 10, 11, 12, 13]

score = -1

warriorScale = 3
bringerOfDeathScale = 4
banditScale = 3
cultistPriestScale = 2
medievalKingScale = 3
evilWizardScale = 2
windHashashinScale = 4
nightBorneScale = 5
skeletonScale = 3
mushroomScale = 3
flyingEyeScale = 3
necromancerScale = 3
necromancertoNormalScale = 4/3

sprite_data = {
    # "name" : (start, numelements, count, scale, link)
    "warriorIdle": (0, 4, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorIdle\adventurer-idle-2-0{}.png'),
    "warriorSpellCast": (0, 8, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorSpellCast\adventurer-cast-0{}.png'),
    "warriorSpell1": (1, 5, 0, 1.3, False, r'CS30\MedievalBattle\assets\LightEffect_0{}.png'),
    "warriorSpell2": (1, 5, 0, 1.3, False, r'CS30\MedievalBattle\assets\Water__0{}.png'),
    "warriorSpell3": (21, 5, 0, 1.3, False, r'CS30\MedievalBattle\assets\Blood-Magic-Effect_{}.png'),
    "warriorSlide": (0, 2, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorSlide\adventurer-slide-0{}.png'),
    "warriorBasicProjectile": (6, 5, 0, 0.5, False, r'CS30\MedievalBattle\warrior\warriorBasicProjectile\Pure_0{}.png'),
    "warriorBasicAttack1": (0, 5, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorBasicAttack\adventurer-attack1-0{}.png'),
    "warriorBasicAttack2": (0, 5, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorBasicAttack\adventurer-attack2-0{}.png'),
    "warriorBasicAttack3": (0, 5, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorBasicAttack\adventurer-attack3-0{}.png'),
    "warriorHurt": (0, 3, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorHurt\adventurer-hurt-0{}.png'),
    "warriorDie": (0, 7, 0, warriorScale, False, r'CS30\MedievalBattle\warrior\warriorDie\adventurer-die-0{}.png'),
    "bringerOfDeathIdle": (1, 8, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\idle\Bringer-of-Death_Idle_{}.png'),
    "bringerOfDeathAttack": (1, 10, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\attack\Bringer-of-Death_Attack_{}.png'),
    "bringerOfDeathCast": (1, 9, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\cast\Bringer-of-Death_Cast_{}.png'),
    "bringerOfDeathSpell": (1, 16, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\spell\Bringer-of-Death_Spell_{}.png'),
    "bringerOfDeathHurt": (1, 3, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\hurt\Bringer-of-Death_Hurt_{}.png'),
    "bringerOfDeathDeath": (1, 10, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\death\Bringer-of-Death_Death_{}.png'),
    "bringerOfDeathWalk": (1, 8, 0, bringerOfDeathScale, False, r'CS30\MedievalBattle\bringerOfDeath\walk\Bringer-of-Death_Walk_{}.png'),
    "lightBanditIdle": (0, 4, 0, banditScale, False, r'CS30\MedievalBattle\lightBandit\idle\LightBandit_Combat Idle_{}.png'),
    "lightBanditAttack": (0, 8, 0, banditScale, False, r'CS30\MedievalBattle\lightBandit\attack\LightBandit_Attack_{}.png'),
    "lightBanditWalk": (0, 8, 0, banditScale, False, r'CS30\MedievalBattle\lightBandit\walk\LightBandit_Run_{}.png'),
    "lightBanditHurt": (0, 2, 0, banditScale, False, r'CS30\MedievalBattle\lightBandit\hurt\LightBandit_Hurt_{}.png'),
    "lightBanditDeath": (0, 9, 0, banditScale, False, r'CS30\MedievalBattle\lightBandit\death\LightBandit_Death_{}.png'),
    "heavyBanditIdle": (0, 4, 0, banditScale, False, r'CS30\MedievalBattle\heavyBandit\idle\HeavyBandit_CombatIdle_{}.png'),
    "heavyBanditAttack": (0, 8, 0, banditScale, False, r'CS30\MedievalBattle\heavyBandit\attack\HeavyBandit_Attack_{}.png'),
    "heavyBanditWalk": (0, 8, 0, banditScale, False, r'CS30\MedievalBattle\heavyBandit\walk\HeavyBandit_Run_{}.png'),
    "heavyBanditHurt": (0, 2, 0, banditScale, False, r'CS30\MedievalBattle\heavyBandit\hurt\HeavyBandit_Hurt_{}.png'),
    "heavyBanditDeath": (0, 9, 0, banditScale, False, r'CS30\MedievalBattle\heavyBandit\death\HeavyBandit_Death_{}.png'),
    "cultistPriestIdle": (1, 5, 0, cultistPriestScale, True, r'CS30\MedievalBattle\cultistPriest\idle\cultist_priest_idle_{}.png'),
    "cultistPriestAttack": (1, 5, 0, cultistPriestScale, True, r'CS30\MedievalBattle\cultistPriest\attack\cultist_priest_attack_{}.png'),
    "cultistPriestHurt": (1, 4, 0, cultistPriestScale, True, r'CS30\MedievalBattle\cultistPriest\hurt\cultist_priest_takehit_{}.png'),
    "cultistPriestDeath": (1, 6, 0, cultistPriestScale, True, r'CS30\MedievalBattle\cultistPriest\death\cultist_priest_die_{}.png'),
    "culristPriestWalk": (1, 6, 0, cultistPriestScale, True, r'CS30\MedievalBattle\cultistPriest\walk\cultist_priest_walk_{}.png'),
    "medievalKingIdle": (0, 8, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\idle\Idle_{}.png'),
    "medievalKingAttack1": (0, 4, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\attack\Attack1_{}.png'),
    "medievalKingAttack2": (0, 4, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\attack\Attack2_{}.png'),
    "medievalKingAttack3": (0, 4, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\attack\Attack3_{}.png'),
    "medievalKingHurt": (0, 4, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\hurt\Hurt_{}.png'),
    "medievalKingDeath": (0, 6, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\death\Death_{}.png'),
    "medievalKingWalk": (0, 8, 0, medievalKingScale, True, r'CS30\MedievalBattle\medievalKing\walk\Run_{}.png'),
    "evilWizardIdle": (0, 8, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\idle\Idle_{}.png'),
    "evilWizardAttack1": (0, 8, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\attack\Attack1_{}.png'),
    "evilWizardAttack2": (0, 8, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\attack\Attack2_{}.png'),
    "evilWizardHurt": (0, 3, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\hurt\Hurt_{}.png'),
    "evilWizardDeath": (0, 7, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\death\Death_{}.png'),
    "evilWizardWalk": (0, 8, 0, evilWizardScale, True, r'CS30\MedievalBattle\evilWizard\walk\Run_{}.png'),
    "evilWizardSpell": (11, 5, 0, 1, True, r'CS30\MedievalBattle\evilWizard\attackprojectile\Blood-Magic-Effect_{}.png'),
    "windHashashinIdle": (1, 8, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\idle\idle_{}.png'),
    "windHashashinAttack1": (1, 8, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\attack_1\1_atk_{}.png'),
    "windHashashinAttack2": (1, 18, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\attack_2\2_atk_{}.png'),
    "windHashashinAttack3": (1, 26, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\attack_3\3_atk_{}.png'),
    "windHashashinAttack4": (1, 30, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\attack_4\sp_atk_{}.png'),
    "windHashashinHurt": (1, 6, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\hurt\take_hit_{}.png'),
    "windHashashinDeath": (1, 19, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\death\death_{}.png'),
    "windHashashinWalk": (1, 8, 0, windHashashinScale, True, r'CS30\MedievalBattle\windHashashin\walk\run_{}.png'),
    "nightBorneIdle": (0, 9, 0, nightBorneScale, True, r'CS30\MedievalBattle\nightBorne\idle\idle{}.png'),
    "nightBorneAttack": (0, 12, 0, nightBorneScale, True, r'CS30\MedievalBattle\nightBorne\attack\attack{}.png'),
    "nightBorneHurt": (0, 5, 0, nightBorneScale, True, r'CS30\MedievalBattle\nightBorne\hurt\hurt{}.png'),
    "nightBorneDeath": (0, 23, 0, nightBorneScale, True, r'CS30\MedievalBattle\nightBorne\death\death{}.png'),
    "nightBorneWalk": (0, 6, 0, nightBorneScale, True, r'CS30\MedievalBattle\nightBorne\walk\walk{}.png'),
    "skeletonIdle": (0, 4, 0, skeletonScale, True, r'CS30\MedievalBattle\skeleton\idle\idle{}.png'),
    "skeletonAttack": (0, 8, 0, skeletonScale, True, r'CS30\MedievalBattle\skeleton\attack\attack{}.png'),
    "skeletonHurt": (0, 4, 0, skeletonScale, True, r'CS30\MedievalBattle\skeleton\hurt\hurt{}.png'),
    "skeletonDeath": (0, 4, 0, skeletonScale, True, r'CS30\MedievalBattle\skeleton\hurt\hurt{}.png'),
    "skeletonWalk": (0, 4, 0, skeletonScale, True, r'CS30\MedievalBattle\skeleton\walk\walk{}.png'),
    "mushroomIdle": (0, 4, 0, mushroomScale, True, r'CS30\MedievalBattle\mushroom\idle\idle{}.png'),
    "mushroomAttack": (0, 8, 0, mushroomScale, True, r'CS30\MedievalBattle\mushroom\attack\attack{}.png'),
    "mushroomHurt": (0, 4, 0, mushroomScale, True, r'CS30\MedievalBattle\mushroom\hurt\hurt{}.png'),
    "mushroomDeath": (0, 4, 0, mushroomScale, True, r'CS30\MedievalBattle\mushroom\death\death{}.png'),
    "mushroomWalk": (0, 8, 0, mushroomScale, True, r'CS30\MedievalBattle\mushroom\walk\walk{}.png'),
    "flyingEyeFly": (0, 8, 0, flyingEyeScale, True, r'CS30\MedievalBattle\flyingEye\fly\fly{}.png'),
    "flyingEyeAttack": (0, 8, 0, flyingEyeScale, True, r'CS30\MedievalBattle\flyingEye\attack\attack{}.png'),
    "flyingEyeHurt": (0, 4, 0, flyingEyeScale, True, r'CS30\MedievalBattle\flyingEye\hurt\hurt{}.png'),
    "flyingEyeDeath": (0, 4, 0, flyingEyeScale, True, r'CS30\MedievalBattle\flyingEye\death\death{}.png'),
    "necromancerIdle": (0, 50, 0, necromancertoNormalScale*necromancerScale, True, r'CS30\MedievalBattle\necromancer\idle\tile0{}.png'),
    "necromancerAttack": (0, 47, 0, necromancerScale*1.3, True, r'CS30\MedievalBattle\necromancer\attack\tile0{}.png'),
    "necromancerCast": (0, 20, 0, necromancerScale*1.3, True, r'CS30\MedievalBattle\necromancer\cast\tile0{}.png'),
    "necromancerHurt": (0, 9, 0, necromancertoNormalScale*necromancerScale, True, r'CS30\MedievalBattle\necromancer\hurt\tile00{}.png'),
    "necromancerDeath": (0, 52, 0, necromancertoNormalScale*necromancerScale, True, r'CS30\MedievalBattle\necromancer\death\tile0{}.png'),
    "necromancerWalk": (0, 10, 0, necromancertoNormalScale*necromancerScale, True, r'CS30\MedievalBattle\necromancer\walk\tile00{}.png')
}

def initializeSprites(sprite_data):
    sprites = {}
    for name, data in sprite_data.items():
        start, numelements, count, scale, flip, link = data
        var_list = []
        loadSprite(start, numelements, var_list, scale, link, flip)
        sprites[name] = (var_list, count)
    return sprites

def loadSprite(start, numelements, var, scale, link_temp, flip):
    for i in range (start, start+numelements):
        link = link_temp.format(i)
        var.append(pygame.image.load(link))
    size = var[0].get_size()
    for i in range (numelements):
        var[i] = pygame.transform.scale(var[i], getScale(size, scale))
        if flip == True:
            var[i] = pygame.transform.flip(var[i], True, False)

def getScale(size, scale):
    return (size[0]*scale, size[1]*scale)

sprites = initializeSprites(sprite_data)
warriorIdle, warriorIdleCount = sprites["warriorIdle"]
warriorSpellCast, warriorSpellCastCount = sprites["warriorSpellCast"]
warriorSpell1, warriorSpell1Count = sprites["warriorSpell1"]
warriorSpell2, warriorSpell2Count = sprites["warriorSpell2"]
warriorSpell3, warriorSpell3Count = sprites["warriorSpell3"]
warriorSlide, warriorSlideCount = sprites["warriorSlide"]
warriorBasicProjectile, warriorBasicProjectileCount = sprites["warriorBasicProjectile"]
warriorBasicAttack1, warriorBasicAttackCount = sprites["warriorBasicAttack1"]
warriorBasicAttack2, warriorBasicAttackCount = sprites["warriorBasicAttack2"]
warriorBasicAttack3, warriorBasicAttackCount = sprites["warriorBasicAttack3"]
warriorHurt, warriorHurtCount = sprites["warriorHurt"]
warriorDie, warriorDieCount = sprites["warriorDie"]
bringerOfDeathIdle, bringerOfDeathIdleCount = sprites["bringerOfDeathIdle"]
bringerofDeathAttack, bringerofDeathAttackCount = sprites["bringerOfDeathAttack"]
bringerofDeathCast, bringerofDeathCastCount = sprites["bringerOfDeathCast"]
bringerofDeathSpell, bringerofDeathSpellCount = sprites["bringerOfDeathSpell"]
bringerofDeathHurt, bringerofDeathHurtCount = sprites["bringerOfDeathHurt"]
bringerofDeathDeath, bringerofDeathDeathCount = sprites["bringerOfDeathDeath"]
bringerofDeathWalk, bringerofDeathWalkCount = sprites["bringerOfDeathWalk"]
lightBanditIdle, lightBanditIdleCount = sprites["lightBanditIdle"]
lightBanditAttack, lightBanditAttackCount = sprites["lightBanditAttack"]
lightBanditWalk, lightBanditWalkCount = sprites["lightBanditWalk"]
lightBanditHurt, lightBanditHurtCount = sprites["lightBanditHurt"]
lightBanditDeath, lightBanditDeathCount = sprites["lightBanditDeath"]
heavyBanditIdle, heavyBanditIdleCount = sprites["heavyBanditIdle"]
heavyBanditAttack, heavyBanditAttackCount = sprites["heavyBanditAttack"]
heavyBanditWalk, heavyBanditWalkCount = sprites["heavyBanditWalk"]
heavyBanditHurt, heavyBanditHurtCount = sprites["heavyBanditHurt"]
heavyBanditDeath, heavyBanditDeathCount = sprites["heavyBanditDeath"]
cultistPriestIdle, cultistPriestIdleCount = sprites["cultistPriestIdle"]
cultistPriestAttack, cultistPriestAttackCount = sprites["cultistPriestAttack"]
cultistPriestHurt, cultistPriestHurtCount = sprites["cultistPriestHurt"]
cultistPriestDeath, cultistPriestDeathCount = sprites["cultistPriestDeath"]
culristPriestWalk, culristPriestWalkCount = sprites["culristPriestWalk"]
medievalKingIdle, medievalKingIdleCount = sprites["medievalKingIdle"]
medievalKingAttack1, medievalKingAttack1Count = sprites["medievalKingAttack1"]
medievalKingAttack2, medievalKingAttack2Count = sprites["medievalKingAttack2"]
medievalKingAttack3, medievalKingAttack3Count = sprites["medievalKingAttack3"]
medievalKingHurt, medievalKingHurtCount = sprites["medievalKingHurt"]
medievalKingDeath, medievalKingDeathCount = sprites["medievalKingDeath"]
medievalKingWalk, medievalKingWalkCount = sprites["medievalKingWalk"]
evilWizardIdle, evilWizardIdleCount = sprites["evilWizardIdle"]
evilWizardAttack1, evilWizardAttackCount = sprites["evilWizardAttack1"]
evilWizardAttack2, evilWizardAttackCount = sprites["evilWizardAttack2"]
evilWizardHurt, evilWizardHurtCount = sprites["evilWizardHurt"]
evilWizardDeath, evilWizardDeathCount = sprites["evilWizardDeath"]
evilWizardWalk, evilWizardWalkCount = sprites["evilWizardWalk"]
evilWizardSpell, evilWizardSpellCount = sprites["evilWizardSpell"]
windHashashinIdle, windHashashinIdleCount = sprites["windHashashinIdle"]
windHashashinAttack1, windHashashinAttack1Count = sprites["windHashashinAttack1"]
windHashashinAttack2, windHashashinAttack2Count = sprites["windHashashinAttack2"]
windHashashinAttack3, windHashashinAttack3Count = sprites["windHashashinAttack3"]
windHashashinAttack4, windHashashinAttack4Count = sprites["windHashashinAttack4"]
windHashashinHurt, windHashashinHurtCount = sprites["windHashashinHurt"]
windHashashinDeath, windHashashinDeathCount = sprites["windHashashinDeath"]
windHashashinWalk, windHashashinWalkCount = sprites["windHashashinWalk"]
nightBorneIdle, nightBorneIdleCount = sprites["nightBorneIdle"]
nightBorneAttack, nightBorneAttackCount = sprites["nightBorneAttack"]
nightBorneHurt, nightBorneHurtCount = sprites["nightBorneHurt"]
nightBorneDeath, nightBorneDeathCount = sprites["nightBorneDeath"]
nightBorneWalk, nightBorneWalkCount = sprites["nightBorneWalk"]
skeletonIdle, skeletonIdleCount = sprites["skeletonIdle"]
skeletonAttack, skeletonAttackCount = sprites["skeletonAttack"]
skeletonHurt, skeletonHurtCount = sprites["skeletonHurt"]
skeletonDeath, skeletonDeathCount = sprites["skeletonDeath"]
skeletonWalk, skeletonWalkCount = sprites["skeletonWalk"]
mushroomIdle, mushroomIdleCount = sprites["mushroomIdle"]
mushroomAttack, mushroomAttackCount = sprites["mushroomAttack"]
mushroomHurt, mushroomHurtCount = sprites["mushroomHurt"]
mushroomDeath, mushroomDeathCount = sprites["mushroomDeath"]
mushroomWalk, mushroomWalkCount = sprites["mushroomWalk"]
flyingEyeFly, flyingEyeFlyCount = sprites["flyingEyeFly"]
flyingEyeAttack, flyingEyeAttackCount = sprites["flyingEyeAttack"]
flyingEyeHurt, flyingEyeHurtCount = sprites["flyingEyeHurt"]
flyingEyeDeath, flyingEyeDeathCount = sprites["flyingEyeDeath"]
necromancerIdle, necromancerIdleCount = sprites["necromancerIdle"]
necromancerAttack, necromancerAttackCount = sprites["necromancerAttack"]
necromancerCast, necromancerCastCount = sprites["necromancerCast"]
necromancerHurt, necromancerHurtCount = sprites["necromancerHurt"]
necromancerDeath, necromancerDeathCount = sprites["necromancerDeath"]
necromancerWalk, necromancerWalkCount = sprites["necromancerWalk"]

def loadSprites():
    global background
    background = pygame.image.load(r'CS30\MedievalBattle\assets\background.jpg')
    backgroundSize = background.get_size()
    background = pygame.transform.scale(background, (backgroundSize[0]*1500/640, backgroundSize[1]*750/360))

class Character:
    def __init__(self, health, defence, x, y):
        self.name = "Null"
        self.health = health
        self.defence = defence
        self.x = x
        self.y = y
        self.dangerArea = [
            [
            ((380, 500),(475,500),(450, 530),(350, 530)), # top left
            ((475,500),(570, 500),(550, 530),(450, 530)), # top middle
            ((570, 500),(660, 500),(650, 530),(550, 530)) # top right
            ],
            [
            ((350, 530),(450, 530),(415, 575),(300, 575)), # middle left
            ((450, 530),(550, 530),(530, 575),(420, 575)), # middle 
            ((550, 530),(650, 530),(640, 575),(530, 575)) # middle right
            ],
            [
            ((300, 575),(415, 575),(375, 630),(240, 630)), # bottom left
            ((415, 575),(530, 575),(500, 630),(370, 630)), # bottom middle
            ((530, 575),(640, 575),(630, 630),(500, 630)) # bottom right
            ]
        ]
        self.idlevar = [list,int]
        self.attackvar = [list,int]
        self.hurtvar = [list,int]
        self.deathvar = [list,int]
        self.castvar = [list,int]
        self.walkvar = [list, int]
        self.health_initial = health
        self.offsety = int
        self.offsetx = int
        self.attackable = False
        self.hitx = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
        self.bleedAmount = 0
        self.hit = False
    alive = bool
    walking = True

    def idle(self):
        screen.blit(self.idlevar[0][self.idlevar[1]//animationSpeed % len(self.idlevar[0])], (self.x, self.y)) 
        self.idlevar[1] += 1

    def attack(self):
        screen.blit(self.attackvar[0][self.attackvar[1]//animationSpeed % len(self.attackvar[0])], (self.x, self.y)) 
        self.attackvar[1] += 1
        if self.attackvar[1] == len(self.attackvar[0])*animationSpeed:
            self.attackvar[1] = 0

    def hurt(self):
        screen.blit(self.hurtvar[0][self.hurtvar[1]//animationSpeed % len(self.hurtvar[0])], (self.x, self.y)) 
        self.hurtvar[1] += 1
        if self.hurtvar[1] == len(self.hurtvar[0])*animationSpeed:
            self.hurtvar[1] = 0

    def death(self):
        screen.blit(self.deathvar[0][self.deathvar[1]//animationSpeed % len(self.deathvar[0])], (self.x, self.y)) 
        self.deathvar[1] += 1
        if self.deathvar[1] == len(self.deathvar[0])*animationSpeed:
            self.deathvar[1] = 0
            self.alive = False
            self.walking = True

    def cast(self):
        screen.blit(self.castvar[0][self.castvar[1]//animationSpeed % len(self.castvar[0])], (self.x, self.y)) 
        self.castvar[1] += 1
        if self.castvar[1] == len(self.castvar[0])*animationSpeed:
            self.castvar[1] = 0

    def walk(self):
        screen.blit(self.walkvar[0][self.walkvar[1]//animationSpeed % len(self.walkvar[0])], (self.x, self.y))
        self.walkvar[1] += 1
        if self.walkvar[1] == len(self.walkvar[0])*animationSpeed:
            self.walkvar[1] = 0
        self.x -= 5

    def bleed(self):
        self.health -= 0.5
        self.bleedAmount -= 0.5

    def updateCooldown(self):
        if self.attackCooldown > 0 and self.attackvar[1] == 0 and self.walking == False:
            self.attackCooldown -= 1
        if self.attackCooldown == 0:
            self.attack()
            self.attackCooldown = self.attackCooldownInitial

    def animation(self):
        self.checkBleed()
        self.attackable = False
        if self.x > self.intendedx and self.walking == True:
            self.walk()
        elif self.x < self.intendedx and self.walking == True:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.attackvar[1] != 0:
            self.attack()
        elif self.hurtvar[1] != 0: # lower priority, attacking gives invincibility frames
            self.hurt()
        else:
            self.attackable = True # enemies only attackable when they are not doing any other animation
            self.idle()

    def display_danger(self, alpha, hitFrame, damage):
        for i in range (3):
            for j in range (3):
                if self.hitx[i][j] == 1:
                    if alpha < 0:
                        alpha = 0
                    if self.attackvar[1] >= hitFrame*animationSpeed:
                        alpha = 0
                        if self.attackvar[1] == hitFrame*animationSpeed and mainCharacter.posx == j and mainCharacter.posy == i:
                            mainCharacter.hurt()
                            mainCharacter.health -= (damage*(1-(mainCharacter.defence/100)))
                            self.hit = True
                    if alpha >= 255:
                        alpha = 255
                    shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                    pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                    screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
        self.hitx = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

    def checkBleed(self):
        if self.bleedAmount != 0:
            self.bleed()

    def display_health(self, numenemies):
        pygame.draw.rect(screen, (25, 25, 25), (WIDTH-50-self.health_initial*3, 50+100*numenemies, self.health_initial*3, 50))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH-50-self.health*3, 50+100*numenemies, self.health*3, 50))
        
        textRect = font2.render(f"{self.name} {self.health}", True, "#ffffff").get_rect()
        textRect.topright = (WIDTH-50, 10+100*numenemies)
        screen.blit(font2.render(f"{self.name} {self.health}", True, "#ffffff"), textRect)

class Warrior(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        global warriorIdle, warriorIdleCount
        self.idlevar = [warriorIdle, warriorIdleCount]
        self.hurtvar = [warriorHurt, warriorHurtCount]
        self.deathvar = [warriorDie, warriorDieCount]
        self.offsetx = 75
        self.offsety = 105
        self.spell1 = warriorSpell(self.x, self.y, 25, "Q")
        self.spell2 = warriorSpell(self.x, self.y, 25, "E")
        self.spell3 = warriorSpell(self.x, self.y, 25, "R")
    alive = True
    posx = 1
    posy = 1
    x = 405
    y = 440
    cooldown1 = 5*fps
    cooldown2 = 10*fps
    cooldown3 = 15*fps
    cooldowntime1 = 5*fps
    cooldowntime2 = 10*fps
    cooldowntime3 = 15*fps
    spellId = 0
    attacktype = 0
    warriorBasicProjectileArr = []
    bleedAmount = 0
    
    global animationSpeed
    
    def updatePos(self):
        self.x = gridx[self.posy][self.posx] - self.offsetx
        self.y = gridy[self.posy] - self.offsety

    def slide(self):
        global warriorSlide, warriorSlideCount, moving
        screen.blit(warriorSlide[warriorSlideCount % 2], (self.x, self.y))
        warriorSlideCount += 1
        moving = True
        if warriorSlideCount == 3: # change to modify movement delay
            warriorSlideCount = 0
            moving = False

    def basicAttack(self, attacktype):
        global warriorBasicAttack1, warriorBasicAttack2, warriorBasicAttack3, warriorBasicAttackCount, animationSpeed
        self.attacktype = attacktype
        if attacktype == 1:
            screen.blit(warriorBasicAttack1[warriorBasicAttackCount//animationSpeed], (self.x, self.y))
        elif attacktype == 2:
            screen.blit(warriorBasicAttack2[warriorBasicAttackCount//animationSpeed], (self.x, self.y))
        elif attacktype == 3:
            screen.blit(warriorBasicAttack3[warriorBasicAttackCount//animationSpeed], (self.x, self.y))
        warriorBasicAttackCount += 1
        if warriorBasicAttackCount == 5*animationSpeed:
            warriorBasicAttackCount = 0

    def spellCast(self, spelltype):
        global warriorSpellCast, warriorSpellCastCount, fps
        screen.blit(warriorSpellCast[warriorSpellCastCount//animationSpeed], (self.x, self.y))
        warriorSpellCastCount += 1

        if warriorSpellCastCount == 5*animationSpeed:
            if spelltype == 1:
                self.spell1 = warriorSpell(self.x+50, self.y-25, 25, "Q")
                self.warriorBasicProjectileArr.append(self.spell1)
                self.spell1.animation()
            elif spelltype == 2:
                self.spell2 = warriorSpell(self.x+50, self.y-25, 15, "E")
                self.warriorBasicProjectileArr.append(self.spell2)
                self.spell2.animation()
                if self.health < 80:
                    self.health += 20
                else:
                    self.health = 100
            elif spelltype == 3: # add bleeding effect
                self.spell3 = warriorSpell(self.x+50, self.y-25, 20, "R")
                self.warriorBasicProjectileArr.append(self.spell3)
                self.spell3.animation()

        if warriorSpellCastCount == 8*animationSpeed:
            warriorSpellCastCount = 0
            self.spellId = 0
            if spelltype == 1:
                self.cooldown1 = 0
            elif spelltype == 2:
                self.cooldown2 = 0
            elif spelltype == 3:
                self.cooldown3 = 0

    def get_attacktype(self):
        return self.attacktype
    
    def updateCooldown(self):
        if self.cooldown1 < self.cooldowntime1:
            self.cooldown1 += 1
        if self.cooldown2 < self.cooldowntime2:
            self.cooldown2 += 1
        if self.cooldown3 < self.cooldowntime3:
            self.cooldown3 += 1

    def animation(self, keys):
        global warriorBasicAttackCount
        super().checkBleed()
        if self.alive == True:
            if warriorDieCount != 0:
                self.death()
            elif self.hurtvar[1] != 0:
                self.hurt()
                warriorBasicAttackCount = 0
            elif keys[pygame.K_q] and warriorSpellCastCount == 0 and self.cooldown1 == 5*fps or warriorSpellCastCount != 0 and (self.spellId == 0 or self.spellId) == 1: # spell cast priority
                self.spellCast(1)
                self.spellId = 1
                warriorBasicAttackCount = 0
            elif keys[pygame.K_e] and warriorSpellCastCount == 0 and self.cooldown2 == 10*fps or warriorSpellCastCount != 0 and (self.spellId == 0 or self.spellId) == 2: 
                self.spellCast(2)
                self.spellId = 2
                warriorBasicAttackCount = 0
            elif keys[pygame.K_r] and warriorSpellCastCount == 0 and self.cooldown3 == 15*fps or warriorSpellCastCount != 0 and (self.spellId == 0 or self.spellId) == 3:
                self.spellCast(3)
                self.spellId = 3
                warriorBasicAttackCount = 0
            elif keys[pygame.K_SPACE] and warriorBasicAttackCount == 0: # Basic attack priority
                attacktype = random.randint(1, 3)
                self.basicAttack(attacktype)
            elif warriorBasicAttackCount != 0:
                attacktype = self.get_attacktype()
                self.basicAttack(attacktype)
            elif keys[pygame.K_w] and self.posy > 0 and moving == False: # movement priority
                self.posy -= 1
                self.updatePos()
                self.slide()
            elif keys[pygame.K_s] and self.posy < 2 and moving == False:
                self.posy += 1
                self.updatePos()
                self.slide()
            elif keys[pygame.K_a] and self.posx > 0 and moving == False:
                self.posx -= 1
                self.updatePos()
                self.slide()
            elif keys[pygame.K_d] and self.posx < 2 and moving == False:
                self.posx += 1
                self.updatePos()
                self.slide()
            elif warriorSlideCount != 0:
                self.slide()
            else: # idle priority
                self.idle()

        if warriorBasicAttackCount == 2*animationSpeed: # outside loop so that other updates with higher priority do not disturb
            self.warriorBasicProjectileArr.append(warriorBasicAttack(mainCharacter.x+50, mainCharacter.y+25, 5))
        for projectile in self.warriorBasicProjectileArr:
            projectile.x += 25
            projectile.animation()
            projectile.checkCollision()
            if projectile.alive == False:
                self.warriorBasicProjectileArr.pop(self.warriorBasicProjectileArr.index(projectile))

        if warriorSpell1Count != 0:
            self.spell1.animation()
        if warriorSpell2Count != 0:
            self.spell2.animation()
        if warriorSpell3Count != 0:
            self.spell3.animation()
        for enemy in enemies:
            if enemy.alive == True:
                if enemy.bleedAmount != 0: # vampirism
                    if self.health <= 99.5:
                        self.health += 0.5

class BringerOfDeath(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Bringer of Death"
        self.projectile1 = self.createProjectile(0, 0)
        self.projectile2 = self.createProjectile(0, 0)
        self.projectile3 = self.createProjectile(0, 0)
        self.hitx = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
        ]
        self.idlevar = [bringerOfDeathIdle, bringerOfDeathIdleCount]
        self.attackvar = [bringerofDeathAttack,bringerofDeathAttackCount]
        self.hurtvar = [bringerofDeathHurt, bringerofDeathHurtCount]
        self.deathvar = [bringerofDeathDeath, bringerofDeathDeathCount]
        self.castvar = [bringerofDeathCast, bringerofDeathCastCount]
        self.walkvar = [bringerofDeathWalk, bringerofDeathWalkCount]
        self.offsety = +365
        self.offsetx = +420
        self.intendedx = 1025-self.offsetx
        self.y = gridy[1]-self.offsety
    posx = 1
    posy = 1
    attackCooldown = 90
    attackCooldownInitial = 90
    castCooldown = 300
    alive = False

    def attack(self):
        super().attack()
        self.hitx = [
                [0, 0, 1],
                [0, 1, 1],
                [0, 0, 1]
            ]
        super().display_danger(self.attackvar[1]*50/animationSpeed, 6, 15)

    def updateCooldown(self):
        super().updateCooldown()
        if self.castCooldown > 0 and self.castvar[1] == 0:
            self.castCooldown -= 1
        if self.castCooldown == 0:
            self.hitx = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
            rand1 = (random.randint(0, 2), random.randint(0, 2))
            self.hitx[rand1[0]][rand1[1]] = 1
            rand2 = (random.randint(0, 2), random.randint(0, 2))
            while self.hitx[rand2[0]][rand2[1]] == 1:
                rand2 = (random.randint(0, 2), random.randint(0, 2))
            self.hitx[rand2[0]][rand2[1]] = 1
            rand3 = (random.randint(0, 2), random.randint(0, 2))
            while self.hitx[rand3[0]][rand3[1]] == 1:
                rand3 = (random.randint(0, 2), random.randint(0, 2))
            self.hitx[rand3[0]][rand3[1]] = 1
            self.projectile1.x = gridx[rand1[0]][rand1[1]]-260
            self.projectile2.x = gridx[rand2[0]][rand2[1]]-260
            self.projectile3.x = gridx[rand3[0]][rand3[1]]-260
            self.projectile1.y = gridy[rand1[0]]-355
            self.projectile2.y = gridy[rand2[0]]-355
            self.projectile3.y = gridy[rand3[0]]-355
            self.cast()
            self.castCooldown = 300
            self.attackCooldown = 90 # doesnt attack directly after spell

    def createProjectile(self, x, y):
        return bringerOfDeathSpell(x, y, 10)

    def animation(self):
        super().checkBleed()
        self.attackable = False
        if self.x > self.intendedx:
            self.walk()
        elif self.x < self.intendedx:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.castvar[1] != 0:
            self.cast()
        elif self.attackvar[1] != 0:
            self.attack()
        elif self.hurtvar[1] != 0: # lower priority, attacking gives invincibility frames
            self.hurt()
        else:
            self.attackable = True # enemies only attackable when they are not doing any other animation
            self.idle()

        if self.castvar[1] == 5*animationSpeed:
            self.projectile1.animation()
        if self.projectile1.bringerofDeathSpellCount != 0:
            self.projectile1.animation()
        if self.castvar[1] == 7*animationSpeed:
            self.projectile2.animation()
        if self.projectile2.bringerofDeathSpellCount != 0:
            self.projectile2.animation()
        if self.castvar[1] == 9*animationSpeed-1:
            self.projectile3.animation()
        if self.projectile3.bringerofDeathSpellCount != 0:
            self.projectile3.animation()
        if self.projectile1.hit == True or self.projectile2.hit == True  or self.projectile3.hit == True:
            self.projectile1.hit = True
            self.projectile2.hit = True
            self.projectile3.hit = True
        if self.projectile3.bringerofDeathSpellCount == 7*animationSpeed+1:
            self.projectile1.hit = False
            self.projectile2.hit = False
            self.projectile3.hit = False

class LightBandit(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Bandit"
        self.idlevar = [lightBanditIdle, lightBanditIdleCount]
        self.attackvar = [lightBanditAttack, lightBanditAttackCount]
        self.hurtvar = [lightBanditHurt, lightBanditHurtCount]
        self.deathvar = [lightBanditDeath, lightBanditDeathCount]
        self.walkvar = [lightBanditWalk, lightBanditWalkCount]
        self.offsetx = 72
        self.offsety = 144
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]+10-self.offsetx
    attackCooldown = 45
    attackCooldownInitial = 45
    alive = False
    attackx = 0
    attacky = 0

    def attack(self):
        super().attack()
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
        self.hitx[self.attacky][self.attackx] = 1 # attacks random square
        super().display_danger(self.attackvar[1]*50/animationSpeed, 4, 5)
        

class HeavyBandit(LightBandit):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Heavy Bandit"
        self.idlevar = [heavyBanditIdle, heavyBanditIdleCount]
        self.attackvar = [heavyBanditAttack, heavyBanditAttackCount]
        self.hurtvar = [heavyBanditHurt, heavyBanditHurtCount]
        self.deathvar = [heavyBanditDeath, heavyBanditDeathCount]
        self.walkvar = [heavyBanditWalk, heavyBanditWalkCount]
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][2]-self.offsetx
    attackCooldown = 60
    attackCooldownInitial = 60

class CultistPriest(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Cultist Priest"
        self.idlevar = [cultistPriestIdle, cultistPriestIdleCount]
        self.attackvar = [cultistPriestAttack, cultistPriestAttackCount]
        self.hurtvar = [cultistPriestHurt, cultistPriestHurtCount]
        self.deathvar = [cultistPriestDeath, cultistPriestDeathCount]
        self.walkvar = [culristPriestWalk, culristPriestWalkCount] 
        self.offsetx = 200
        self.offsety = 360
        self.attackCooldown = 120
        self.attackCooldownInitial = 120
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]-self.offsetx
    attackx = 0
    attacky = 0

    def attack(self):
        screen.blit(self.attackvar[0][self.attackvar[1]//(animationSpeed*2) % len(self.attackvar[0])], (self.x, self.y)) 
        self.attackvar[1] += 1
        if self.attackvar[1] == len(self.attackvar[0])*animationSpeed*2:
            self.attackvar[1] = 0
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
            while self.attacky == self.attackx:
                self.attacky = random.randint(0, 2)
        for i in range (3):
            self.hitx[i][self.attackx] = 1
            self.hitx[i][self.attacky] = 1
        super().display_danger(self.attackvar[1]*50/animationSpeed, 6, 20)

class MedievalKing(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Medieval King"
        self.idlevar = [medievalKingIdle, medievalKingIdleCount]
        self.attackvar1 = [medievalKingAttack1, medievalKingAttack1Count]
        self.attackvar2 = [medievalKingAttack2, medievalKingAttack2Count]
        self.attackvar3 = [medievalKingAttack3, medievalKingAttack3Count]
        self.hurtvar = [medievalKingHurt, medievalKingHurtCount]
        self.deathvar = [medievalKingDeath, medievalKingDeathCount]
        self.walkvar = [medievalKingWalk, medievalKingWalkCount]
        self.offsety = 310
        self.offsetx = 230
        self.attackCooldown = 60
        self.attackCooldownInitial = 60
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]-self.offsetx
        self.attacks = [self.attackvar1, self.attackvar2, self.attackvar3]
        self.attacktype = self.attacks[random.randint(0, 2)]
    attackx = 0
    attacky = 0

    def updateCooldown(self):
        if self.attackCooldown > 0 and self.attacktype[1] == 0 and self.walking == False:
            self.attackCooldown -= 1
        if self.attackCooldown == 0:
            self.attacktype = self.attacks[random.randint(0, 2)]
            self.attack(self.attacktype)
            self.attackCooldown = self.attackCooldownInitial

    def attack(self, attacktype):
        screen.blit(attacktype[0][attacktype[1]//(animationSpeed*2) % len(attacktype[0])], (self.x, self.y)) 
        attacktype[1] += 1
        if attacktype[1] == len(attacktype[0])*animationSpeed*2:
            attacktype[1] = 0
            self.attackCooldown = self.attackCooldownInitial

        if attacktype[1] >= 1:
            if attacktype == self.attackvar1 or attacktype == self.attackvar2:
                self.hitx = [
                    [0, 1, 1],
                    [0, 1, 1],
                    [0, 1, 1]
                ]
            elif attacktype == self.attackvar3:
                self.hitx = [
                    [0, 0, 1],
                    [1, 1, 1],
                    [0, 0, 1]
                ]
        for i in range (3):
            for j in range (3):
                if self.hitx[i][j] == 1:
                    alpha = attacktype[1]*50/animationSpeed
                    if attacktype[1] >= 3*animationSpeed*2:
                        alpha = 0
                        if attacktype[1] == 3*animationSpeed*2 and mainCharacter.posx == j and mainCharacter.posy == i:
                            mainCharacter.hurt()
                            mainCharacter.health -= (20*(1-(mainCharacter.defence/100)))
                    if alpha >= 255:
                        alpha = 255
                    shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                    pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                    screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
        self.hitx = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

    def animation(self):
        super().checkBleed()
        self.attackable = False
        if self.x > self.intendedx:
            self.walk()
        elif self.x < self.intendedx:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.attacktype[1] != 0:
            self.attack(self.attacktype)
        elif self.hurtvar[1] != 0:
            self.hurt()
        else:
            self.attackable = True
            self.idle()

class EvilWizard(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Evil Wizard"
        self.idlevar = [evilWizardIdle, evilWizardIdleCount]
        self.attackvar1 = [evilWizardAttack1, evilWizardAttackCount]
        self.attackvar2 = [evilWizardAttack2, evilWizardAttackCount]
        self.hurtvar = [evilWizardHurt, evilWizardHurtCount]
        self.deathvar = [evilWizardDeath, evilWizardDeathCount]
        self.walkvar = [evilWizardWalk, evilWizardWalkCount]
        self.offsety = 160*evilWizardScale
        self.offsetx = 125*evilWizardScale
        self.attackCooldown = 60
        self.attackCooldownInitial = 60
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]-self.offsetx
        self.attacks = [self.attackvar1, self.attackvar2]
        self.attacktype = self.attacks[random.randint(0, 1)]
        self.projectile = evilWizardAttack(self.intendedx+20, self.y+self.offsety/2-60, 20)

    def updateCooldown(self):
        if self.attackCooldown > 0 and self.attacktype[1] == 0 and self.walking == False:
            self.attackCooldown -= 1
        if self.attackCooldown == 0:
            self.attacktype = self.attacks[random.randint(0, 1)]
            self.attack(self.attacktype)
            self.attackCooldown = self.attackCooldownInitial

    def attack(self, attacktype):
        screen.blit(attacktype[0][attacktype[1]//(animationSpeed) % len(attacktype[0])], (self.x, self.y)) 
        attacktype[1] += 1
        if attacktype[1] == len(attacktype[0])*animationSpeed:
            attacktype[1] = 0
            self.attackCooldown = self.attackCooldownInitial

    def animation(self):
        super().checkBleed()
        self.attackable = False
        if self.x > self.intendedx:
            self.walk()
        elif self.x < self.intendedx:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.attacktype[1] != 0:
            self.attack(self.attacktype)
        elif self.hurtvar[1] != 0:
            self.hurt()
        else:
            self.attackable = True
            self.idle()

        if self.attacktype[1] == 5*animationSpeed:
            self.projectile = evilWizardAttack(self.intendedx+20, self.y+self.offsety/2, 10)
            self.projectile.hit = False
            self.projectile.animation()
        if self.projectile.evilWizardSpellCount != 0:
            self.projectile.animation()
        if mainCharacter.bleedAmount != 0: # vampirism
            if self.health <= 149.5:
                self.health += 0.5

class WindHashashin(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Wind Hashashin"
        self.idlevar = [windHashashinIdle, windHashashinIdleCount]
        self.attackvar1 = [windHashashinAttack1, windHashashinAttack1Count]
        self.attackvar2 = [windHashashinAttack2, windHashashinAttack2Count]
        self.attackvar3 = [windHashashinAttack3, windHashashinAttack3Count]
        self.attackvar4 = [windHashashinAttack4, windHashashinAttack4Count]
        self.hurtvar = [windHashashinHurt, windHashashinHurtCount]
        self.deathvar = [windHashashinDeath, windHashashinDeathCount]
        self.walkvar = [windHashashinWalk, windHashashinWalkCount]
        self.offsety = 128*windHashashinScale
        self.offsetx = 144*windHashashinScale-20
        self.attackCooldown = 60
        self.attackCooldownInitial = 60
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]-self.offsetx
        self.attacks = [self.attackvar1, self.attackvar2, self.attackvar3, self.attackvar4]
        self.attacknum = -1
        self.attacktype = self.attacks[self.attacknum]
    attackx = 0 
    attacky = 0

    def updateCooldown(self):
        if self.attackCooldown > 0 and self.attacktype[1] == 0 and self.walking == False:
            self.attackCooldown -= 1
        if self.attackCooldown == 0:
            self.attacknum += 1
            self.attacktype = self.attacks[self.attacknum % 4]
            self.attack(self.attacktype)
            self.attackCooldown = self.attackCooldownInitial

    def attack(self, attacktype):
        screen.blit(attacktype[0][attacktype[1]//(animationSpeed) % len(attacktype[0])], (self.x, self.y)) 
        if attacktype != self.attackvar4 and attacktype[1] <= 4*animationSpeed:
            if attacktype[1] == 0 or attacktype[1] == animationSpeed+1:
                self.attackx = random.randint(0, 2)
                for i in range (3):
                    self.hitx[i][self.attackx] = 1
            if attacktype[1] == animationSpeed or attacktype[1] == 4*animationSpeed:
                self.hitx = [
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]
                ]
            for i in range (3):
                for j in range (3):
                    if self.hitx[i][j] == 1:
                        alpha = 255
                        if attacktype[1] != 0:
                            alpha = self.attacktype[1]*100/animationSpeed
                        if (attacktype[1] == 0 or attacktype[1] == 2*animationSpeed) and mainCharacter.posx == j and mainCharacter.posy == i:
                            mainCharacter.hurt()
                            if attacktype[1] == 0: # first stike, impossible to dodge
                                mainCharacter.health -= (5*(1-(mainCharacter.defence/100)))
                            else:
                                mainCharacter.health -= (10*(1-(mainCharacter.defence/100)))
                        if alpha >= 255:
                            alpha = 255
                        shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                        pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                        screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))

        if attacktype != self.attackvar1 and attacktype != self.attackvar4 and attacktype[1] > 4*animationSpeed:
            # 8, 9, 10, 11
            if attacktype[1] == 7*animationSpeed or attacktype[1] == 8*animationSpeed or attacktype[1] == 9*animationSpeed or attacktype[1] == 10*animationSpeed:
                self.attackx = random.randint(0, 2)
                self.attacky = random.randint(0, 2)
            if attacktype[1] < 11*animationSpeed:    
                self.hitx[self.attacky][self.attackx] = 1
            if attacktype[1] >= 10*animationSpeed and attacktype[1] <= 11*animationSpeed and attacktype == self.attackvar2:
                self.hitx = [
                    [0, 1, 0],
                    [1, 1, 1],
                    [0, 1, 0]
                ]
            for i in range (3):
                for j in range (3):
                    if self.hitx[i][j] == 1:
                        alpha = 255
                        if attacktype[1] > 12*animationSpeed:
                            alpha = 0
                        if (attacktype[1] == 7*animationSpeed or attacktype[1] == 8*animationSpeed or attacktype[1] == 9*animationSpeed or attacktype[1] == 10*animationSpeed or attacktype[1] == 11*animationSpeed) and mainCharacter.posx == j and mainCharacter.posy == i:
                            mainCharacter.hurt()
                            if attacktype[1] == 7*animationSpeed or attacktype[1] == 8*animationSpeed or attacktype[1] == 9*animationSpeed or attacktype[1] == 10*animationSpeed: # barrage, really hard to dodge
                                mainCharacter.health -= (5*(1-(mainCharacter.defence/100)))
                            else:
                                mainCharacter.health -= (10*(1-(mainCharacter.defence/100)))
                        shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                        pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                        screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
            self.hitx = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]

        if attacktype == self.attackvar3 and attacktype[1] > 12*animationSpeed:
            self.hitx = [
                [0, 0, 1], 
                [0, 0, 1],
                [0, 0, 1]
            ]
            for i in range (3):
                for j in range (3):
                    if self.hitx[i][j] == 1:
                        alpha = (attacktype[1]-15*animationSpeed)*50/animationSpeed
                        if alpha < 0:
                            alpha = 0
                        if attacktype[1] >= 21*animationSpeed:
                            alpha = 0
                            if attacktype[1] == 21*animationSpeed and mainCharacter.posx == j and mainCharacter.posy == i:
                                mainCharacter.hurt()
                                mainCharacter.health -= (20*(1-(mainCharacter.defence/100)))
                        if alpha >= 255:
                            alpha = 255
                        shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                        pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                        screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
            self.hitx = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
        if attacktype == self.attackvar4 and attacktype[1] > 8*animationSpeed:
            self.x = 483-self.offsetx
            # 12 , cross -- 18, line -- 20, line
            if attacktype[1] >= 7*animationSpeed and attacktype[1] <= 11*animationSpeed:
                self.hitx = [
                    [0, 1, 0],
                    [1, 1, 1],
                    [0, 1, 0]
                ] 
            elif attacktype[1] >= 15*animationSpeed and attacktype[1] <= 19*animationSpeed:
                if attacktype[1] == 15*animationSpeed or attacktype[1] == 17*animationSpeed:
                    self.attackx = gridy.index(mainCharacter.y + mainCharacter.offsety) # homes on character
                for i in range(3):
                    self.hitx[self.attackx][i] = 1
                    self.y = gridy[self.attackx] - self.offsety 

            if attacktype[1] == 26*animationSpeed:
                self.y = gridy[1] - self.offsety

            for i in range (3):
                for j in range (3):
                    if self.hitx[i][j] == 1:
                        alpha = (attacktype[1]-7*animationSpeed)*50/animationSpeed
                        if alpha < 0:
                            alpha = 0
                        if attacktype[1] >= 21*animationSpeed:
                            alpha = 0
                        if (attacktype[1] == 11*animationSpeed or attacktype[1] == 17*animationSpeed or attacktype[1] == 19*animationSpeed) and mainCharacter.posx == j and mainCharacter.posy == i:
                            mainCharacter.hurt()
                            mainCharacter.health -= (15*(1-(mainCharacter.defence/100)))
                        if alpha >= 255:
                            alpha = 255
                        shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                        pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                        screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
            self.hitx = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]

        attacktype[1] += 1
        if attacktype[1] == len(attacktype[0])*animationSpeed:
            attacktype[1] = 0
            self.attackCooldown = self.attackCooldownInitial
            self.hitx = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
            ]

    def animation(self):
        super().checkBleed()
        self.attackable = False
        if self.x > self.intendedx:
            self.walk()
        elif self.x < self.intendedx and self.attackvar4[1] == 0:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.attacktype[1] != 0:
            self.attack(self.attacktype)
        elif self.hurtvar[1] != 0:
            self.hurt()
        else:
            self.attackable = True
            self.idle()

class NightBorne(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Night Borne"
        self.idlevar = [nightBorneIdle, nightBorneIdleCount]
        self.attackvar = [nightBorneAttack, nightBorneAttackCount]
        self.hurtvar = [nightBorneHurt, nightBorneHurtCount]
        self.deathvar = [nightBorneDeath, nightBorneDeathCount]
        self.walkvar = [nightBorneWalk, nightBorneWalkCount]
        self.offsetx = 40*nightBorneScale
        self.offsety = 60*nightBorneScale
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][0]+10-self.offsetx
    attackCooldown = 30
    attackCooldownInitial = 30
    alive = False
    attacky = 0

    def attack(self):
        super().attack()
        if self.attackvar[1] == 1:
            self.y = mainCharacter.y + mainCharacter.offsety - self.offsety
            self.x = WIDTH-gridx[gridy.index(self.y+self.offsety)][0]+10 - self.offsetx
        for i in range (3):
            self.hitx[gridy.index(self.y+self.offsety)][i] = 1 
        super().display_danger(self.attackvar[1]*50/animationSpeed, 9, 25)

class Skeleton(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Skeleton"
        self.idlevar = [skeletonIdle, skeletonIdleCount]
        self.attackvar = [skeletonAttack, skeletonAttackCount]
        self.hurtvar = [skeletonHurt, skeletonHurtCount]
        self.deathvar = [skeletonDeath, skeletonHurtCount]
        self.walkvar = [skeletonWalk, skeletonWalkCount]
        self.offsetx = 75*skeletonScale
        self.offsety = 100*skeletonScale
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][2]+10-self.offsetx
    attackCooldown = 45
    attackCooldownInitial = 45
    alive = False
    attackx = 0
    attacky = 0

    def attack(self):
        super().attack()
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
        self.hitx[self.attacky][self.attackx] = 1
        super().display_danger(self.attackvar[1]*50/animationSpeed, 6, 5)

class SkeletonMinion(Skeleton):
    def __init__(self, health, defence, x, y, intendedx):
        super().__init__(health, defence, x, y)
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][intendedx]+10-self.offsetx

class Mushroom(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Mushroom"
        self.idlevar = [mushroomIdle, mushroomIdleCount]
        self.attackvar = [mushroomAttack, mushroomAttackCount]
        self.hurtvar = [mushroomHurt, mushroomHurtCount]
        self.deathvar = [mushroomDeath, mushroomDeathCount]
        self.walkvar = [mushroomWalk, mushroomWalkCount]
        self.offsetx = 75*mushroomScale
        self.offsety = 100*mushroomScale
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][2]+10-self.offsetx
    attackCooldown = 45
    attackCooldownInitial = 45
    alive = False
    attackx = 0
    attacky = 0

    def attack(self):
        super().attack()
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
        self.hitx[self.attacky][self.attackx] = 1 # attacks random square
        self.hit = False
        super().display_danger(self.attackvar[1]*50/animationSpeed, 6, 5)
        if self.hit == True:
            mainCharacter.bleedAmount = 5

class FlyingEye(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Flying Eye"
        self.idlevar = [flyingEyeFly, flyingEyeFlyCount]
        self.attackvar = [flyingEyeAttack, flyingEyeAttackCount]
        self.hurtvar = [flyingEyeHurt, flyingEyeHurtCount]
        self.deathvar = [flyingEyeDeath, flyingEyeDeathCount]
        self.walkvar = [flyingEyeFly, flyingEyeFlyCount]
        self.offsetx = 75*flyingEyeScale
        self.offsety = 100*flyingEyeScale
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][2]+10-self.offsetx

    attackCooldown = 45
    attackCooldownInitial = 45
    alive = False
    attackx = 0
    attacky = 0

    def attack(self):
        super().attack()
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
        self.hitx[self.attacky][self.attackx] = 1 # attacks random square
        self.hit = False
        super().display_danger(self.attackvar[1]*50/animationSpeed, 6, 5)
        if self.hit == True:
            if self.health >= 95:
                self.health = 100
            else:
                self.health += 5

class Necromancer(Character):
    def __init__(self, health, defence, x, y):
        super().__init__(health, defence, x, y)
        self.name = "Necromancer"
        self.idlevar = [necromancerIdle, necromancerIdleCount]
        self.attackvar = [necromancerAttack, necromancerAttackCount]
        self.castvar = [necromancerCast, necromancerCastCount]
        self.hurtvar = [necromancerHurt, necromancerHurtCount]
        self.deathvar = [necromancerDeath, necromancerDeathCount]
        self.walkvar = [necromancerWalk, necromancerWalkCount]
        self.offsetx = 64*necromancerScale
        self.offsety = 80*necromancerScale
        self.intendedx = WIDTH-gridx[gridy.index(self.y+self.offsety)][1]+10-self.offsetx
    attackCooldown = 90
    attackCooldownInitial = 90
    castCooldown = 90
    
    alive = False
    attackx = 0
    attacky = 0
    animationSpeed = 1

    def attack(self):
        screen.blit(self.attackvar[0][self.attackvar[1]//animationSpeed % len(self.attackvar[0])], (self.x-60, self.y-60)) 
        self.attackvar[1] += 1
        if self.attackvar[1] == len(self.attackvar[0])*animationSpeed:
            self.attackvar[1] = 0
        if self.attackvar[1] == 1:
            self.attackx = random.randint(0, 2)
            self.attacky = random.randint(0, 2)
        self.hitx[self.attacky][self.attackx] = 1
        super().display_danger(50*(self.attackvar[1]-32*animationSpeed), 38, 5)

    def cast(self):
        screen.blit(self.castvar[0][self.castvar[1]//animationSpeed % len(self.castvar[0])], (self.x-60, self.y-60)) 
        self.castvar[1] += 1
        if self.castvar[1] == len(self.castvar[0])*animationSpeed:
            self.castvar[1] = 0
        if self.castvar[1] == 9*animationSpeed:
            if score < 10:
                index = [5, 6, 7, 14, 19, 20, 21]
            else:
                index = [5, 6, 14, 19, 20]
            minion = random.randint(0, len(index)-1)
            flag = 0
            while enemies[index[minion]].alive == True:
                minion = random.randint(0, len(index)-1)
                flag += 1
                if flag == 10:
                    break
            if enemies[index[minion]].alive == False:
                enemies[index[minion]].alive = True
                enemies[index[minion]].alive.__init__(50, 10, WIDTH, gridy[gridcoords[i][1]]-100*skeletonScale, gridcoords[i][0]*-1+2)
                enemies[index[minion]].x = WIDTH
                enemies[index[minion]].health = 50

    def updateCooldown(self):
        super().updateCooldown()
        if self.castCooldown > 0 and self.castvar[1] == 0 and self.attackvar[1] == 0:
            self.castCooldown -= 1
        if self.castCooldown == 0:
            indeces = [5, 6, 7, 14, 19, 20, 21]
            spawn = False
            for i in range (7):
                if enemies[indeces[i]].alive == False:
                    spawn = True
            if spawn == True:
                self.cast()
                self.castCooldown = 90
                self.attackCooldown = 90 # doesnt attack directly after spell
            else:
                self.castCooldown = 90
        

    def animation(self):
        super().checkBleed()
        self.attackable = False
        if self.x > self.intendedx:
            self.walk()
        elif self.x < self.intendedx:
            self.x = self.intendedx
        elif self.walking == True and self.x == self.intendedx:
            self.walking = False
        elif self.health < 0:
            self.health = 0
            self.death()
        elif self.deathvar[1] != 0 or self.health == 0:
            self.death()
        elif self.castvar[1] != 0:
            self.cast()
        elif self.attackvar[1] != 0:
            self.attack()
        elif self.hurtvar[1] != 0: # lower priority, attacking gives invincibility frames
            self.hurt()
        else:
            self.attackable = True # enemies only attackable when they are not doing any other animation
            self.idle()
            

class Projectile():
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.dangerArea = [
            [
            ((380, 500),(475,500),(450, 530),(350, 530)), # top left
            ((475,500),(570, 500),(550, 530),(450, 530)), # top middle
            ((570, 500),(660, 500),(650, 530),(550, 530)) # top right
            ],
            [
            ((350, 530),(450, 530),(415, 575),(300, 575)), # middle left
            ((450, 530),(550, 530),(530, 575),(420, 575)), # middle 
            ((550, 530),(650, 530),(640, 575),(530, 575)) # middle right
            ],
            [
            ((300, 575),(415, 575),(375, 630),(240, 630)), # bottom left
            ((415, 575),(530, 575),(500, 630),(370, 630)), # bottom middle
            ((530, 575),(640, 575),(630, 630),(500, 630)) # bottom right
            ]
        ]
        self.alive = True

class warriorBasicAttack(Projectile):
    warriorBasicProjectileCount = 0
    def __init__(self, x, y, damage):
        super().__init__(x, y, damage)
        self.warriorBasicProjectileCount = warriorBasicProjectileCount

    def animation(self):
        global warriorBasicProjectile, animationSpeed
        basicProjectileLoop = [0, 1, 2, 3, 4, 3, 2, 1]
        screen.blit(warriorBasicProjectile[basicProjectileLoop[self.warriorBasicProjectileCount//animationSpeed % 8]], (self.x, self.y))
        self.warriorBasicProjectileCount += 1

    def checkCollision(self): # offset (+50, +25), (-75, -105)
        if self.x > 750:
            for enemy in enemies:
                if enemy.alive:
                    if self.y-25+mainCharacter.offsety == enemy.y+enemy.offsety and self.x+25 > enemy.x+enemy.offsetx-50 and self.x+25 < enemy.x+enemy.offsetx+50 and enemy.attackable == True:
                        enemy.health -= (self.damage*(1-(enemy.defence/100))) # include enemy defence
                        enemy.hurt()
                        self.alive = False
            if self.x > WIDTH-75: # delete projectile when crossing right side of screen
                self.alive = False

class warriorSpell(Projectile):
    def __init__(self, x, y, damage, id):
        super().__init__(x, y, damage)
        self.id = id
        self.acceleration = 0
        self.velocity = 0
    
    def animation(self):
        global warriorSpell1, warriorSpell2, warriorSpell3, warriorSpell1Count, warriorSpell2Count, warriorSpell3Count
        self.acceleration += 0.1
        self.velocity += 0.1 + self.acceleration
        self.x += self.velocity
        if self.id == "Q":
            screen.blit(warriorSpell1[warriorSpell1Count//(2*animationSpeed)], (self.x, self.y))
            if warriorSpell1Count < animationSpeed*10-1:
                warriorSpell1Count += 1
            else:
                warriorSpell1Count -= animationSpeed*4-1
        if self.id == "E":
            screen.blit(warriorSpell2[warriorSpell2Count//(2*animationSpeed)], (self.x, self.y))
            if warriorSpell2Count < animationSpeed*10-1:
                warriorSpell2Count += 1
            else:
                warriorSpell2Count -= animationSpeed*4-1
        if self.id == "R":
            screen.blit(warriorSpell3[warriorSpell3Count//(2*animationSpeed)], (self.x, self.y))
            if warriorSpell3Count < animationSpeed*10-1:
                warriorSpell3Count += 1
            else:
                warriorSpell3Count -= animationSpeed*4-1

    def checkCollision(self):
        global warriorSpell1Count, warriorSpell2Count, warriorSpell3Count
        if self.x > 750:
            for enemy in enemies:
                if enemy.alive:
                    if self.y+25+mainCharacter.offsety == enemy.y+enemy.offsety and self.x+25 > enemy.x+enemy.offsetx-50 and self.x+25 < enemy.x+enemy.offsetx+50:
                        enemy.health -= (self.damage*(1-(enemy.defence/100))) # include enemy defence
                        if enemy.attackable == True:
                            enemy.hurt()
                        self.alive = False
                        if self.id == "Q":
                            warriorSpell1Count = 0
                        if self.id == "E":
                            warriorSpell2Count = 0
                        if self.id == "R":
                            warriorSpell3Count = 0
                            enemy.bleedAmount = 20
            if self.x > WIDTH-75: # delete projectile when crossing right side of screen
                self.alive = False
                if self.id == "Q":
                    warriorSpell1Count = 0
                if self.id == "E":
                    warriorSpell2Count = 0
                if self.id == "R":
                    warriorSpell3Count = 0

class bringerOfDeathSpell(Projectile):
    def __init__(self, x, y, damage):
        super().__init__(x, y, damage)
        self.bringerofDeathSpellCount = 0
        self.hit = False

    def animation(self):
        global bringerofDeathSpell
        screen.blit(bringerofDeathSpell[self.bringerofDeathSpellCount//animationSpeed % 16], (self.x, self.y))
        self.bringerofDeathSpellCount += 1
        if self.bringerofDeathSpellCount == 16*animationSpeed:
            self.bringerofDeathSpellCount = 0
            self.hit = False
        self.showDanger()

    def showDanger(self):
        for i in range (3):
            for j in range (3):
                if bringerofdeath.hitx[i][j] == 1:
                    alpha = self.bringerofDeathSpellCount*16/animationSpeed
                    if self.bringerofDeathSpellCount >= 7*animationSpeed:
                        alpha = 0
                        if self.bringerofDeathSpellCount == 7*animationSpeed and mainCharacter.posx == j and mainCharacter.posy == i and self.hit == False:
                            mainCharacter.hurt() # damage taken
                            mainCharacter.health -= (self.damage-mainCharacter.defence)
                            self.hit = True
                    if alpha >= 255:
                        alpha = 255
                    shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                    pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                    screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))

class evilWizardAttack(Projectile):
    def __init__(self, x, y, damage):
        super().__init__(x, y, damage)
        self.evilWizardSpellCount = 0
        self.hit = False
        self.acceleration = 0
        self.velocity = 0

    def animation(self):
        self.acceleration -= 0.05
        self.velocity -= 0.1 - self.acceleration
        self.x += self.velocity
        screen.blit(evilWizardSpell[self.evilWizardSpellCount//(animationSpeed*3) % 5], (self.x, self.y))
        self.evilWizardSpellCount += 1
        if self.evilWizardSpellCount < animationSpeed*5*3-1:
            self.evilWizardSpellCount += 1
        else:
            self.evilWizardSpellCount -= animationSpeed*3-1
        evilwizard.hitx = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        self.showDanger()

    def showDanger(self):
        for i in range (3):
            for j in range (3):
                if evilwizard.hitx[i][j] == 1:
                    alpha = 255-(self.x-gridx[i][j])
                    if alpha < 0:
                        alpha = 0
                    if self.x <= gridx[i][j]:
                        alpha = 0
                        if self.x >= gridx[i][j] - 50 and self.x <= gridx[i][j] + 50 and mainCharacter.posx == j and mainCharacter.posy == i and self.hit == False:
                            mainCharacter.hurt()
                            mainCharacter.health -= self.damage*(1-mainCharacter.defence/100) # Change defence
                            self.hit = True
                            evilwizard.projectile.evilWizardSpellCount = 0
                            mainCharacter.bleedAmount = 20
                    shape_surf = pygame.Surface(pygame.Rect(0, 0, WIDTH, HEIGHT).size, pygame.SRCALPHA)
                    pygame.draw.polygon(shape_surf, (255, 0, 0, alpha), self.dangerArea[i][j], 5)
                    screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))

def main():
    global screen, clock, running, dt, background, weightedindex, originalweightedindex
    while running:
        pygame.display.set_caption("Medieval Battle " + str(round(clock.get_fps())) + "fps")
        screen.fill("#0e1111")
        screen.blit(background, (0, 0))
        keys = pygame.key.get_pressed()
        drawBackground()
        updateSprites(keys)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                print(pygame.mouse.get_pos())
        
        spawn = True
        for enemy in enemies:
            if enemy.alive == True:
                spawn = False
        # spawn = False
        if spawn == True and mainCharacter.health > 0:
            global score
            score += 1
            if mainCharacter.health < 90:
                mainCharacter.health += 10  
            else:
                mainCharacter.health = 100
            
            # no repeated enemies for every list
            randomindex = random.randint(0, len(weightedindex)-1)
            enemyindex = weightedindex[randomindex]
            if len(weightedindex) == 1:
                weightedindex += originalweightedindex
                weightedindex.pop(weightedindex.index(weightedindex[randomindex]))
            else:
                weightedindex.pop(weightedindex.index(weightedindex[randomindex]))

            enemies[enemyindex].alive = True
            enemies[enemyindex].__init__(enemieshealth[enemyindex], enemiesdefence[enemyindex], enemiesx[enemyindex], enemiesy[enemyindex])
            
            if enemyindex != 13:
                minions = random.randint(0, 1) # selects minions of enemy
                if minions == 0:
                    lightbandit1.alive = True
                    lightbandit2.alive = True
                    heavybandit.alive = True
                    lightbandit1.__init__(100, 20, WIDTH, 515-lightbandit1.offsety)
                    lightbandit2.__init__(100, 20, WIDTH, 603-lightbandit2.offsety)
                    heavybandit.__init__(100, 40, WIDTH, 553-heavybandit.offsety)
                else:
                    possibleenemies = [
                        [mushroom1, mushroom2],
                        [flyingeye1, flyingeye2]
                    ]
                    skeleton.alive = True
                    skeleton.__init__(100, 15, WIDTH-skeleton.offsetx+100, 553-skeleton.offsety)
                    for i in range(2):
                        lineup = random.randint(0, 1)
                        possibleenemies[lineup][i].alive = True
                        statsindex = enemies.index(possibleenemies[lineup][i])
                        possibleenemies[lineup][i].__init__(enemieshealth[statsindex], enemiesdefence[statsindex], enemiesx[statsindex], enemiesy[statsindex])
            if score >= 10: # extra enemy, makes the game harder
                nightborne.alive = True
                nightborne.__init__(150, 5, WIDTH-nightborne.offsetx+500, 553-nightborne.offsety)
            if score >= 15:
                if mainCharacter.hurtvar[1] == 1:
                    mainCharacter.health -= score-14 # increasing damage taken

        # command buttons to test game
        if keys[pygame.K_b]: # suicide button
            mainCharacter.health = 0
        if keys[pygame.K_m]: # kill button
            for enemy in enemies:
                if enemy.alive == True:
                    enemy.health = 0
        if keys[pygame.K_n]: # add score button
            score += 1
        if keys[pygame.K_v]: # max health
            mainCharacter.health = 100


        if mainCharacter.health <= 0:
            mainCharacter.health = 0
            mainCharacter.alive = False
            for enemy in enemies:
                if enemy.alive == True:
                    enemy.health = 0
            play_again(keys)

        pygame.display.flip()
        dt = clock.tick(fps)/1000     

def play_again(keys):
    global score, running
    shape_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, (20, 20, 20, 150), shape_surf.get_rect())
    screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))

    textRect = font.render("Game Over!", True, "#ffffff").get_rect()
    textRect.center = (WIDTH/2, HEIGHT/3)
    screen.blit(font.render("Game Over!", True, "#ffffff"), textRect)

    textRect = font2.render(f"Your Score: {score}", True, "#ffffff").get_rect()
    textRect.center = (WIDTH/2, HEIGHT*2/3)
    screen.blit(font2.render(f"Your Score: {score}", True, "#ffffff"), textRect)

    textRect = font2.render("Press Space to Play Again", True, "#ffffff").get_rect()
    textRect.center = (WIDTH/2, HEIGHT*5/6)
    screen.blit(font2.render("Press Space to Play Again", True, "#ffffff"), textRect)
        
    if keys[pygame.K_ESCAPE]:
        running = False
    if keys[pygame.K_SPACE]:
        mainCharacter.alive = True
        mainCharacter.health = 100
        score = -1
        mainCharacter.x = 483-75
        mainCharacter.y = 553-105


def drawBackground():
    pygame.draw.polygon(screen, "#91bbff", ((380,500),(660,500),(650,530),(350,530),(300,575),(640,575),(630,630),(245,630),(380,500),(470,500),(370,630),(500,630),(570,500),(660,500),(630,630),(245,630)), 5)
    pygame.draw.polygon(screen, "#ff9191", ((WIDTH-370,500),(WIDTH-650,500),(WIDTH-640,530),(WIDTH-340,530),(WIDTH-290,575),(WIDTH-630,575),(WIDTH-620,630),(WIDTH-235,630),(WIDTH-370,500),(WIDTH-460,500),(WIDTH-360,630),(WIDTH-490,630),(WIDTH-560,500),(WIDTH-650,500),(WIDTH-620,630),(WIDTH-235,630)), 5)

    # Score
    textRect = font2.render(f"{score}", True, "#ffffff").get_rect()
    textRect.center = (WIDTH/2, 10)
    screen.blit(font.render(f"{score}", True, "#ffffff"), (WIDTH/2-20, 10))

    # Health Bars
    pygame.draw.rect(screen, (25, 25, 25), (50, 50, 100*3, 50))
    pygame.draw.rect(screen, (255, 0, 0), (50, 50, mainCharacter.health*3, 50))
    screen.blit(font2.render(f"You {mainCharacter.health}", True, "#ffffff"), (50, 10))
    numenemies = -1
    for enemy in enemies:
        if enemy.alive == True:
            numenemies += 1
            enemy.display_health(numenemies)

def updateSprites(keys):
    global warriorSpellCast, warriorSpellCastCount, warriorSlide, warriorSlideCount, projectile, warriorBasicAttackCount, moving, animationSpeed
    # draw cooldown boxes
    for i in range (3):
        pygame.draw.rect(screen, (0, 0, 0), (620+i*100, 345, 75, 75))

    screen.blit(font.render(f"Q", True, "#ffffff"), (630, 345))
    screen.blit(font.render(f"E", True, "#ffffff"), (735, 345))
    screen.blit(font.render(f"R", True, "#ffffff"), (830, 345))

    cooldown_params = [
    (620, 345, mainCharacter.cooldown1, 2),
    (720, 345, mainCharacter.cooldown2, 4),
    (820, 345, mainCharacter.cooldown3, 6)
    ]

    # Loop through each set of parameters to create, draw, and blit each surface
    for x, y, cooldown, divisor in cooldown_params:
        rect_height = 75 - cooldown / divisor
        rect_y = y + cooldown / divisor
        shape_surf = pygame.Surface((75, rect_height), pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (255, 255, 255, 150), shape_surf.get_rect())
        screen.blit(shape_surf, (x, rect_y, 75, rect_height))

    # Projectile appears behind the enemy when required
    forwardLayer = True
    animated = False
    for projectile in mainCharacter.warriorBasicProjectileArr:
        for enemy in enemies:
            if enemy.alive == True:
                y = enemy.y
        if projectile.y-25-mainCharacter.offsety < y+enemy.offsety and animated == False:
            mainCharacter.animation(keys)
            mainCharacter.updateCooldown()
            forwardLayer = False
            animated = True
    for enemy in enemies:           
        if enemy.alive == True:
            enemy.animation()
            enemy.updateCooldown()
    if forwardLayer == True:
        mainCharacter.animation(keys)                                    
        mainCharacter.updateCooldown()
    
loadSprites()

mainCharacter = Warrior(100, 0, 483-75, 553-105) # defence is % of damage reduced
bringerofdeath = BringerOfDeath(200, 40, 1025-420, 555-365)
lightbandit1 = LightBandit(100, 20, WIDTH, 371)
lightbandit2 = LightBandit(100, 20, WIDTH, 459)
heavybandit = HeavyBandit(100, 40, WIDTH, 409)
cultistpriest = CultistPriest(200, 75, WIDTH, 193)
medievalking = MedievalKing(150, 30, WIDTH, 243)
evilwizard = EvilWizard(150, 20, WIDTH, 553-160*evilWizardScale)
windhashashin = WindHashashin(150, 30, WIDTH-300, 553-128*windHashashinScale)
nightborne = NightBorne(150, -25, WIDTH, 553-60*nightBorneScale)
skeleton = Skeleton(100, 15, WIDTH, 553-100*skeletonScale)
mushroom1 = Mushroom(100, 10, WIDTH, 515-100*mushroomScale)
mushroom2 = Mushroom(100, 10, WIDTH, 603-100*mushroomScale)
flyingeye1 = FlyingEye(100, 5, WIDTH, 515-100*flyingEyeScale)
flyingeye2 = FlyingEye(100, 5, WIDTH, 603-100*flyingEyeScale)
necromancer = Necromancer(150, 0, WIDTH, 553-80*necromancerScale)
enemies = [lightbandit1, nightborne, mushroom1, flyingeye1, skeleton, None, None, None, 
           bringerofdeath, cultistpriest, medievalking, evilwizard, windhashashin, necromancer, None, 
           heavybandit, lightbandit2, mushroom2, flyingeye2, None, None, None]
enemieshealth = [100, 150, 100, 100, 100, 50, 50, 50, 
                 200, 200, 150, 150, 150, 150, 50, 
                 100, 100, 100, 100, 50, 50, 50]
enemiesdefence = [20, -25, 15, 10, 5, 10, 10, 10, 
                  40, 75, 30, 20, 40, 0, 10, 
                  30, 20, 10, 5, 10, 10, 10]
enemiesx = [WIDTH-lightbandit1.offsetx+100, WIDTH-nightborne.offsetx+500, WIDTH-mushroom1.offsetx+100, WIDTH-flyingeye1.offsetx+100, WIDTH-skeleton.offsetx-100, WIDTH, WIDTH, WIDTH, 
            WIDTH-bringerofdeath.offsetx+300, WIDTH-cultistpriest.offsetx+300, WIDTH-medievalking.offsetx+300, WIDTH-evilwizard.offsetx+300, WIDTH-windhashashin.offsetx+300, WIDTH-necromancer.offsetx+300, WIDTH, 
            WIDTH-heavybandit.offsetx+100, WIDTH-lightbandit2.offsetx+100, WIDTH-mushroom2.offsetx+100, WIDTH-flyingeye2.offsetx+100, WIDTH, WIDTH, WIDTH]
enemiesy = [515-lightbandit1.offsety, 553-nightborne.offsety, 515-mushroom1.offsety, 515-flyingeye1.offsety, 553-skeleton.offsety, 553-skeleton.offsety, 553-skeleton.offsety, 553-skeleton.offsety, 
            555-bringerofdeath.offsety, 553-cultistpriest.offsety, 553-medievalking.offsety, 553-evilwizard.offsety, 553-windhashashin.offsety, 553-necromancer.offsety, 553-skeleton.offsety, 
            554-heavybandit.offsety, 603-lightbandit1.offsety, 603-mushroom2.offsety, 603-flyingeye2.offsety, 553-skeleton.offsety, 553-skeleton.offsety, 553-skeleton.offsety]
minions = []
gridcoords = [
    (0, 0), (1, 0), (2, 0),
    (0, 1), (1, 1), (2, 1),
    (0, 2), (1, 2), (2, 2)
    ]
for i in range (9):
    index = [5, 6, 7, 14, 0, 0, 19, 20, 21]
    if i != 4 and i != 5:
        enemies[index[i]] = (SkeletonMinion(50, 10, WIDTH, gridy[gridcoords[i][1]]-100*skeletonScale, gridcoords[i][0]*-1+2))

main()

pygame.quit()