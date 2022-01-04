from os import path

from game.game import game
from game.CONST import *
from game.lib.Character import characters

from ...CONST import *
from ...componentLib.ComponentBase import ComponentBase

from .gridHelper import grid_coord


class Grid(ComponentBase):
    def init(self, grid):
        self.id = grid.id
        self.border = self.children.create_component('Rectangle', BoxSize, BoxSize, *grid_coord(self.id))

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
        self.background = self.children.create_component('Rectangle', BoxSize, BoxSize, x, y, pygame.Color('white'), border_width=0, first=True)
        self.name_label = self.children.create_component('Text', self.grid.name, 'Small', center=(x + BoxSize / 2, y + 15))
        self.children.create_component('Text', str(self.grid.prices.buy), 'Small', center=(x + BoxSize / 2, y + BoxSize - 15))
        self.children.create_component('Image', path.join(ImageFolder, f'{grid.name}.png'), center=(x + BoxSize / 2, y + BoxSize / 2))

    def update(self):
        self.name_label.content = self.grid.name + (f'({self.grid.level})' if self.grid.level else '')
        if self.grid.owner != None:
            self.background.color = self.grid.owner.color_light


class EffectGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', '效果', 'Small', center=(x + BoxSize / 2, y + BoxSize / 3))
        self.children.create_component('Text', self.grid.name, 'Small', center=(x + BoxSize / 2, y + BoxSize * 2 / 3))


class EventGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', '經營卡', 'Small', center=(x + BoxSize / 2, y + BoxSize / 2))


class MainKitchenGrid(Grid):
    def init(self, grid):
        super().init(grid)
        (x, y) = self.grid_padding
        self.children.create_component('Text', '中央廚房', 'Small', center=(x + BoxSize / 2, y + BoxSize * 1 / 2))
        self.children.create_component('Text', characters[self.grid.character_id].name, 'Small', center=(x + BoxSize / 2, y + BoxSize * 3 / 4))

    @property
    def player(self):
        return game.players_by_char[self.grid.character_id]
