import pygame

from pygame.sprite import Sprite


class Ship(Sprite):
    """管理飞船的类。"""

    def __init__(self, ai_game):
        """初始化飞船并设置其初始位置。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # 加载飞船图像并获取其外接矩形。
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # 对于每艘新飞船，都将其放在屏幕底部的中央。
        # self.rect.midbottom = self.screen_rect.midbottom
        self.rect.midleft = self.screen_rect.midleft

        # 在飞船中的属性x中存储小数值。
        self.x = float(self.rect.x)

        # 在飞船中的属性y中存储小数值。
        self.y = float(self.rect.y)

        # 移动标志。
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """根据移动标志调整飞船位置。"""
        # 更新飞船而不是rect对象的x值。
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 更新飞船而不是rect对象的y值
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed

        # 根据self.x更新rect对象。
        self.rect.x = self.x

        # 根据self.y更新rect对象
        self.rect.y = self.y

    def blitme(self):
        """在指定位置绘制飞船。"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """让飞船在屏幕底部边缘"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.midleft = self.screen_rect.midleft
        # self.x = float(self.rect.x)
        # self.x = 0
        # self.y = 750
        # self.rect.bottomleft = self.screen_rect.bottomleft
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)