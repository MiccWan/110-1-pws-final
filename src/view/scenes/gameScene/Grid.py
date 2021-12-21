from game.game import game

from ...CONST import *
from ...componentLib.ComponentBase import ComponentBase
from ..basicComponents.Rectangle import Rectangle
from ..basicComponents.Text import Text

from .gridHelper import grid_coord


class Grid(ComponentBase):
    def init(self, grid):
        self.id = grid.id
        self.box_color = DefaultBoxColor
        self.children.create_component('Rectangle', BoxSize, BoxSize, *grid_coord(self.id), self.box_color)

    @property
    def grid(self):
        return game.grids[self.id]

    @property
    def grid_padding(self):
        return grid_coord(self.id)


class FoodStandGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', self.grid.name, 'Small', (x + BoxSize / 2, y + BoxSize / 2))
        self.children.create_component('Text', str(self.grid.price.buy), 'Small', (x + BoxSize / 2, y + BoxSize * 3 / 4))


class EffectGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', 'Effect', 'Small', (x + BoxSize / 2, y + BoxSize / 2))
        self.children.create_component('Text', self.grid.effect_type, 'Small', (x + BoxSize / 2, y + BoxSize * 3 / 4))


class EventGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', '抽一張經營卡', 'Small', (x + BoxSize / 2, y + BoxSize / 2))


class MainKitchenGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', '中央廚房', 'Small', (x + BoxSize / 2, y + BoxSize * 1 / 2))
        self.children.create_component('Text', self.player.name, 'Small', (x + BoxSize / 2, y + BoxSize * 2 / 3))

    @property
    def player(self):
        return game.players[self.grid.player_id]