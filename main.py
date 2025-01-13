import discord
import random
import queue
import re
from discord.ext import commands

token = #{your token here}
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)  # 봇의 접두사 설정
charDataFileName = "charDatas.csv"
true = 1
false = 0


class Character:
    def __init__(self, weapon_skill, strength, agility, luck, cover, hp, evade_difficulty):
        self.weapon_skill = weapon_skill
        self.strength = strength
        self.agility = agility
        self.luck = luck
        self.cover = cover
        self.hp = hp
        self.evade_difficulty = evade_difficulty

    def move_toward(self):
        return self.agility / 10

    def melee_damage(self):
        return (self.strength / 20) + self.weapon_skill

    def evade_chance(self, opponent):
        return ((self.agility - opponent.agility) * 3 *
                (self.luck - opponent.luck) / self.evade_difficulty)


class Shooter(Character):
    def __init__(self, weapon_skill, agility, luck, hp, evade_difficulty,
                 proficiency, damage, clip, reload_time, hit_difficulty):
        super().__init__(weapon_skill, 0, agility, luck, 0, hp, evade_difficulty)
        self.proficiency = proficiency
        self.damage = damage
        self.clip = clip
        self.current_ammo = clip
        self.reload_time = reload_time
        self.turns_until_reloaded = 0
        self.hit_difficulty = hit_difficulty

    def hit_chance(self, target):
        difficulty = self.hit_difficulty
        if target.cover != 0:
            difficulty += 2 * self.hit_difficulty
        return self.proficiency / difficulty


class PC:
    def __init__(self, UID, cConstitution, cStrength, cDeterxity,
                 cIntelligence, cWisdom, cLuck, cWeaponRange,
                 cWeaponDamage, cHealthPoint):
        # 인스턴스 변수로 설정 (self를 통해 각 객체에 속성값 할당)
        self.UID = UID
        self.cConstitution = cConstitution
        self.cStrength = cStrength
        self.cDeterxity = cDeterxity  # 인스턴스 변수로 할당
        self.cIntelligence = cIntelligence
        self.cWisdom = cWisdom
        self.cLuck = cLuck
        self.cWeaponRange = cWeaponRange
        self.cWeaponDamage = cWeaponDamage
        self.cHealthPoint = cHealthPoint

    def calcEvadeChance(self, attacker):
        """회피 확률 계산"""
        agilDiff = max(self.cDeterxity - attacker.cDeterxity, 1)
        luckDiff = max(self.cLuck - attacker.cLuck, 1)

        evade_value = agilDiff * 3 * luckDiff
        evade_chance = min(max(evade_value, 5), 90)  # 최소 5, 최대 90으로 제한

        return evade_chance
    """    def targettingChance(self, distance = 1):#명중판정
        if (distance <= 1):
            return -1 #"근접 거리이므로 타게팅 판정을 무시합니다"
        else:
            return random.randint(1, 100)
    """
    """    def evadeAttack(self, attacker):
        evadeChance = self.calcEvadeChance(attacker)
        randInt = random.randint(1, 100)
        if evadeChance > randInt:#evaded
            return true
        else:
            return false #evade failed
    """

    def calcEvadeChance(self, attacker):
        """회피 확률 계산"""
        agilDiff = max(int(self.cDeterxity) - int(attacker.cDeterxity), 1)
        luckDiff = max(int(self.cLuck) - int(attacker.cLuck), 1)

        evade_value = agilDiff * 3 * luckDiff
        evade_chance = min(max(evade_value, 5), 90)  # 최소 5, 최대 90으로 제한

        return evade_chance


@bot.event
async def on_ready():  # 봇 준비 시 1회 동작하는 부분
    # 봇 이름 하단에 나오는 상태 메시지 및 상태 설정
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!helpMe로 명령어 확인 하는중"))  # 이곳에
    print("Bot is ready")


@bot.command()  # 봇 명령어
async def hello(ctx):  # !hello라고 사용자가 입력하면
    await ctx.send("Hello world")  # 봇이 Hello world라고 대답함


@bot.command()
async def doh(ctx):
    randnum = random.randint(1, 100)  # 1이상 100이하 랜덤 숫자를 뽑음
    await ctx.send(f'주사위 결과는 {randnum} 입니다.')


@bot.command()
async def d20(ctx):
    userMean = 30.0;  # 유저 스탯의 평균을 집어넣는다.
    randnum = random.randint(1, 20)  # 1이상 20이하 랜덤 숫자를 뽑음
    userMean = 90 - userMean
    userMean = userMean + float(randnum * 5)
    randnum = int(((userMean)) / 10)
    if randnum > 20:
        randnum = 20
    elif randnum < 1:
        randnum = 1
    await ctx.send(f'1d20 주사위 결과는 {randnum}/20 입니다.')


@bot.command()
async def evade(ctx):
    cnt = 0
    tempString = "50d100 = \n{"
    for i in range(49):
        randNum = random.randint(1, 100)  # 1이상 100이하 랜덤 숫자를 뽑음
        if (randNum >= 10):
            tem = "%d " % randNum
        else:
            tem = "0%d " % randNum
        tempString = tempString + tem
        if ((i + 1) % 10 == 0):
            tempString = tempString + "\n "
        if (randNum <= 25):
            cnt += 1
    randNum = random.randint(1, 100)  # 1이상 100이하 랜덤 숫자를 뽑음
    if (randNum >= 10):
        tem = "%d}가 나왔습니다.\n" % randNum
    else:
        tem = "0%d}가 나왔습니다.\n" % randNum
    tempString = tempString + tem
    if (randNum <= 25):
        cnt += 1
    tempString = tempString + "25 이하인 회피성공 횟수는 %d개,\n" % cnt
    tempString = tempString + "25 초과인 회피실패 횟수는 %d개입니다" % (50 - cnt)
    await ctx.send(tempString)
    tempString = ""


@bot.command()
async def dr(ctx, diceDef="d"):  # diceRoll
    diceList = diceDef.split("d")
    tempstring = "당신이 굴린 "
    if (len(diceList) != 2):
        tempstring = "입력이 잘못되었습니다.\n!dr (다이스 개수)d(다이스 눈 수)형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !dr 1d5"  # no d or too many d
    elif diceList[0] == "":
        tempstring = "입력이 잘못되었습니다.\n!dr (다이스 개수)d(다이스 눈 수)형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !dr 1d5"  # didn't input anything front
    elif diceList[1] == "":
        tempstring = "입력이 잘못되었습니다.\n!dr (다이스 개수)d(다이스 눈 수)형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !dr 1d5"  # didn't input anything rear
    else:
        howManyDice = 0  # how many dice you wanna role?
        howManyPoint = 0  # how many dice point you wanna role?
        # diceList[0].strip()
        # diceList[0].strip("\n")
        # diceList[1].strip()
        # diceList[1].strip("\n")
        diceQ = queue.Queue()  # a queue to put dice results on
        dicePassed = 0  # sum of all dice
        try:
            howManyDice = int(diceList[0])
            howManyPoint = int(diceList[1])
            tempstring += diceDef + " 결과는 [ "
            for i in range(0, howManyDice):
                randNum = random.randint(1, howManyPoint)  # 1이상 input이하 랜덤 숫자를 뽑음
                diceQ.put(randNum)
                # print(randNum + " ")
            for i in range(0, diceQ.qsize()):
                tempInt = diceQ.get()
                tempstring += (str(tempInt) + " ")
                dicePassed += tempInt
            tempstring += "] 이고\n이 수의 합은 %d가 나왔습니다." % dicePassed
            # tempstring += diceList[0] + " " + diceList[1]
        except:
            tempstring = "입력이 잘못되었습니다.\n!dr (다이스 개수)d(다이스 눈 수)형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !dr 1d5"
        # for i in range(0, len(diceList)):
        #    tempstring += " " + diceList[i]
    await ctx.send(tempstring)


@bot.command()
async def ctd(ctx, targetTemp="50"):  # CThulu Dice
    try:
        target = int(targetTemp)
        if target == -1:
            tempstring = "입력이 잘못되었습니다.\n'!ctd (목표값)' 형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !ctd! 50"
        tempstring = "당신이 굴린 1d100은 목표값인 " + str(target) + " 기준"
        randNum = random.randint(1, 100)  # 1이상 100이하 랜덤 숫자를 뽑음
        tempstring += str(randNum) + " 이 나왔고, 이는 "
        if randNum == 1:
            tempstring += "완전 성공(Complete Success)에 해당합니다."
        elif randNum == 100:
            tempstring += "완전실패(Complete Failure)에 해당합니다"
        elif randNum >= 95:
            tempstring += "펌블(Super Critical)에 해당합니다"
        elif randNum <= 10:
            tempstring += "대성공(Extreme Success)에 해당합니다."
        elif randNum >= 90:
            tempstring += "대실패(Critical Failure)에 해당합니다"
        elif randNum <= target:
            tempstring += "성공(Success)에 해당합니다"
        else:
            tempstring += "실패(Failure)에 해당합니다"

    except:
        tempstring = "입력이 잘못되었습니다.\n'!ctd (목표값)' 형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !ctd 50"
    await ctx.send(tempstring)


@bot.command()
async def ccm(ctx, statArr=""):  # CThulu Character Make
    statList = statArr.split("/")
    tempstring = "당신의 캐릭터의 스탯은 \n"
    if (statArr == ""):
        tempstring = "입력이 잘못되었습니다.\n!ccm (굴릴 파라미터)/(굴릴 파라미터)/...형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !ccm 근력/체력/운"  # no parameter or wrone one
    elif len(statList) == 0:
        tempstring = "입력이 잘못되었습니다.\n!ccm (굴릴 파라미터)/(굴릴 파라미터)/...형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !ccm 근력/체력/운"  # didn't input anything
    else:
        try:
            for i in statList:
                randNum = (random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6)) * 5
                tempstring += i + ": %d\n" % randNum
        except:
            tempstring = "입력이 잘못되었습니다.\n!ccm (굴릴 파라미터)/(굴릴 파라미터)/...형식으로 입력해주시기를 부탁드리겠습니다.\n예시: !ccm 근력/체력/운"

    await ctx.send(tempstring)


@bot.command()
async def ds(ctx):  # d6
    randnum1 = random.randint(1, 6)  # 1이상 100이하 랜덤 숫자를 뽑음
    randnum2 = random.randint(1, 6)  # 1이상 100이하 랜덤 숫자를 뽑음
    tempstring = ""
    tempstring += str(randnum1) + ", "
    tempstring += str(randnum2) + "\n합: "
    tempstring += str(randnum2 + randnum2)
    await ctx.send(tempstring)


@bot.command()
async def simWar(ctx, aLuck=30, aDex=50, aAtkDamage=5, aIsHidden=0, aHP=30, aClip=5, aReloadTime=1, bLuck=30, bDex=50,
                 bAtkDamage=5, bIsHidden=0, bHP=30, bClip=5, bReloadTime=1, shotDifficulty=1,
                 evadeDifficulty=1):  # ai fight
    aAtkType = "총"
    bAtkType = "총"
    tempstring = "모의전을 시작합니다\n A:\n-행운: "
    tempstring += (str(aLuck) + '\n-민첩: ')
    tempstring += (str(aDex) + '\n-공격타입: ')
    tempstring += (str(aAtkType) + '\n-무기 데미지:')
    tempstring += (str(aAtkDamage) + '\n-엄폐여부:')
    tempstring += (str(aIsHidden) + '\n-체력:')
    tempstring += (str(aHP) + '\n-클립 탄 수:')
    tempstring += (str(aClip) + "\n-클립 재장전 턴수: ")
    tempstring += (str(aReloadTime) + '\nB:\n-행운:')
    tempstring += (str(bLuck) + '\n-민첩: ')
    tempstring += (str(bDex) + '\n-공격타입: ')
    tempstring += (str(bAtkType) + '\n-무기 데미지:')
    tempstring += (str(bAtkDamage) + '\n-엄폐여부:')
    tempstring += (str(bIsHidden) + '\n-체력:')
    tempstring += (str(bHP) + '\n-클립 탄 수:')
    tempstring += (str(bClip) + "\n-클립 재장전 턴수: ")
    tempstring += (str(bReloadTime) + '')
    await ctx.send(tempstring)
    aTurnLeft = aReloadTime
    bTurnLeft = bReloadTime
    aClipLeft = aClip
    bClipLeft = bClip

    aEvadeRate = 0
    bEvadeRate = 0
    aShotDifficulty = shotDifficulty
    bShotDifficulty = shotDifficulty
    if (aIsHidden == 1):
        bShotDifficulty += 2
    if (bIsHidden == 1):
        aShotDifficulty += 2
    aDexDiff = 1
    bDexDiff = 1
    aLuckDiff = 1
    bLuckDiff = 1
    if ((aDex - bDex) >= 1):
        aDexDiff = (aDex - bDex)
    if ((bDex - aDex) >= 1):
        bDexDiff = (aDex - bDex)
    if ((aLuck - bLuck) >= 1):
        bLuckDiff = (aLuck - bLuck)
    if ((bLuck - aLuck) >= 1):
        bLuckDiff = (bLuck - aLuck)
    if (aDex >= bDex):
        if (aLuck - bLuck >= 0):
            aEvadeRate = aDexDiff * 3 / evadeDifficulty * aLuckDiff
        else:
            aEvadeRate = 0
    else:
        aEvadeRate = 0
    if (bDex >= aDex):
        if (bLuck - aLuck >= 0):
            bEvadeRate = bDexDiff * 3 / evadeDifficulty * bLuckDiff
        else:
            bEvadeRate = 0
    else:
        bEvadeRate = 0
    if (aEvadeRate > 90):
        aEvadeRate = 90
    elif (aEvadeRate < 5):
        aEvadeRate = 5
    if (bEvadeRate > 90):
        bEvadeRate = 90
    elif (bEvadeRate < 5):
        bEvadeRate = 5

    turnNow = 0
    while (aHP > 0 and bHP > 0):
        turnNow += 1
        tempstring = ("Turn: " + str(turnNow) + "\nA의 턴:\n")

        # Handle A's turn
        if aClipLeft <= 0:  # Check if A needs to reload
            if aTurnLeft <= 1:  # Reload completes
                aClipLeft = aClip  # Reset clip
                aTurnLeft = aReloadTime  # Reset reload counter
                tempstring += "A 장전 완료\n"
            else:  # Reload in progress
                aTurnLeft -= 1
                tempstring += f"A 장전중... ({aReloadTime - aTurnLeft}/{aReloadTime})\n"
        else:  # A can fire
            aClipLeft -= 1
            aShotRand = random.randint(1, 100)
            tempstring += f"A 발사 \nA 명중굴림: {aShotRand}"
            if aShotRand < (70 / aShotDifficulty):  # A's attack hit
                bEvadeRand = random.randint(1, 100)
                tempstring += f" < 70 / {aShotDifficulty}, A 공격 명중\nB 회피굴림: {bEvadeRand}"
                if bEvadeRand > bEvadeRate:  # B couldn't evade
                    bHP -= aAtkDamage
                    tempstring += f" > {bEvadeRate}, 실패 B는 {aAtkDamage}의 데미지를 입었습니다. 남은 B HP: {bHP}\n"
                else:  # B evaded
                    tempstring += f" <= {bEvadeRate}, 성공 B는 A의 공격을 회피했습니다. 남은 B HP: {bHP}\n"
            else:  # A's attack missed
                tempstring += f" >= 70 / {aShotDifficulty}, A 공격 명중 실패\n"

        if bHP <= 0:
            tempstring += f"B의 HP가 0보다 낮으므로, B는 사망했습니다. A {turnNow}턴 만에 우승"
            await ctx.send(tempstring)
            break

        # Handle B's turn
        tempstring += "\nB의 턴:\n"
        if bClipLeft <= 0:  # Check if B needs to reload
            if bTurnLeft <= 1:  # Reload completes
                bClipLeft = bClip  # Reset clip
                bTurnLeft = bReloadTime  # Reset reload counter
                tempstring += "B 장전 완료\n"
            else:  # Reload in progress
                bTurnLeft -= 1
                tempstring += f"B 장전중... ({bReloadTime - bTurnLeft}/{bReloadTime})\n"
        else:  # B can fire
            bClipLeft -= 1
            bShotRand = random.randint(1, 100)
            tempstring += f"B 발사 \nB 명중굴림: {bShotRand}"
            if bShotRand < (70 / bShotDifficulty):  # B's attack hit
                aEvadeRand = random.randint(1, 100)
                tempstring += f" < 70 / {bShotDifficulty}, B 공격 명중\nA 회피굴림: {aEvadeRand}"
                if aEvadeRand > aEvadeRate:  # A couldn't evade
                    aHP -= bAtkDamage
                    tempstring += f" > {aEvadeRate}, 실패 A는 {bAtkDamage}의 데미지를 입었습니다. 남은 A HP: {aHP}\n"
                else:  # A evaded
                    tempstring += f" <= {aEvadeRate}, 성공 A는 B의 공격을 회피했습니다. 남은 A HP: {aHP}\n"
            else:  # B's attack missed
                tempstring += f" >= 70 / {bShotDifficulty}, B 공격 명중 실패\n"

        if aHP <= 0:
            tempstring += f"A의 HP가 0보다 낮으므로, A는 사망했습니다. B {turnNow}턴 만에 우승"
            await ctx.send(tempstring)
            break

        await ctx.send(tempstring)  # Send message after both turns

    tempstring = "\n시뮬레이션 종료"
    await ctx.send(tempstring)


@bot.command()
async def simWarMelee(ctx, aWeaponSkill=2, aStrength=60, aAgility=70, aLuck=60,
                      aCover=0, aHP=40, aEvadeDifficulty=3, bLuck=20, bAgility=40,
                      bProficiency=70, bDamage=5, bHP=60, bClip=6,
                      bReloadTime=2, bHitDifficulty=3, bEvadeDifficulty=3, distance=100):
    A = Character(aWeaponSkill, aStrength, aAgility, aLuck, aCover, aHP, aEvadeDifficulty)
    B = Shooter(aWeaponSkill, bAgility, bLuck, bHP, bEvadeDifficulty,
                bProficiency, bDamage, bClip, bReloadTime, bHitDifficulty)

    await ctx.send(
        f"A:\n"
        f"- 무기 능력치: {A.weapon_skill}\n"
        f"- 근력: {A.strength}\n"
        f"- 민첩: {A.agility}\n"
        f"- 행운: {A.luck}\n"
        f"- 엄폐 여부: {A.cover}\n"
        f"- 체력: {A.hp}\n"
        f"- 회피 난이도: {A.evade_difficulty}"
    )

    await ctx.send(
        f"B:\n"
        f"- 행운: {B.luck}\n"
        f"- 민첩: {B.agility}\n"
        f"- 공격 타입: 총\n"
        f"- 무기 데미지: {B.damage}\n"
        f"- 엄폐 여부: {B.cover}\n"
        f"- 체력: {B.hp}\n"
        f"- 클립 탄 수: {B.clip}\n"
        f"- 클립 재장전 턴수: {B.reload_time}"
    )

    tempstring = []
    # 전투 루프
    while A.hp > 0 and B.hp > 0:
        distance = battle_turn(A, B, distance, tempstring)
        await ctx.send("\n".join(tempstring))
        tempstring.clear()

        if A.hp <= 0 or B.hp <= 0:
            break


def battle_turn(A, B, distance, tempstring):
    if distance > 0:
        tempstring.append("\nA, B쪽으로 이동")
        move_distance = A.move_toward()
        distance -= move_distance
        distance = max(0, distance)  # 음수 방지
        tempstring.append(f"A가 B 방향으로 {move_distance:.2f} 이동. 남은 거리: {distance:.2f}")
    else:
        # A가 도달 시 근접 공격 수행
        tempstring.append("A, 근접 공격 수행")
        evade_chance = calculate_evade_chance(B, A)  # 수정된 함수 사용
        evade_roll = random.randint(1, 100)

        tempstring.append(f"B 회피굴림: {evade_roll} < {evade_chance:.2f}, {'성공' if evade_roll < evade_chance else '실패'}")

        if evade_roll >= evade_chance:
            damage = A.melee_damage()
            B.hp -= damage
            tempstring.append(f"A가 B에게 {damage}의 근접 데미지를 입혔습니다. 남은 B HP: {B.hp}")

            if B.hp <= 0:
                tempstring.append("\nB의 체력이 0이 되었습니다. A의 승리")
                return distance
        else:
            tempstring.append("B 회피 성공")

    # B의 공격 처리 또는 장전 상태 관리
    if B.turns_until_reloaded > 0:
        tempstring.append(f"B 장전중({B.reload_time - B.turns_until_reloaded + 1}/{B.reload_time})턴")
        B.turns_until_reloaded -= 1
        if B.turns_until_reloaded == 0:
            tempstring.append("B 장전 완료")
            B.current_ammo = B.clip
    elif B.current_ammo > 0:
        hit_roll = random.randint(1, 100)
        hit_chance = B.hit_chance(A)  # 확률 계산에 100 곱하지 않음

        tempstring.append(
            f"B 명중굴림: {hit_roll} < {hit_chance:.2f} / 1, {'B 공격 명중' if hit_roll < hit_chance else 'B 명중 실패'}"
        )
        B.current_ammo -= 1

        if hit_roll < hit_chance:
            evade_chance = calculate_evade_chance(A, B)  # 수정된 함수 사용
            evade_roll = random.randint(1, 100)

            tempstring.append(
                f"A 회피굴림: {evade_roll} < {evade_chance:.2f}, {'성공' if evade_roll < evade_chance else '실패'}")

            if evade_roll >= evade_chance:
                A.hp -= B.damage
                tempstring.append(f"B가 A에게 {B.damage}의 총기 데미지를 입혔습니다. 남은 A HP: {A.hp}")

                if A.hp <= 0:
                    tempstring.append("\nA의 체력이 0이 되었습니다. B의 승리!")
                    return distance
            else:
                tempstring.append("A, 회피 성공")
        else:
            tempstring.append("B, 명중 실패")
    else:
        tempstring.append("B 탄환 부족, 장전 시작")
        B.turns_until_reloaded = B.reload_time

    return distance


@bot.command()
async def simWarMelee2(ctx, aWeaponSkill=2, aStrength=60, aAgility=70, aLuck=60,
                       aCover=0, aHP=40, aEvadeDifficulty=3, bWeaponSkill=2, bStrength=60, bAgility=70, bLuck=60,
                       bCover=0, bHP=40, bEvadeDifficulty=3):
    A = Character(aWeaponSkill, aStrength, aAgility, aLuck, aCover, aHP, aEvadeDifficulty)
    B = Character(bWeaponSkill, bStrength, bAgility, bLuck, bCover, bHP, bEvadeDifficulty)

    await ctx.send(
        f"A:\n"
        f"- 무기 능력치: {A.weapon_skill}\n"
        f"- 근력: {A.strength}\n"
        f"- 민첩: {A.agility}\n"
        f"- 행운: {A.luck}\n"
        f"- 엄폐 여부: {A.cover}\n"
        f"- 체력: {A.hp}\n"
        f"- 회피 난이도: {A.evade_difficulty}"
    )

    await ctx.send(
        f"B:\n"
        f"- 무기 능력치: {B.weapon_skill}\n"
        f"- 근력: {B.strength}\n"
        f"- 민첩: {B.agility}\n"
        f"- 행운: {B.luck}\n"
        f"- 엄폐 여부: {B.cover}\n"
        f"- 체력: {B.hp}\n"
        f"- 회피 난이도: {B.evade_difficulty}"
    )

    tempstring = []
    # 전투 루프
    while A.hp > 0 and B.hp > 0:
        battle_turn2(A, B, tempstring)
        await ctx.send("\n".join(tempstring))
        tempstring.clear()

        if A.hp <= 0 or B.hp <= 0:
            break


def battle_turn2(A, B, tempstring):
    # A가 도달 시 근접 공격 수행
    tempstring.append("A, 근접 공격 수행")
    evade_chance = calculate_evade_chance(B, A)  # 수정된 함수 사용
    evade_roll = random.randint(1, 100)

    tempstring.append(f"B 회피굴림: {evade_roll} < {evade_chance:.2f}, {'성공' if evade_roll < evade_chance else '실패'}")

    if evade_roll >= evade_chance:
        damage = A.melee_damage()
        B.hp -= damage
        tempstring.append(f"A가 B에게 {damage}의 근접 데미지를 입혔습니다. 남은 B HP: {B.hp}")

        if B.hp <= 0:
            tempstring.append("\nB의 체력이 0이 되었습니다. A의 승리")
            return
    else:
        tempstring.append("B 회피 성공")

    tempstring.append("B의 턴\nB, 근접 공격 수행")
    evade_chance = calculate_evade_chance(A, B)  # 수정된 함수 사용
    evade_roll = random.randint(1, 100)

    tempstring.append(f"A 회피굴림: {evade_roll} < {evade_chance:.2f}, {'성공' if evade_roll < evade_chance else '실패'}")

    if evade_roll >= evade_chance:
        damage = B.melee_damage()
        A.hp -= damage
        tempstring.append(f"B가 A에게 {damage}의 근접 데미지를 입혔습니다. 남은 A HP: {B.hp}")

        if A.hp <= 0:
            tempstring.append("\nA의 체력이 0이 되었습니다. B의 승리")
    else:
        tempstring.append("A 회피 성공")
    return


def calculate_evade_chance(evader, attacker):
    """회피 확률 계산 (퍼센트 환산 제거)"""
    # 회피 공식 계산
    agilDiff = 1
    luckDiff = 1
    if (evader.agility - attacker.agility >= 1):
        agilDiff = (evader.agility - attacker.agility)
    else:
        agilDiff = 1

    if (evader.luck - attacker.luck >= 1):
        luckDiff = (evader.luck - attacker.luck)
    else:
        luckDiff = 1
    evade_value = agilDiff * 3 * luckDiff

    # 회피 난이도 체크 (0으로 나누는 것을 방지)
    if evader.evade_difficulty <= 1:
        evader.evade_difficulty = 1  # 최소 1로 설정

    # 회피 확률 계산 (퍼센트 환산 제거)
    evade_chance = evade_value / evader.evade_difficulty
    if (evade_chance >= 90):
        evade_chance = 90
    elif (evade_chance <= 5):
        evade_chance = 5

    return evade_chance  # 그대로 반환


@bot.command()
async def createCharacter(ctx, cHealth=0, cStrength=0, cDeterxity=0, cIntelligence=0,
                           cWisdom=0, cLuck=0, cWeaponRange=0, cWeaponDamage=0):
    """캐릭터 생성 및 데이터베이스 저장"""
    if ctx.author.bot:
        return

    user_id = str(ctx.author.id)
    updated = False
    new_lines = []

    # 파일 읽기 및 중복 확인
    try:
        with open(charDataFileName, "r") as RCF:
            lines = RCF.readlines()
            for line in lines:
                if line.split(",")[0] == user_id:  # 정확한 ID 매칭
                    # 기존 유저 데이터 업데이트
                    new_line = f"{user_id}, {cHealth}, {cStrength}, {cDeterxity}, {cIntelligence}, {cWisdom}, {cLuck}, {cWeaponRange}, {cWeaponDamage}, {cHealth * 5}\n"
                    new_lines.append(new_line)
                    updated = True
                else:
                    new_lines.append(line)
    except FileNotFoundError:
        # 파일이 없을 경우 새로 생성
        new_lines = []

    # 기존 데이터 업데이트 or 새 데이터 추가
    if not updated:
        new_line = f"{user_id}, {cHealth}, {cStrength}, {cDeterxity}, {cIntelligence}, {cWisdom}, {cLuck}, {cWeaponRange}, {cWeaponDamage}, {cHealth * 5}\n"
        new_lines.append(new_line)
        print("새 UID 추가")
        await ctx.send("캐릭터 생성 완료.")
    else:
        print("UID 이미 존재, 업데이트 완료")
        await ctx.send("UID 이미 존재, 업데이트 완료")

    # 변경된 내용 파일에 쓰기
    with open(charDataFileName, "w") as WCF:
        WCF.writelines(new_lines)
    return


def loadCharacter(UID):  # 특정 UID를 가진 캐릭터를 Load해오는 명령어
    # 파일 읽기 및 중복 확인
    try:
        with open(charDataFileName, "r") as RCF:
            lines = RCF.readlines()
            for line in lines:
                if line.split(",")[0] == str(UID):  # 정확한 ID 매칭
                    character = PC(line.split(",")[0], line.split(",")[1], line.split(",")[2], line.split(",")[3],
                                   line.split(",")[4], line.split(",")[5], line.split(",")[6], line.split(",")[7],
                                   line.split(",")[8], line.split(",")[9])
                    return character

    except FileNotFoundError:
        # 파일이 없을 경우 새로 생성
        new_lines = []
    return

@bot.command()
async def charStat(ctx):
    selfChar = loadCharacter(ctx.author.id)
    await ctx.send(f"체력: {selfChar.cConstitution}\n근력: {selfChar.cStrength}\n민첩: {selfChar.cDeterxity}\n지능: {selfChar.cIntelligence}\n지혜: {selfChar.cWisdom}\n행운: {selfChar.cLuck}\n무기 사거리: {selfChar.cWeaponRange}\n무기 데미지: {selfChar.cWeaponDamage}\n현재 남은 HP: {selfChar.cHealthPoint} 최대 HP: {int(selfChar.cConstitution) * 5}")


@bot.command()
async def evadeCharAtk(ctx, mention: str):
    match = re.match(r"<@!?(\d+)>", mention)
    if match:
        targetUserID = int(match.group(1))
    else:
        await ctx.send("올바른 멘션 형식이 아닙니다.")
        return

    print(ctx.author.id)
    selfChar = loadCharacter(ctx.author.id)
    if selfChar is None:
        await ctx.send("당신의 캐릭터가 존재하지 않습니다. 먼저 캐릭터를 생성해주세요.")
        return

    print(targetUserID)
    attackerChar = loadCharacter(targetUserID)
    if attackerChar is None:
        await ctx.send("공격자의 캐릭터가 존재하지 않습니다. 먼저 캐릭터를 생성해주세요.1")
        return

    if not hasattr(selfChar, 'calcEvadeChance') or not hasattr(attackerChar, 'calcEvadeChance'):
        await ctx.send("캐릭터 데이터에 필요한 메서드가 없습니다.")
        return

    randNum = random.randint(1, 100)
    evadeChance = selfChar.calcEvadeChance(attackerChar)
    await ctx.send(f"회피 확률: {evadeChance}, 랜덤 값: {randNum}")
    if(randNum <= evadeChance):
        await ctx.send(f"1d100({randNum}) <= {evadeChance}\n회피 성공")
    else:
        await ctx.send(f"1d100({randNum}) > {evadeChance}\n회피 실패\n{attackerChar.cWeaponDamage}의 데미지를 받았습니다.\n캐릭터의 체력이 ({max(int(selfChar.cHealthPoint) - int(attackerChar.cWeaponDamage), 0)}/{int(selfChar.cConstitution) * 5})만큼 남았습니다")
        if(int(selfChar.cHealthPoint) - int(attackerChar.cWeaponDamage) <= 0):
            await ctx.send("캐릭터의 체력이 0보다 낮습니다. 캐릭터가 전투불능에 빠졌습니다.")
        new_lines = []
        try:
            with open(charDataFileName, "r") as RCF:
                lines = RCF.readlines()
                for line in lines:
                    if line.split(",")[0] == selfChar.UID:  # 정확한 ID 매칭
                        # 기존 유저 데이터 업데이트
                        new_line = f"{selfChar.UID}, {selfChar.cConstitution}, {selfChar.cStrength}, {selfChar.cDeterxity}, {selfChar.cIntelligence}, {selfChar.cWisdom}, {selfChar.cLuck}, {selfChar.cWeaponRange}, {selfChar.cWeaponDamage}, {int(selfChar.cHealthPoint) - int(attackerChar.cWeaponDamage)}\n"
                        new_lines.append(new_line)
                        updated = True
                    else:
                        new_lines.append(line)
        except FileNotFoundError:
            # 파일이 없을 경우 새로 생성
            new_lines = []
        with open(charDataFileName, "w") as WCF:
            WCF.writelines(new_lines)
        return


@bot.command()
async def charRunAway(ctx, distance, mention: str):
    match = re.match(r"<@!?(\d+)>", mention)
    print(ctx.author.id)

    if match:
        targetUserID = int(match.group(1))
        print(targetUserID)
    else:
        await ctx.send("올바른 멘션 형식이 아닙니다.")
        return
    selfChar = loadCharacter(ctx.author.id)
    if selfChar is None:
        await ctx.send("당신의 캐릭터가 존재하지 않습니다. 먼저 캐릭터를 생성해주세요.")
        return

    attackerChar = loadCharacter(targetUserID)
    if attackerChar is None:
        await ctx.send("공격자의 캐릭터가 존재하지 않습니다. 먼저 캐릭터를 생성해주세요.1")
        return

    if not hasattr(selfChar, 'calcEvadeChance') or not hasattr(attackerChar, 'calcEvadeChance'):
        await ctx.send("캐릭터 데이터에 필요한 메서드가 없습니다.")
        return

    randNum = random.randint(1, 100)
    runChance = min(max(int(selfChar.cDeterxity) - int(attackerChar.cDeterxity) + (int(distance) / 3) - int(attackerChar.cDeterxity) / 2, 10), 90)
    if (randNum < runChance):
        await ctx.send(f"1d100({randNum}) < {runChance}이므로 도주에 성공하셨습니다.")
    else:
        await ctx.send(f"1d100({randNum}) >= {runChance}이므로 도주에 실패하셨습니다.")

@bot.command()
async def healChar(ctx, amount = 1000000):
    selfChar = loadCharacter(ctx.author.id)
    new_lines = []
    try:
        with open(charDataFileName, "r") as RCF:
            lines = RCF.readlines()
            for line in lines:
                if line.split(",")[0] == selfChar.UID:  # 정확한 ID 매칭
                    # 기존 유저 데이터 업데이트
                    if (amount != 1000000 & int(selfChar.cHealthPoint) + amount <= int(selfChar.cConstitution) * 5):
                        new_line = f"{selfChar.UID}, {selfChar.cConstitution}, {selfChar.cStrength}, {selfChar.cDeterxity}, {selfChar.cIntelligence}, {selfChar.cWisdom}, {selfChar.cLuck}, {selfChar.cWeaponRange}, {selfChar.cWeaponDamage}, {int(selfChar.cHealthPoint) + amount}\n"
                        new_lines.append(new_line)
                        await ctx.send(f"체력을 {amount}만큼 회복시켜 ({int(selfChar.cHealthPoint)}/{int(selfChar.cConstitution) * 5})에서 ({int(selfChar.cHealthPoint) + amount}/{int(selfChar.cConstitution) * 5})가 되었습니다.")
                    elif (amount != 1000000):
                        new_line = f"{selfChar.UID}, {selfChar.cConstitution}, {selfChar.cStrength}, {selfChar.cDeterxity}, {selfChar.cIntelligence}, {selfChar.cWisdom}, {selfChar.cLuck}, {selfChar.cWeaponRange}, {selfChar.cWeaponDamage}, {int(selfChar.cConstitution) * 5}\n"
                        new_lines.append(new_line)
                        await ctx.send(f"체력을 {amount}만큼 회복시켜 ({selfChar.cHealthPoint}/{int(selfChar.cConstitution) * 5})에서 ({int(selfChar.cConstitution) * 5}/{int(selfChar.cConstitution) * 5})가 되었습니다.")
                    else:
                        new_line = f"{selfChar.UID}, {selfChar.cConstitution}, {selfChar.cStrength}, {selfChar.cDeterxity}, {selfChar.cIntelligence}, {selfChar.cWisdom}, {selfChar.cLuck}, {selfChar.cWeaponRange}, {selfChar.cWeaponDamage}, {int(selfChar.cConstitution) * 5}\n"
                        new_lines.append(new_line)
                        await ctx.send(
                            f"체력을 전부 회복시켜 ({selfChar.cHealthPoint}/{int(selfChar.cConstitution) * 5})에서 ({int(selfChar.cConstitution) * 5}/{int(selfChar.cConstitution) * 5})가 되었습니다.")

                else:
                    new_lines.append(line)
    except FileNotFoundError:
        # 파일이 없을 경우 새로 생성
        new_lines = []
    with open(charDataFileName, "w") as WCF:
        WCF.writelines(new_lines)

@bot.command()
async def setCharHP(ctx, newH):
    selfChar = loadCharacter(ctx.author.id)
    newHP = int(newH)
    new_lines = []
    try:
        with open(charDataFileName, "r") as RCF:
            lines = RCF.readlines()
            for line in lines:
                if line.split(",")[0] == selfChar.UID:  # 정확한 ID 매칭
                    # 기존 유저 데이터 업데이트
                    if (newHP > -1):
                        new_line = f"{selfChar.UID}, {selfChar.cConstitution}, {selfChar.cStrength}, {selfChar.cDeterxity}, {selfChar.cIntelligence}, {selfChar.cWisdom}, {selfChar.cLuck}, {selfChar.cWeaponRange}, {selfChar.cWeaponDamage}, {max(min(newHP, int(selfChar.cConstitution) * 5),1)}\n"
                        new_lines.append(new_line)
                        await ctx.send(
                            f"체력을 ({newHP}/{int(selfChar.cConstitution) * 5})로 설정하였습니다.")
                    else:
                        await ctx.send("올바른 체력 값을 입력하여 주십시오.")
                else:
                    new_lines.append(line)
    except FileNotFoundError:
        # 파일이 없을 경우 새로 생성
        new_lines = []
    with open(charDataFileName, "w") as WCF:
        WCF.writelines(new_lines)

@bot.command()
async def helpList(ctx):
    await ctx.send("현재 help가 작성되어 있는 명령어는 doh, d20, evade, dr, ctd, ccm, ds, createCharacter, charStat, evadeCharAtk, charRunAway, healChar, 가 있습니다\n!helpMe 명령어를 사용해 질의해 주세요.")

@bot.command()
async def charAttack(ctx):
    randnum = random.randint(1, 100)  # 1이상 100이하 랜덤 숫자를 뽑음
    #answer = (randnum <= 70 ? "성공" : "실패")
    answer = ["> 70이므로, 공격은 빗나갔습니다. 턴을 넘깁니다.", "<= 70이므로, 공격은 명중하였습니다.\n회피 판정을 진행해주시기 바랍니다. (evadeCharAtk)"][randnum <= 70]
    await ctx.send(f"d100({randnum}) {answer}.")


@bot.command()
async def helpMe(ctx, submenu = ""):
    if(submenu == "doh"):
        await ctx.send("doh\n\t사용법: !doh\n\t주사위를 굴려 1에서 100 사이의 랜덤 숫자를 생성하고 결과를 보여줍니다.")
    elif(submenu == "d20"):
        await ctx.send("d20\n\t사용법: !d20\n\t1에서 20 사이의 랜덤 숫자를 굴리고, 유저의 평균 스탯에 따라 결과를 조정하여 1에서 20 사이의 값을 반환합니다.")
    elif (submenu == "evade"):
        await ctx.send("evade\n\t사용법: !evade\n\t50개의 100면 주사위를 굴린 후, 25 이하의 숫자가 나온 횟수와 25 초과의 숫자가 나온 횟수를 계산하여 결과를 보여줍니다.")
    elif (submenu == "dr"):
        await ctx.send("dr\n\t사용법: !dr (다이스 개수)d(다이스 눈 수) (예시: !dr 1d5)\n\t지정한 개수의 주사위를 굴려 결과를 보여줍니다.")
    elif (submenu == "ctd"):
        await ctx.send("ctd\n\t사용법: !ctd (목표값) (예시: !ctd 50)\n\t1d100 주사위를 굴리고, 결과에 따라 성공/실패를 판단하여 메시지를 반환합니다.")
    elif (submenu == "ccm"):
        await ctx.send("ccm\n\t사용법: !ccm (굴릴 파라미터)/(굴릴 파라미터)/... (예시: !ccm 근력/체력/운)\n\t각 파라미터에 대해 3d6 주사위를 굴려 캐릭터의 스탯을 생성하여 보여줍니다.")
    elif (submenu == "ds"):
        await ctx.send("ds\n\t사용법: !ds\n\t2개의 6면 주사위를 굴리고, 각각의 결과와 합계를 보여줍니다.")
    elif (submenu == "createCharacter"):
        await ctx.send("createCharacter\n\t사용법: !createCharacter (체력) (근력) (민첩) (지능) (지혜) (행운) (무기 사거리) (무기 데미지)\n\t(예시: !createCharacter 10 20 20 20 20 20 30 30\n\t캐릭터를 생성하고 해당 정보를 데이터베이스에 저장합니다.")
    elif (submenu == "charStat"):
        await ctx.send("charStat\n\t사용법: !charStat\n\t현재 사용자의 캐릭터 스탯을 보여줍니다.")
    elif (submenu == "evadeCharAtk"):
        await ctx.send("evadeCharAtk\n\t사용법: !evadeCharAtk @멘션\n\t(예시: !evadeCharAtk @eat_or_die)\n\t멘션한 캐릭터의 공격을 회피 시도하고 결과를 보여줍니다.")
    elif (submenu == "charRunAway"):
        await ctx.send("charRunAway\n\t사용법: !charRunAway (거리) @멘션\n\t(예시: !charRunAway 50 @eat_or_die)\n\t멘션한 캐릭터에게서 도망가려 시도하고 성공 여부를 보여줍니다.")
    elif (submenu == "healChar"):
        await ctx.send("healChar\n\t사용법: !healChar (회복량) (예시: !healChar 10)\n\t캐릭터의 체력을 (회복량)만큼 회복시키고 결과를 보여줍니다. (회복량을 비울경우 최대회복으로 간주합니다)")
    elif (submenu == "setCharHP"):
        await ctx.send("!setCharHP (새 체력)\n\t(예시: !setCharHP 50)\n\t캐릭터의 체력을 지정한 값으로 설정합니다.")
    elif (submenu == "charAttack"):
        await ctx.send("!charAttack \n\t캐릭터의 명중판정을 진행합니다.")
    else:
        await ctx.send("1. doh\n\t사용법: !doh\n\t주사위를 굴려 1에서 100 사이의 랜덤 숫자를 생성하고 결과를 보여줍니다.\n2. d20\n\t사용법: !d20\n\t1에서 20 사이의 랜덤 숫자를 굴리고, 유저의 평균 스탯에 따라 결과를 조정하여 1에서 20 사이의 값을 반환합니다.\n3. evade\n\t사용법: !evade\n\t50개의 100면 주사위를 굴린 후, 25 이하의 숫자가 나온 횟수와 25 초과의 숫자가 나온 횟수를 계산하여 결과를 보여줍니다.\n4. dr\n\t사용법: !dr (다이스 개수)d(다이스 눈 수) (예시: !dr 1d5)\n\t지정한 개수의 주사위를 굴려 결과를 보여줍니다.\n5. ctd\n\t사용법: !ctd (목표값) (예시: !ctd 50)\n\t1d100 주사위를 굴리고, 결과에 따라 성공/실패를 판단하여 메시지를 반환합니다.\n6. ccm\n\t사용법: !ccm (굴릴 파라미터)/(굴릴 파라미터)/... (예시: !ccm 근력/체력/운)\n\t각 파라미터에 대해 3d6 주사위를 굴려 캐릭터의 스탯을 생성하여 보여줍니다.\n7. ds\n\t사용법: !ds\n\t2개의 6면 주사위를 굴리고, 각각의 결과와 합계를 보여줍니다.\n8. createCharacter\n\t사용법: !createCharacter (체력) (근력) (민첩) (지능) (지혜) (행운) (무기 사거리) (무기 데미지)\n\t캐릭터를 생성하고 해당 정보를 데이터베이스에 저장합니다.\n9. charStat\n\t사용법: !charStat\n\t현재 사용자의 캐릭터 스탯을 보여줍니다.\n10. evadeCharAtk\n\t사용법: !evadeCharAtk @멘션\n\t멘션한 캐릭터의 공격을 회피 시도하고 결과를 보여줍니다.\n11. charRunAway\n\t사용법: !charRunAway (거리) @멘션\n\t멘션한 캐릭터에게서 도망가려 시도하고 성공 여부를 보여줍니다.\n12. healChar\n\t사용법: !healChar (회복량) (예시: !healChar 10)\n\t캐릭터의 체력을 (회복량)만큼 회복시키고 결과를 보여줍니다. (회복량을 비울경우 최대회복으로 간주합니다)\n13. setCharHP\n\t 사용법: !setCharHP (새 체력)\n\t캐릭터의 체력을 지정한 값으로 설정합니다.\n14. !charAttack \n\t캐릭터의 명중판정을 진행합니다.")



bot.run(token)
