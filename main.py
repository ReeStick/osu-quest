import discord
from discord.ext import commands
import json
import random
from ossapi import Ossapi
from sqlalchemy import text
import init_db
from anek_parser import get_random_aneks
import asyncio

with open('token.txt') as f:
    tokens = f.readline().split(', ')
    # print(tokens)
config = {
    'token': tokens[0],
    'prefix': '=',
}

intents = discord.Intents.all()
with open('gacha.json', encoding='utf-8') as file:
    gacha_conf = json.load(file)
osu_api = Ossapi(28386, tokens[1])
engine = init_db.engine
init_db.init_db()
anekdotes = []
bot = commands.Bot(command_prefix=config['prefix'],intents=intents)

def gacha_rolls(discord_id, roll_count=1) -> list[str]:
    message = ''
    global anekdotes
    with engine.connect() as conn:
        rolls = []
        rolls_done = []
        for i in conn.execute(text(f'SELECT rolls_amount, rolls_done FROM user WHERE discord_id = {discord_id}')):
            rolls = i[0]
            rolls_done = i[1]
        if not rolls:
            return ['Link your account first! Command: `=link <osu name/id>`']
        if rolls < roll_count:
            return [f'Not enough rolls on account. Current amount: {rolls}']
        else:
            conn.execute(text(f'UPDATE user SET rolls_amount = {rolls - roll_count}, rolls_done = {rolls_done + roll_count} WHERE discord_id = {discord_id}'))
            conn.commit()
            message = f'Rolls remain: {rolls - roll_count}'
    odds_dict = {key: value["chance"] for key, value in gacha_conf.items()}
    odds = list(reversed(list(odds_dict.items())))
    rewards_list = []
    rewards = message
    for roll_num in range(roll_count):
        cumulative_chance = 0
        result = random.random()    
        reward = ''
        # print(odds_dict.items())
        for key, chance in odds:
            # print(f'key={key}, chance={chance}')
            cumulative_chance += chance
            if result < cumulative_chance:
                reward = random.choice(gacha_conf[key]['variants'])
                if reward == 'Анекдоты':
                    if not anekdotes:
                        anekdotes = get_random_aneks()
                    reward += '\n' + anekdotes.pop(0)
                reward = str(roll_num+1) + ' - ' + key + ':\n' + reward
                print(reward + 'length:', len(reward))
                if len(rewards + reward) >= 2000:
                    print('sum of len: ', len(rewards))
                    rewards_list.append(rewards)
                    rewards = ''
                rewards += '\n' + reward
                break
    rewards_list.append(rewards)
    print(rewards_list)
    return rewards_list

@bot.command()
async def gacha(ctx, *arg):
    '''
    Defines the reward based on gacha.json odds.
    '''
    for i in gacha_rolls(ctx.author.id):
        if i:
            await ctx.reply(i)
    
@bot.command()
async def roll_10(ctx, *arg):
    '''
    Same as gacha(ctx, *arg), but do 10 rolls at the time. Returns multiple messages bcs of discord symbol limit
    '''
    for i in gacha_rolls(ctx.author.id, roll_count=10):
        if i:
            await ctx.reply(i)
            await asyncio.sleep(1)
    
@bot.command(pass_context=True)
async def TEST_COMMAND_add_rolls(ctx, *arg):
    with engine.connect() as conn:
        conn.execute(text(f'UPDATE user SET rolls_amount = {arg[0]} WHERE discord_id = {ctx.author.id}'))
        conn.commit()
        await ctx.reply(f'Set {arg[0]} rolls for user {ctx.author.id}')
    
@bot.command()
async def dump(ctx, *arg):
    init_db.dump()
    await ctx.reply('dumped')
    
@bot.command(pass_context=True)
async def link(ctx, *arg):
    '''
    Links discord id with osu id. Currently uses arguments instead of OAuth
    '''
    if type(arg[0]) == str:
        user = osu_api.user(arg[0]).id
    else:
        user = arg[0]
    with engine.connect() as conn:
        discord_id = ctx.author.id
        is_in = False
        for i in conn.execute(text(f'SELECT * FROM user WHERE discord_id = {discord_id}')):
            is_in = i
        if not is_in:
            conn.execute(text(f'INSERT INTO user (discord_id, osu_id, rolls_amount, rolls_done) VALUES ({discord_id}, {user}, 10, 0)'))
            conn.commit()
            await ctx.reply(f"Succesfully linked {arg[0]} profile")
        else:
            conn.execute(text(f'UPDATE user SET osu_id = {user} WHERE discord_id = {discord_id}'))
            conn.commit()
            await ctx.reply(f"Succesfully re-linked with {arg[0]} profile")
    
@bot.command()
async def osu(ctx, *arg):
    '''
    Best alias for pr(ctx, *arg)
    '''
    await pr(ctx, *arg)

@bot.command()
async def pr(ctx, *arg):
    '''
    Displays profile with all the information about osu and osu!quest profiles
    '''
    with engine.connect() as conn:
        info = ()
        for i in conn.execute(text(f'SELECT * FROM user WHERE discord_id = {ctx.author.id}')):
            info = i
        if not info:
            await ctx.reply('Link your account first! Command: `=link <osu name/id>`')
            return
        await ctx.reply(f'''
osu id: {info[1]}
rolls remain: {info[2]}
rolls done: {info[3]}
                        ''')

@bot.command()
async def add_count_task(ctx, *arg):
    await ctx.reply(add_count_task(arg[0], arg[1]))

@bot.command()
async def rs(ctx, *arg):
    print(osu_api)

bot.run(config['token'])