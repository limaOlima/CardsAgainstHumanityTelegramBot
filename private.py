import random

from main import send_choice_to_czar, get_current_black_card, send_cards_choice_to_user, czar_round, \
    create_cards_choice_czar_dict, game_loop, send_message_to_players
from stats import *
from util import is_user_czar, format_msg
from emoji import emojize

point_right = emojize(":point_right:", use_aliases=True)
grin = emojize(":grin:", use_aliases=True)
wave = emojize(":wave:", use_aliases=True)
drum = emojize(":drum:", use_aliases=True)
glass = "\U0001f942"



def start(update, context):


    if update.effective_chat.type == "private":
        msg = format_msg(f'''
                Hello Human! I am the

                *Cards Against Humanity Bot*
                v{version}!!

                Feel free to create feature or issue requests on
                *github.com/ApfelPresse/CardsAgainstHumanityTelegramBot*
            ''')
        msg2 = format_msg(f'''{point_right} *Go back to the group now* and
        join a game with /join {glass} or
        create a new game with /create {drum} !''')

        print(msg2)

        user_id = update.effective_user.id
        if user_id not in user_ids:
            user_ids[user_id] = {
                "info": json.loads(update.effective_user.to_json())
            }
            player_to_private_chat_id[user_id] = update.effective_chat.id
            send_return_back_to_game[user_id] = []
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg2)

        return

    msg = format_msg(f'''
        Send me a *private* message! (/start), please...
    ''')
    context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)


def check_if_choose_was_correct(game_id, user_id, choose):
    current_game = games[game_id]
    player_cards = current_game["cards"][user_id]

    for card in player_cards:
        if choose == decks["whiteCards"][card]:
            return card
    return -1


def get_user_id_from_choice(game_id, choice):
    czar_choices = create_cards_choice_czar_dict(game_id)
    inv_map_czar_choices = {v: k for k, v in czar_choices.items()}
    try:
        return inv_map_czar_choices[choice]
    except:
        return -1


def callback(update, context):
    if update.effective_chat.type == "private":
        user_id = update.effective_user.id
        if user_id in send_return_back_to_game and len(send_return_back_to_game[user_id]) != 0:
            game_id = send_return_back_to_game[user_id].pop(0)
            choice = update["message"]["text"]

            if is_user_czar(game_id, user_id) and czar_round(game_id):
                user_id_choice = get_user_id_from_choice(game_id, choice)
                if user_id_choice == -1:
                    send_choice_to_czar(update, context, game_id)
                    return
                current_game = games[game_id]
                current_game["scores"][user_id_choice] += 1
                player_name_score = user_ids[user_id_choice]["info"]["first_name"]

                back_card_text = get_current_black_card(game_id)['text']
                msg = format_msg(f'''
                        Czar chose..
                        *{back_card_text}*
                        {choice}

                        Player {player_name_score} gets a point!
                ''')
                send_message_to_players(update, context, game_id, msg)
                game_loop(update, context, game_id)
                return

            card_choice = check_if_choose_was_correct(game_id, user_id, choice)
            if card_choice == -1:
                send_cards_choice_to_user(update, context, game_id, user_id)

            current_game = games[game_id]
            current_game["card_choice"][user_id].append(card_choice)

            if czar_round(game_id):
                czar_possible_choices = create_cards_choice_czar_dict(game_id)
                msg = "All players have chosen their cards!\n"
                choices = list(czar_possible_choices.values())
                random.shuffle(choices)
                for c in choices:
                    msg += c + "\n"
                send_message_to_players(update, context, game_id, msg)
                send_choice_to_czar(update, context, game_id)
            else:
                how_many_cards_to_choose = get_current_black_card(game_id)["pick"]
                how_many_cards_did_player_choose = len(current_game["card_choice"][user_id])
                if how_many_cards_did_player_choose < how_many_cards_to_choose:
                    send_cards_choice_to_user(update, context, game_id, user_id)
