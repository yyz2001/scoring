from random import randint

import pygame
from pygame.sprite import Sprite

random_number = randint(-10, 10)


class Star(Sprite):
    def __init__(self, ai_game):
        """初始化星星并设置其起始位置。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # 加载星星图像并设置其rect属性。
        self.image = pygame.image.load('images/stars.png')
        self.rect = self.image.get_rect()

        # 每个星星最初都在屏幕左上角附近。
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 存储星星的精确水平位置。
        self.x = float(self.rect.x)