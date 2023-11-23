import discord
from discord.ext import commands
import json
import random
from ossapi import Ossapi
import sqlalchemy
from sqlalchemy import text
import init_db
from anek_parser import get_random_aneks


with open('token.txt') as f:
    tokens = f.readline().split(', ')
    print(tokens)
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


@bot.command()
async def gacha(ctx, *arg):
    '''
    Defines the reward based on gacha.json odds. Currently don't cosumes the amount of users tries
    '''
    print('negr')
    global anekdotes
    # with engine.connect() as conn:
    #     res = conn.execute(text(f'SELECT * FROM user '))
    #     print(res.mappings().all())
        # if res[0].rolls_amount < 1:
        #     await ctx.reply('Not enough rolls on account')
        #     return
        # else:
        #     conn.execute(text(f'UPDATE user SET rolls_amount = {res[0].rolls_amount - 1} WHERE discord_id = {ctx.author.id}'))
    odds_dict = {key: value["chance"] for key, value in gacha_conf.items()}
    odds = list(reversed(list(odds_dict.items())))
    cumulative_chance = 0
    result = random.random()    
    
    print(odds_dict.items())
    for key, chance in odds:
        print(f'key={key}, chance={chance}')
        cumulative_chance += chance
        if result < cumulative_chance:
            reward = random.choice(gacha_conf[key]['variants'])
            if reward == 'Анекдоты':
                if not anekdotes:
                    anekdotes = get_random_aneks()
                reward += '\n' + anekdotes.pop(0)
            await ctx.reply(key + ':\n' + reward)
            return
        
    await ctx.reply('how')
    
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
        conn.execute(text(f'INSERT INTO user (discord_id, osu_id, rolls_amount, rolls_done) VALUES ({discord_id}, {user}, 0, 0)'))
        await ctx.reply(f"Succesfully linked {arg[0]} profile")
    
@bot.command()
async def osu(ctx, *arg):
    '''
    Best alias for pr
    '''
    await pr(ctx, *arg)

@bot.command()
async def pr(ctx, *arg):
    '''
    Displays profile with all the information about osu and osu!quest profiles
    '''
    print(osu_api.user("reestick").id)

@bot.command()
async def rs(ctx, *arg):
    print(osu_api)


bot.run(config['token'])