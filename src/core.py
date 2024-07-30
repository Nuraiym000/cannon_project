import math
import random
import sqlite3
from datetime import datetime

# Kivy components
from kivy.clock import Clock
from kivy.graphics import Rectangle, PopMatrix, PushMatrix, Rotate
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from constants import *


# Function to check collision between two rectangles defined by their positions and sizes.
def collides(rect1, rect2):
    r1x, r1y, r1w, r1h = rect1
    r2x, r2y, r2w, r2h = rect2
    return r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y



class GameWidget(Widget):

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

        # Initialize game state variables
        self.angle = 0
        self.min_angle = -45
        self.max_angle = 80
        self.bullets = []
        self.score = 0
        self.shots = 0
        self.hits = 0
        self.explosion = None
        self.explosion_duration = 0.5
        self.weapon = "cannon"
        self.time_left = GAME_TIME
        self.game_over = False
        self.timer_event = None
        self.bullet_speed = 300
   
        # Loads game assets (Rectangle objects with image sources) onto the canvas.
        with self.canvas:
            self.background = Rectangle(source="assets/bg.jpg", pos=self.pos, size=self.size)
            self.cannon = Rectangle(source="assets/cannon.png", pos=(10, 40), size=(150, 67))
            self.table = Rectangle(source="assets/cannon2.png", pos=(10, 0), size=(86, 68))
            self.pistol = Rectangle(source="assets/pistol.png", pos=(10, 40), size=(150, 50))
            self.laser_gun = Rectangle(source="assets/laser_gun.png", pos=(10, 40), size=(150, 50))
            self.target = Rectangle(source="assets/enemy.png", pos=(800, 300), size=(100, 100))
            self.stone = Rectangle(source="assets/stone.png", pos=(600, 200), size=(100, 100))
            self.mirror = Rectangle(source="assets/mirror.png", pos=(400, 250), size=(100, 100))
            self.perpetitos = [Rectangle(source="assets/perpetito.webp", pos=self.random_position(), size=(100, 100))
                               for _ in range(1)]

        # Sets up event bindings (bind) for resizing and repositioning the background.
        self.bind(size=self.update_background, pos=self.update_background)

        self.bullet_speed = 300
        self.left_rotate_event = None
        self.right_rotate_event = None

        # Schedules move_step function to be called at a specific interval.
        Clock.schedule_interval(self.move_step, 1 / FPS)

    # Generate a random position within screen boundaries
    def random_position(self):
        return (random.randint(200, SCREEN_WIDTH - 200), random.randint(200, SCREEN_HEIGHT - 200))

    # Methods to handle rotation of a cannon or other objects.

    def start_left_rotate(self, instance):
        self.stop_right_rotate(instance)
        self.left_rotate_event = Clock.schedule_interval(self.rotate_left, 0.01)

    def stop_left_rotate(self, instance):
        if self.left_rotate_event:
            self.left_rotate_event.cancel()
            self.left_rotate_event = None

    def start_right_rotate(self, instance):
        self.stop_left_rotate(instance)
        self.right_rotate_event = Clock.schedule_interval(self.rotate_right, 0.01)

    def stop_right_rotate(self, instance):
        if self.right_rotate_event:
            self.right_rotate_event.cancel()
            self.right_rotate_event = None

    # Methods to adjust the angle of rotation (angle) incrementally.

    def rotate_left(self, dt):
        self.angle = max(self.angle - 1, self.min_angle)
        self.update_canvas()

    def rotate_right(self, dt):
        self.angle = min(self.angle + 1, self.max_angle)
        self.update_canvas()

    # Bullet Shooting, Depending on the current weapon selected (cannon, pistol, laser), shoots bullets (Rectangle objects) with specified velocities and positions.
    def shoot_bullet(self, instance):
        if self.game_over:
            return

        self.shots += 1
        angle_rad = math.radians(self.angle)
        bullet_velocity = (self.bullet_speed * math.cos(angle_rad),
                           self.bullet_speed * math.sin(angle_rad))
        if self.weapon == "cannon":
            bullet_start_x = self.cannon.pos[0] + self.cannon.size[0] / 2 + math.cos(angle_rad) * self.cannon.size[
                0] / 2
            bullet_start_y = self.cannon.pos[1] + self.cannon.size[1] / 2 + math.sin(angle_rad) * self.cannon.size[
                0] / 2
            bullet = {
                'rect': Rectangle(source="assets/ball.png", pos=(bullet_start_x, bullet_start_y), size=(35, 35)),
                'velocity': bullet_velocity,
                'type': 'cannon'
            }
        elif self.weapon == "pistol":
            bullet_start_x = self.pistol.pos[0] + self.pistol.size[0] / 2 + math.cos(angle_rad) * self.pistol.size[
                0] / 2
            bullet_start_y = self.pistol.pos[1] + self.pistol.size[1] / 2 + math.sin(angle_rad) * self.pistol.size[
                0] / 2
            bullet = {
                'rect': Rectangle(source="assets/bullet.png", pos=(bullet_start_x, bullet_start_y), size=(30, 20)),
                'velocity': (PISTOL_BULL * math.cos(angle_rad), PISTOL_BULL * math.sin(angle_rad)),
                'angle': self.angle,
                'type': 'pistol'
            }
        elif self.weapon == "laser":
            bullet_start_x = self.laser_gun.pos[0] + self.laser_gun.size[0] / 2 + math.cos(angle_rad) * self.laser_gun.size[0] / 2
            bullet_start_y = self.laser_gun.pos[1] + self.laser_gun.size[1] / 2 + math.sin(angle_rad) * self.laser_gun.size[0] / 2
            bullet = {
                'rect': Rectangle(source="assets/sticker.webp", pos=(bullet_start_x, bullet_start_y),
                                  size=(30, 20)),
                'velocity': (LASER_VEL * math.cos(angle_rad), LASER_VEL * math.sin(angle_rad)),
                'angle': self.angle,
                'type': 'laser'
            }
        
        self.bullets.append(bullet)
        self.update_labels()  # Update the labels each time a bullet is shot

    

# Collision Handling method: Updates the position of bullets, checks for collisions 
# with various game objects (target, stone, mirror, perpetitos), and 
# triggers appropriate actions (on_target_hit, on_stone_hit, on_mirror_hit).
    def move_step(self, dt):
        if self.game_over:
            return

        new_bullets = []
        for bullet in self.bullets:
            if bullet['type'] == "cannon":
                bullet['velocity'] = (bullet['velocity'][0], bullet['velocity'][1] + GRAVITY * dt)
            bullet['rect'].pos = (bullet['rect'].pos[0] + bullet['velocity'][0] * dt,
                                  bullet['rect'].pos[1] + bullet['velocity'][1] * dt)
            bullet_rect = bullet['rect'].pos + bullet['rect'].size
            if collides(bullet_rect, self.target.pos + self.target.size):
                self.on_target_hit(bullet['rect'].pos)
            elif collides(bullet_rect, self.stone.pos + self.stone.size):
                if bullet['type'] == "cannon":
                    self.on_stone_hit(bullet['rect'].pos)
                elif bullet['type'] == "pistol":
                    bullet['type'] = "pistol_hit_stone"
                    new_bullets.append(bullet)
            elif collides(bullet_rect, self.mirror.pos + self.mirror.size):
                if bullet['type'] == "laser":
                    bullet['velocity'] = (-bullet['velocity'][0], bullet['velocity'][1])
                    new_bullets.append(bullet)
                else:
                    self.on_mirror_hit(bullet['rect'].pos)
            elif any(collides(bullet_rect, perpetito.pos + perpetito.size) for perpetito in self.perpetitos):
                continue
            else:
                new_bullets.append(bullet)

        self.bullets = new_bullets
        self.update_canvas()


# Event Handlers (on_target_hit, on_stone_hit, on_mirror_hit), Methods that handle events when bullets collide with specific game objects (target, stone, mirror). 
# They update game state variables (score, hits), trigger visual effects (explosion), and respawn objects.
    def on_target_hit(self, pos):
        self.score += 1
        self.hits += 1
        self.update_labels()
        self.explosion = {'pos': pos, 'time': Clock.get_time()}
        Clock.schedule_once(self.clear_explosion, self.explosion_duration)
        self.respawn_target()

    def on_stone_hit(self, pos):
        self.explosion = {'pos': pos, 'time': Clock.get_time()}
        Clock.schedule_once(self.clear_explosion, self.explosion_duration)
        self.respawn_stone()

    def on_mirror_hit(self, pos):
        self.explosion = {'pos': pos, 'time': Clock.get_time()}
        Clock.schedule_once(self.clear_explosion, self.explosion_duration)
        self.respawn_mirror()

    def clear_explosion(self, dt):
        self.explosion = None

    def respawn_target(self):
        self.target.pos = self.random_position()

    def respawn_stone(self):
        self.stone.pos = self.random_position()

    def respawn_mirror(self):
        self.mirror.pos = self.random_position()

    def respawn_perpetitos(self):
        for perpetito in self.perpetitos:
            perpetito.pos = self.random_position()

# Clears and redraws the game canvas with updated positions of game objects, bullets, and visual effects.
    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            self.background = Rectangle(source="assets/bg.jpg", pos=self.pos, size=self.size)
            if self.weapon == "cannon":
                self.canvas.add(self.table)
            self.target = Rectangle(source="assets/enemy.png", pos=self.target.pos, size=self.target.size)
            self.stone = Rectangle(source="assets/stone.png", pos=self.stone.pos, size=self.stone.size)
            self.mirror = Rectangle(source="assets/mirror.png", pos=self.mirror.pos, size=self.mirror.size)
            for perpetito in self.perpetitos:
                self.canvas.add(perpetito)
            for bullet in self.bullets:
                with self.canvas.before:
                    PushMatrix()
                    Rotate(angle=bullet.get('angle', 0), origin=(bullet['rect'].pos[0], bullet['rect'].pos[1]))
                    self.canvas.add(bullet['rect'])
                    PopMatrix()
            if self.explosion:
                self.canvas.add(Rectangle(source="assets/explosion.png", pos=self.explosion['pos'], size=(100, 100)))
            PushMatrix()
            Rotate(angle=self.angle,
                   origin=(self.cannon.pos[0] + self.cannon.size[0] / 2, self.cannon.pos[1] + self.cannon.size[1] / 2))
            if self.weapon == "cannon":
                self.canvas.add(self.cannon)
            elif self.weapon == "pistol":
                self.canvas.add(self.pistol)
            elif self.weapon == "laser":
                self.canvas.add(self.laser_gun)
            PopMatrix()

# Adjusts the size and position of the background based on window size changes.
    def update_background(self, *args):
        self.background.size = self.size
        self.background.pos = self.pos


# Weapon Selection (set_weapon), Changes the current weapon (cannon, pistol, laser) and updates bullet speed accordingly.
    def set_weapon(self, weapon):
        self.weapon = weapon
        self.update_canvas()
     
    def set_custom_velocity(self, velocity):
        try:
            self.bullet_speed = int(velocity)
        except ValueError:
            self.bullet_speed = 300  # Default value if input is invalid
        self.update_canvas()


# Game Flow 

# Updates the game timer and handles game-over conditions.
    def update_time(self, dt):
        if self.game_over:
            return

        self.time_left -= 1
        self.timer_label.text = f"Time: {self.time_left}s"

        if self.time_left <= 0:
            self.game_over = True
            self.save_score()

# Saves the player's score, shots, hits, and accuracy in a database.
    def save_score(self):
        accuracy = self.hits / self.shots if self.shots > 0 else 0
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                          (id INTEGER PRIMARY KEY, score INTEGER, date TEXT, shots INTEGER, hits INTEGER, accuracy REAL)''')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO scores (score, date, shots, hits, accuracy) VALUES (?, ?, ?, ?, ?)',
                       (self.score, current_time, self.shots, self.hits, accuracy))
        conn.commit()
        conn.close()
        self.timer_label.text = "Game Over!"
        self.show_game_over()

# Displays a popup with game-over message and options to restart or return to the menu.
    def show_game_over(self):
        content = FloatLayout()
        game_over_label = Label(text="Game Over!", size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.7},
                                font_size='30sp', color=(1, 0, 0, 1))
        content.add_widget(game_over_label)

        restart_button = Button(text="Restart", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.3, 'center_y': 0.4})
        restart_button.bind(on_press=self.restart_game)
        content.add_widget(restart_button)

        menu_button = Button(text="Menu", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.7, 'center_y': 0.4})
        menu_button.bind(on_press=self.return_to_menu)
        content.add_widget(menu_button)

        self.popup = Popup(title='', content=content, size_hint=(None, None), size=(400, 300), auto_dismiss=False)
        self.popup.open()

# Methods to restart the game or return to the main menu.
    def restart_game(self, instance):
        self.stop_game()  # Stop the previous timer before restarting
        self.popup.dismiss()
        self.clear_widgets()
        self.__init__(self.screen_manager)
        self.start_game()

    def return_to_menu(self, instance):
        self.stop_game()  # Stop the timer when returning to the menu
        self.popup.dismiss()
        self.screen_manager.current = 'menu'

# Methods to start and stop the game loop and timer.
    def start_game(self):
        self.game_over = False
        self.time_left = GAME_TIME
        self.score = 0
        self.shots = 0
        self.hits = 0
        self.update_labels()
        self.timer_event = Clock.schedule_interval(self.update_time, 1)
        self.update_canvas()

    def stop_game(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def update_labels(self):
        self.score_label.text = f"Score: {self.score} | Shots: {self.shots}"


