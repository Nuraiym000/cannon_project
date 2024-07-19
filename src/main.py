import sqlite3 

from kivy.app import App #App Base class for creating Kivy applications.
from kivy.clock import Clock #Clock: Allows scheduling of function calls.
from kivy.core.window import Window #Window: Provides access to window properties and methods.

# Kivy UI components and screen management tools.
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition #NoTransition: A screen transition class that disables transitions between screens.

from constants import *
from core import GameWidget 
from storage import create_table 

# Set the initial size of the application window based on constants defined in constants.py.
Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)


file = open("src/help_text.txt", "r")

# MainMenuScreen Contains buttons for starting a game, continuing a game, viewing high scores, and accessing help.
# Methods like start_game, continue_game, show_high_scores, show_help handle button presses to switch screens or start game logic.
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        start_button = Button(text="Start Game", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.7})
        start_button.bind(on_press=self.start_game)
        layout.add_widget(start_button)

        self.continue_button = Button(text="Continue Game", size_hint=(0.2, 0.1),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.continue_button.bind(on_press=self.continue_game)
        layout.add_widget(self.continue_button)

        high_scores_button = Button(text="High Scores", size_hint=(0.2, 0.1),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.3})
        high_scores_button.bind(on_press=self.show_high_scores)
        layout.add_widget(high_scores_button)

        help_button = Button(text="Help", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.1})
        help_button.bind(on_press=self.show_help)
        layout.add_widget(help_button)

        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.get_screen('game').game_widget.start_game()
        self.manager.current = 'game'

    def continue_game(self, instance):
        if self.manager.get_screen('game').game_widget.time_left > 0:
            self.manager.get_screen('game').game_widget.game_over = False
            self.manager.get_screen('game').game_widget.timer_event = Clock.schedule_interval(
                self.manager.get_screen('game').game_widget.update_time, 1)
            self.manager.current = 'game'

    def show_high_scores(self, instance):
        self.manager.current = 'high_scores'

    def show_help(self, instance):
        self.manager.current = 'help'


# HighScoresScreen Displays high scores fetched from an SQLite database (scores.db).
# Uses update_scores to query and display top scores.
# Includes a back button (go_back) to return to the main menu.
class HighScoresScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.scores_label = Label(text="High Scores", size_hint=(None, None),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.8}, font_size='20sp')
        layout.add_widget(self.scores_label)

        back_button = Button(text="Back", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)
        self.update_scores()

    def go_back(self, instance):
        self.manager.current = 'menu'

    def update_scores(self):
        try:
            conn = sqlite3.connect('scores.db')
            cursor = conn.cursor()
            cursor.execute(
                'SELECT score, date, shots, hits, accuracy FROM scores ORDER BY accuracy DESC, score DESC LIMIT 10')
            scores = cursor.fetchall()
            conn.close()

            scores_text = "High Scores:\n\n"
            for i, (score, date, shots, hits, accuracy) in enumerate(scores):
                scores_text += f"{i + 1}. Score: {score}, Date: {date}, Shots: {shots}, Hits: {hits}, Accuracy: {accuracy:.2f}\n"

            self.scores_label.text = scores_text
        except sqlite3.OperationalError:
            self.scores_label.text = "No scores available."


# HelpScreen Provides instructions on how to play the game.
# Includes a back button (go_back) to return to the main menu.
class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        help_text = file.read()
        file.close()
        help_label = Label(text=help_text, size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout.add_widget(help_label)

        back_button = Button(text="Back", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.1})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'menu'


# GameScreen Integrates GameWidget, which handles the actual game logic and rendering.
# Displays labels for score, timer, and weapon selection.
# Provides buttons for controlling game actions (rotate, shoot).
# Includes a back button (back_to_menu) to return to the main menu.
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.game_widget = GameWidget(screen_manager=self.manager)
        layout.add_widget(self.game_widget)

        score_label = Label(text="Score: 0 | Shots: 0", size_hint=(None, None), pos_hint={'x': 0.4, 'y': 0.1},
                            font_size='20sp', color=(1, 0, 0, 1))
        self.game_widget.score_label = score_label
        layout.add_widget(score_label)

        timer_label = Label(text=f"Time: {GAME_TIME}s", size_hint=(None, None), pos_hint={'x': 0.1, 'y': 0.9},
                            font_size='20sp', color=(1, 1, 1, 1))
        self.game_widget.timer_label = timer_label
        layout.add_widget(timer_label)

        weapon_select_label = Label(text="Select Weapon:", size_hint=(None, None), pos_hint={'x': 0.4, 'y': 0.9},
                                    font_size='20sp', color=(1, 1, 1, 1))
        layout.add_widget(weapon_select_label)

        cannon_button = Button(text="Cannon", size_hint=(0.1, 0.1), pos_hint={'x': 0.2, 'y': 0.8})
        cannon_button.bind(on_press=lambda x: self.game_widget.set_weapon("cannon"))
        layout.add_widget(cannon_button)

        pistol_button = Button(text="Pistol", size_hint=(0.1, 0.1), pos_hint={'x': 0.4, 'y': 0.8})
        pistol_button.bind(on_press=lambda x: self.game_widget.set_weapon("pistol"))
        layout.add_widget(pistol_button)

        laser_button = Button(text="Laser", size_hint=(0.1, 0.1), pos_hint={'x': 0.6, 'y': 0.8})
        laser_button.bind(on_press=lambda x: self.game_widget.set_weapon("laser"))
        layout.add_widget(laser_button)

        left_button = Button(text="<", size_hint=(0.1, 0.1), pos_hint={'right': 1, 'y': 0})
        left_button.bind(on_press=self.game_widget.start_left_rotate)
        left_button.bind(on_release=self.game_widget.stop_left_rotate)
        layout.add_widget(left_button)

        shoot_button = Button(text="Shoot", size_hint=(0.1, 0.1), pos_hint={'right': 0.9, 'y': 0})
        shoot_button.bind(on_press=self.game_widget.shoot_bullet)
        layout.add_widget(shoot_button)

        right_button = Button(text=">", size_hint=(0.1, 0.1), pos_hint={'right': 0.8, 'y': 0})
        right_button.bind(on_press=self.game_widget.start_right_rotate)
        right_button.bind(on_release=self.game_widget.stop_right_rotate)
        layout.add_widget(right_button)

        back_button = Button(text="Back to Menu", size_hint=(0.2, 0.1), pos_hint={'x': 0.8, 'y': 0.9})
        back_button.bind(on_press=self.back_to_menu)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.game_widget.screen_manager = self.manager

    def back_to_menu(self, instance):
        self.game_widget.stop_game()
        self.manager.current = 'menu'


# MyApp Class (Kivy Application) build method sets up and returns the ScreenManager.
# Calls create_table() to initialize the SQLite database.
# Adds instances of MainMenuScreen, GameScreen, HighScoresScreen, and HelpScreen to the ScreenManager.
class MyApp(App):
    def build(self):
        create_table()

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(HighScoresScreen(name='high_scores'))
        sm.add_widget(HelpScreen(name='help'))
        return sm

# Entry point of the application. Creates an instance of MyApp and starts the Kivy application loop.
if __name__ == "__main__":
    app = MyApp()
    app.run()

