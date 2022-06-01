import sys
sys.path.append("E:/python/python/Lib/site-packages")
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star
from random import randint


class AlienInvasion:
    """管理游戏资源和行为的类."""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()

        # 全屏运行游戏
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # 创建一个用于存储游戏统计信息的实例
        #   并创建记分牌。
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        """将飞船绘制到屏幕上"""
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()

        self.stars = pygame.sprite.Group()
        self._create_starry()
        self._create_fleet()

        # 创建Play按钮。
        self.play_button = Button(self, "Play")

    def run_game(self):

        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._end_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """点击play按钮开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设定。
            self.settings.initialize_dynamic_settings()

            # 重置游戏统计信息。
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # 清空余下的外星人和子弹。
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人并让飞船居中。
            self._create_fleet()
            self.ship.center_ship()

            # 进入无敌模式五秒
            # self.activate_super_mode()

            # 隐藏鼠标光标。
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应按键."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            self._end_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应松开。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets。"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹。"""
        # 更新子弹的位置。
        self.bullets.update()

        # 删除消失的子弹。
        for bullet in self.bullets.copy():
            # if bullet.rect.bottom <= 0:
            if bullet.rect.right >= self.ship.screen_rect.right:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人碰撞。"""
        # 删除发生碰撞的子弹和外星人。
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        # 有外星人被击落，更新得分。
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # 删除现有的子弹并新建一群外星人。
            self.bullets.empty()
            self.ship.center_ship()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级。
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        检查是否有外星人位于屏幕边缘
          并更新整群外星人的位置。
        """
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞。
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检测外星人是否到达屏幕底部。
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端。"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.left <= screen_rect.left:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ships_left > 0:
            # 将ships_left减1并更新记分牌。
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空余下的外星人和子弹。
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新外星人，并将飞船放置到屏幕底部中央。
            self.ship.center_ship()
            self._create_fleet()

            # 暂停。
            sleep(1)


        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """创建外星人群。"""
        # 创建一个外星人并计算一行可容纳多少外星人。
        # 外星人的间距为外星人宽度。
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_y = self.settings.screen_width - (2 * alien_width)
        number_aliens_y = available_space_y // (4 * alien_width)

        # 计算屏幕可容纳多少行外星人。
        ship_height = self.ship.rect.height
        available_space_x = (self.settings.screen_height - alien_height + ship_height)
        number_rows = available_space_x // (4 * alien_height)

        # 创建外星人群。
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_y):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其放在当前行。"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        # alien.y = alien.rect.height + 2 * alien.rect.height * row_number
        alien.y = self.settings.screen_height - (3 * alien_height * row_number) - 5 * alien_height
        alien.rect.y = alien.y
        alien.rect.x = self.settings.screen_width - (2 * alien_width * alien_number) - 3 * alien_width
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施。"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人右移，并改变它们的方向。"""
        for alien in self.aliens.sprites():
            alien.rect.x -= self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """更新屏幕上图像，并切换到新屏幕。"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.stars.draw(self.screen)
        # 显示得分。
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Plau按钮。
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _create_starry(self):
        """ 创建星群 """
        # 创建一个星星并计算一行可容纳多少个星星
        star = Star(self)
        star_width, star_height = star.rect.size
        # 屏幕x方向左右各预留一个星星宽度
        self.availiable_space_x = self.screen.get_rect().width - (2 * star_width)
        # 星星的间距为星星宽度的4倍
        number_stars_x = self.availiable_space_x // (5 * star_width) + 1

        # 计算屏幕可容纳多少行星星
        # 屏幕y方向上下各预留一个星星宽度
        self.availiable_space_y = self.screen.get_rect().height - (2 * star_height)
        # 星星的间距为星星高度的4倍
        number_rows = self.availiable_space_y // (5 * star_height) + 1

        # 创建星群
        for row_number in range(number_rows):
            for star_number in range(number_stars_x):
                self._create_star(star_number, row_number)

    def _create_star(self, star_number, row_number):
        # 创建一个星星并将其加入到当前行
        star = Star(self)
        star.rect.x = randint(0, self.availiable_space_x)
        star.rect.y = randint(0, self.availiable_space_y)
        self.stars.add(star)

    def _end_game(self):
        """保存最高分数记录并关闭游戏"""
        self.stats.save_high_score()
        sys.exit()



if __name__ == '__main__':
    # 创建游戏实例并运行游戏.
    ai = AlienInvasion()
    ai.run_game()