import random
import json
import discord
from datetime import datetime
from discord import ActionRow, Button, Interaction

# X_O

client = None

# Config
xo_init_purge_channel = True # To delete all messages on bot startup
xo_purge_limit = 100000

# Ranking
xo_ranking_channel_id = 962313472618680420
xo_ranking_message_id = None
xo_ranking_embed_title = 'LIVE LEADERBOARD'


xo_channel_id = 962323645148049469

xo_cmd_start = "/startgame"

xo_embed_title = 'XO DUEL'

xo_x_emoji = '❌'
xo_o_emoji = '⭕'
# Config End

# Utils
xo_games = dict()

xo_ranking = dict()
async def load_ranking(_client):
    global client
    global xo_ranking
    global xo_ranking_message_id

    client = _client

    with open('xo_ranking.json') as json_file:
        xo_ranking = json.load(json_file)

    message = None
    with open('xo_config.json') as json_file:
        xo_config = json.load(json_file)
        if not xo_config['xo_ranking_message_id']:
            message = await write_leaderboard('w')
        else:
            xo_ranking_message_id = xo_config['xo_ranking_message_id']

    if message:
        to_write = { 'xo_ranking_message_id': message.id }
        with open('xo_config.json', 'w') as outfile:
            json.dump(to_write, outfile)
        xo_ranking_message_id = message.id

    return

async def save_ranking():
    global xo_ranking

    # Update DB in json
    with open('xo_ranking.json', 'w') as outfile:
        json.dump(xo_ranking, outfile)

    # Update message
    await write_leaderboard('e')
    

def add_game_to_history(user_id, status):
    global xo_ranking

    user_id = str(user_id)

    if user_id not in xo_ranking.keys():
        xo_ranking[user_id] = {
            'w': 0,
            'd': 0,
            'l': 0
        }

    if status == 'w':
        xo_ranking[user_id]['w'] += xo_ranking[user_id]['w'] + 1
    elif status == 'd':
        xo_ranking[user_id]['d'] += xo_ranking[user_id]['d'] + 1
    elif status == 'l':
        xo_ranking[user_id]['l'] += xo_ranking[user_id]['l'] + 1

async def write_leaderboard(flag):
    global xo_ranking

    channel = client.get_channel(xo_ranking_channel_id)

    description = '➡️ **Top 10 XO Players.** 🏆\n\n'
    
    i = 0
    sorted_xo_ranking = sorted(xo_ranking.items(), key = lambda x: (x[1])['w'], reverse = True)
    for (key, value) in sorted_xo_ranking:
        wins = value['w']
        draws = value['d']
        loses = value['l']

        description += f'`{i+1}.` <@{key}>: `{wins} Wins, {draws} Draws, {loses} Loses`\n'
        i += 1

        if i >= 10:
            break
    
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    description += f'\n*Today at {dt_string}*\n'

    embed = discord.Embed(title = xo_ranking_embed_title, description = description)
    embed.set_image(url = 'https://cdn.discordapp.com/attachments/909084451802325094/962340160710787112/Banner_149.gif?size=4096')

    if flag == 'w':
        return await channel.send(embed = embed)
    elif flag == 'e':
        message = await channel.fetch_message(xo_ranking_message_id)
        await message.edit(embed = embed)

    return

# Utils end

# Class

class XoGame:
    def __init__(self, client, channel, message):
        self.client = client
        self.channel = channel
        self.player_one = message.author
        self.player_two = message.mentions[0]
        self.winner = None
        self.draw = False

    def mark_tile(self, target):
        row = None
        col = None
        
        if 1 <= target <= 3:
            # First row
            row = 0
            col = target
        elif 4 <= target <= 6:
            # Second row
            row = 1
            col = target - 3
        elif 7 <= target <= 9:
            # Third row
            row = 2
            col = target-6
        else: 
            return

        # Mark tile
        # self.components = self.components[row].set_component_at(index = col, component = Button(label = self.next_emoji, custom_id = str(col), disabled = True))
        row_dict = self.components[row].to_dict()
        row_dict[0]['components'][col-1]['label'] = self.next_emoji
        row_dict[0]['components'][col-1]['disabled'] = True
        self.components[row] = ActionRow.from_dict(data = row_dict[0])
        # Set next player & emoji
        self.next_player = self.player_one if self.next_player == self.player_two else self.player_two # UNCOMMENT TO WORK
        self.next_emoji = xo_o_emoji if self.next_emoji == xo_x_emoji else xo_x_emoji

        return

    def check_game_status(self):
        row_0_dict = (self.components[0].to_dict())[0]
        row_1_dict = (self.components[1].to_dict())[0]
        row_2_dict = (self.components[2].to_dict())[0]

        check_emoji = xo_o_emoji if self.next_emoji == xo_x_emoji else xo_x_emoji
        check_winner = self.player_one if self.next_player == self.player_two else self.player_two

        game_status = True

        # Row win
        if row_0_dict['components'][0]['label'] == check_emoji and row_0_dict['components'][1]['label'] == check_emoji and row_0_dict['components'][2]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False
        elif row_1_dict['components'][0]['label'] == check_emoji and row_1_dict['components'][1]['label'] == check_emoji and row_1_dict['components'][2]['label'] == check_emoji:
            self.winner = check_winner
            game_status =  False
        elif row_2_dict['components'][0]['label'] == check_emoji and row_2_dict['components'][1]['label'] == check_emoji and row_2_dict['components'][2]['label'] == check_emoji:
            self.winner = check_winner
            game_status =  False
        # Col win
        elif row_0_dict['components'][0]['label'] == check_emoji and row_1_dict['components'][0]['label'] == check_emoji and row_2_dict['components'][0]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False
        elif row_0_dict['components'][1]['label'] == check_emoji and row_1_dict['components'][1]['label'] == check_emoji and row_2_dict['components'][1]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False
        elif row_0_dict['components'][2]['label'] == check_emoji and row_1_dict['components'][2]['label'] == check_emoji and row_2_dict['components'][2]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False
        # Diagonal win
        elif row_0_dict['components'][0]['label'] == check_emoji and row_1_dict['components'][1]['label'] == check_emoji and row_2_dict['components'][2]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False
        elif row_0_dict['components'][2]['label'] == check_emoji and row_1_dict['components'][1]['label'] == check_emoji and row_2_dict['components'][0]['label'] == check_emoji:
            self.winner = check_winner
            game_status = False

        # If game is finished
        if not game_status:
            for i in range(3):
                row_0_dict['components'][i]['disabled'] = True
                row_1_dict['components'][i]['disabled'] = True
                row_2_dict['components'][i]['disabled'] = True
            self.components[0] = ActionRow.from_dict(data = row_0_dict)
            self.components[1] = ActionRow.from_dict(data = row_1_dict)
            self.components[2] = ActionRow.from_dict(data = row_2_dict)

            return False

        # Check for draw
        elif (row_0_dict['components'][0]['disabled'] == True and
            row_0_dict['components'][1]['disabled'] == True and
            row_0_dict['components'][2]['disabled'] == True and
            row_1_dict['components'][0]['disabled'] == True and
            row_1_dict['components'][1]['disabled'] == True and
            row_1_dict['components'][2]['disabled'] == True and
            row_2_dict['components'][0]['disabled'] == True and
            row_2_dict['components'][1]['disabled'] == True and
            row_2_dict['components'][2]['disabled'] == True):
            self.draw = True

            for i in range(3):
                row_0_dict['components'][i]['disabled'] = True
                row_1_dict['components'][i]['disabled'] = True
                row_2_dict['components'][i]['disabled'] = True
            self.components[0] = ActionRow.from_dict(data = row_0_dict)
            self.components[1] = ActionRow.from_dict(data = row_1_dict)
            self.components[2] = ActionRow.from_dict(data = row_2_dict)

            return False

        return True

    async def init_game(self):
        self.next_player = random.choice([self.player_one, self.player_two])
        self.next_emoji = xo_x_emoji

        self.components = [
            ActionRow(
                Button(label=" ", custom_id="1"), 
                Button(label=" ", custom_id="2"), 
                Button(label=" ", custom_id="3")
            ),
            ActionRow(
                Button(label=" ", custom_id="4"), 
                Button(label=" ", custom_id="5"), 
                Button(label=" ", custom_id="6")
            ),
            ActionRow(
                Button(label=" ", custom_id="7"), 
                Button(label=" ", custom_id="8"), 
                Button(label=" ", custom_id="9")
            )
        ]

        # Send message
        self.text_header_message = f'<:game_die:960128092561637386> <@{self.player_one.id}> vs. <@{self.player_two.id}>\n\n'
        message = f'{self.text_header_message}<@{self.next_player.id}> ({self.next_emoji}), select your move:'
        embed = discord.Embed(title = xo_embed_title, description = message)

        self.game_message = await self.channel.send(embed = embed, components = self.components)

        def _check(i: discord.Interaction, b):
            return i.message.id == self.game_message.id and i.member == self.next_player
        
        while True:
            interaction, button = await self.client.wait_for('button_click', check = _check)
            button_id = button.custom_id

            await interaction.defer()
            self.mark_tile(button_id)

            result = self.check_game_status()
            if result:
                # .add_field(name='Choose', value=f'Your Choose was `{button_id}`')
                message = f'{self.text_header_message}<@{self.next_player.id}> ({self.next_emoji}), select your move:'
            else:
                if not self.draw:
                    message = f'{self.text_header_message}<@{self.winner.id}>, has won the match! Congrats <:boom:960165338408947812>'
                else:
                    message = f'{self.text_header_message}Oh, it\'s a draw! Another match?'

            embed = discord.Embed(title = xo_embed_title, description = message)
            await interaction.edit(embed = embed, components = self.components)

            if not result:
                # Remove from xo_games
                del xo_games[f'{self.player_one.id}-{self.player_two.id}']
                break

        if self.draw:
            add_game_to_history(self.player_one.id, 'd')
            add_game_to_history(self.player_two.id, 'd')
        else:
            add_game_to_history(self.winner.id, 'w')

            loser = self.player_one if self.winner == self.player_two else self.player_two
            add_game_to_history(loser.id, 'l')
        await save_ranking()

        return

# Class end

# Functions
async def xo_message_handler(message):
    channel = client.get_channel(xo_channel_id)
    if (message.content.startswith(xo_cmd_start)):
        
        if not len(message.mentions):
            await message.delete()
            await channel.send(f'<@{message.author.id}>, please mention the enemy player!')
        elif len(message.mentions) > 1:
            await message.delete()
            await channel.send(f'<@{message.author.id}>, please only mention one enemy player!')
        else:
            # Check if ongoing match exist already between players
            player_one_id = message.author.id
            player_two_id = message.mentions[0].id

            if player_one_id == player_two_id:
                await message.delete()
                await channel.send(f'<@{message.author.id}>, you can\'t start a game with yourself!')
            elif f'{player_one_id}-{player_two_id}' in xo_games.keys() or f'{player_two_id}-{player_one_id}' in xo_games.keys():
                await message.delete()
                await channel.send(f'<@{message.author.id}>, you already have an ongoing match with the same player!')
            else:
                await message.delete()
                xo_game = XoGame(client, channel, message)
                xo_games[f'{player_one_id}-{player_two_id}'] = xo_game
                await xo_game.init_game()
    else:
        await message.delete()
        await channel.send(f'<@{message.author.id}>, please use the command `/startgame @enemy` to play TicTacToe!')

    return



# Functions end

# X_O End