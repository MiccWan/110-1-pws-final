import random


from .CONST import StandMaxLevel

from .lib.GridImpl import make_grids
from .lib.EventImpl import make_event_cards
from .lib.TechImpl import make_tech_cards
from .lib.Grid import *
from .lib.Player import Player
from .lib.Character import characters

class Game:
    def __init__(self):
        self.turn = 0

    # ############################################################
    #  getter
    # ############################################################

    @property
    def current_player(self):
        return self.players[self.turn]

    # ############################################################
    #  init
    # ############################################################

    def init(self, player_amount):
        self.init_players(player_amount)
        self.init_grids()
        self.init_events()
        self.init_techs()

    def init_grids(self):
        self.grids = make_grids()

        for grid in self.grids:
            grid.game = self
            grid.init()

    def init_players(self, player_amount):
        char_ids = list(range(len(characters)))
        random.shuffle(char_ids)
        char_ids = char_ids[:player_amount]
        # char_ids = [1, 2]
        self.players = [Player(index, char_id) for (index, char_id) in enumerate(char_ids)]

        self.players_by_char = [None] * 4
        for player in self.players:
            player.game = self
            player.init()

    def init_events(self):
        self.event_cards = make_event_cards()

        for event in self.event_cards:
            event.game = self

        self.reshuffle_events()

    def reshuffle_events(self):
        self.event_pointer = 0
        random.shuffle(self.event_cards)

    def init_techs(self):
        self.tech_cards = make_tech_cards()

        for tech in self.tech_cards:
            tech.game = self

        self.tech_pointer = 0
        random.shuffle(self.tech_cards)

    # ############################################################
    #  game play helper
    # ############################################################

    def player_exists(self, player_id):
        return 0 <= player_id and player_id < len(self.players)

    def draw_event_card(self):
        card = self.event_cards[self.event_pointer]
        self.event_pointer += 1
        if self.event_pointer >= len(self.event_cards):
            self.reshuffle_events()
        return card

    def draw_tech_card(self):
        if self.tech_pointer >= len(self.event_cards):
            print(Exception('[Game.draw_tech_card] tech cards empty'))
            return
        card = self.tech_cards[self.tech_pointer]
        self.tech_pointer += 1
        return card

    def is_end(self):
        return self.tech_pointer >= len(self.tech_cards)

    def player_transfer_money(self, receiver_id, giver_id, amount):
        receiver = self.players[receiver_id]
        giver = self.players[giver_id]
        amount = min(amount, giver.money)
        receiver.alter_money(amount)
        giver.alter_money(-amount)

    def get_stand_profit(self, grid_id, triggerer_id):
        stand = self.grids[grid_id]
        triggerer = self.players[triggerer_id]
        owner = stand.owner
        if owner == None:
            raise Exception(f'Cannot get profit of stand {stand.name} with no owner')
        return stand.prices.profit[stand.level] - triggerer.stand_fee_discount + owner.extra_stand_fee

    def profit_stand(self, grid_id, triggerer_id):
        stand = self.grids[grid_id]
        owner = stand.owner
        if owner == None:
            raise Exception(f'Cannot profit stand {stand.name} with no owner')
        owner.alter_money(self.get_stand_profit(grid_id, triggerer_id))

    def get_stand_buy_price(self, player_id, grid_id):
        stand = self.grids[grid_id]
        return stand.prices.buy

    def get_stand_build_price(self, player_id, grid_id):
        player = self.players[player_id]
        stand = self.grids[grid_id]
        return stand.prices.build - player.build_discount

    def ask_for_build_table(self, player_id, stand_id):
        player = self.players[player_id]
        stand = self.grids[stand_id]
        price = self.get_stand_build_price(player_id, stand_id)

        # sanity check
        if stand.owner_id != player_id:
            print(Exception(f'[Game.ask_for_build_table] player "{player.name}" does not own stand {stand.name}'))

        if stand.level >= StandMaxLevel:
            confirm("????????????", f"{stand.name}????????????????????????????????????????????????????????????")
            return

        if player.money >= price or player.free_table:
            result = yesno("????????????", f"????????? {price} ??????{stand.name}??????????????????")
            if result:
                self.build_stand(player_id, stand_id)

                # handle double table tech
                if player.double_table:
                    if player.money < price:
                        confirm("????????????", f"[???????????????] ??????????????????\n ??????????????????????????????????????? {price} ????????????{stand.name}?????????????????????")
                    elif stand.level >= StandMaxLevel:
                        confirm("????????????", f"[???????????????] ??????????????????\n {stand.name}????????????????????????????????????????????????????????????")
                    else:
                        result = yesno("????????????", f"[???????????????] ??????????????????\n ???????????? {price} ??????{stand.name}?????????????????????")
                        if result:
                            self.build_stand(player_id, stand_id)
        else:
            confirm("????????????", f"??????????????????????????????????????? {price} ????????????{stand.name}??????????????????")

    def ask_for_buy_stand(self, player_id, stand_id):
        player = self.players[player_id]
        stand = self.grids[stand_id]
        owner_msg = ''
        if stand.owner_id != None:
            owner_msg = f"??? {stand.owner.name} "
        if player.money >= self.get_stand_buy_price(player_id, stand_id):
            result = yesno("????????????", f"????????? {stand.prices.buy} ???{owner_msg}??????{stand.name}")
            if result:
                self.buy_stand(player_id, stand_id)
        else:
            confirm("????????????", f"??????????????????????????????????????? {stand.prices.buy} ??????{stand.name}")

    def pass_kitchen(self, player_id):
        player = self.players[player_id]

        if player.idle_kitchen:
            player.idle_kitchen -= 1
            confirm("??????????????????", "???????????????????????????????????????")
            return

        price = player.get_tech_invent_price()
        income = player.get_income()
        if player.money >= price:
            result = yesno("??????????????????", f"???????????????????????????????????????????????? {income} ??????")
            if result:
                self.invent_tech(player_id)
                return
        player.alter_money(income)
        confirm("??????????????????", f"???????????? {income} ???")

    def buy_stand(self, player_id, grid_id):
        player = self.players[player_id]
        stand = self.grids[grid_id]
        owner = stand.owner
        if player.money < self.get_stand_buy_price(player_id, grid_id):
            print(Exception(f'[Game.buy_stand] Player {player.name} cannot afford buying stand {stand.name}'))
        stand.owner_id = player.id
        player.alter_money(-stand.prices.buy)
        if owner:
            owner.alter_money(stand.prices.buy)

    def build_stand(self, player_id, grid_id):
        player = self.players[player_id]
        stand = self.grids[grid_id]
        price = self.get_stand_build_price(player_id, grid_id)

        # sanity check
        if player.money < price and not player.free_table:
            print(Exception(f'[Game.build_stand] Player {player.name} cannot afford building stand {stand.name}'))

        if stand.level == StandMaxLevel:
            print(Exception(f'[Game.build_stand] Stand {stand.name} already at max level'))

        stand.level += 1

        if player.free_table:
            player.free_table -= 1
            confirm('??????????????????', '[???????????????] ????????????????????????!')
        else:
            player.alter_money(-price)

    def invent_tech(self, player_id):
        player = self.players[player_id]
        card = self.draw_tech_card()
        player.alter_money(-player.get_tech_invent_price())
        confirm("???????????????", f"[{card.score}???] {card.tech_description}???\n{card.ability_description}")
        card.trigger(player)
        player.tech_invented.append(card)

    def next_turn(self):
        game.turn = (game.turn + 1) % len(self.players)

    def random_remove_table(self, player_id):
        player = self.players[player_id]
        stands = player.own_stands
        random.shuffle(stands)
        for stand in stands:
            if stand.level > 0:
                confirm("????????????", f"{stand.name}??????????????????????????????")
                stand.level -= 1
                return stand
        else:
            confirm("????????????", "??????????????????????????????")
            return None

    def switch_position(self, player_id_1, player_id_2):
        player_1 = self.players[player_id_1]
        player_2 = self.players[player_id_2]
        player_1.position, player_2.position = player_2.position, player_1.position


game = Game()