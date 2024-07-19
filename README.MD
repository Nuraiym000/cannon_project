## Overview

Cannon Game is a shooting game developed using Kivy, offering players the ability to select from different weapons to shoot at various targets within a specified time limit. The game tracks essential metrics such as scores, shots, hits, and accuracy, providing an engaging and challenging experience.

## Features

- Multiple Weapons: Choose from a cannon, pistol, or laser gun, each with unique properties.
- Targets: Aim at moving targets, stones, mirrors, and more.
- Scoring: Track your shots, hits, and accuracy.
- High Scores: View the top scores from previous games.
- Help: Get instructions on how to play the game.

## Requirements

- Python 3.6 or higher
- Kivy
- SQLite

## Installation

1. **After opening the project make sure that you are now in a Cannon-Game directory**
    cd Cannon-Game


2. **Create a virtual environment (optional but recommended)**:
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   

3. Install the required packages:
   pip install -r requirements.txt
   

## Running the Game

1. Ensure you are in the project directory:
   cd Cannon-Game/src
   

2. Run the game:
   python main.py
   

## Game Controls

- Rotate Cannon: Use the < and > buttons to rotate the cannon left and right.
- Shoot: Press the "Shoot" button to fire a bullet.
- Select Weapon: Use the weapon buttons (Cannon, Pistol, Laser) to switch between weapons.
- Back to Menu: Press the "Back to Menu" button to return to the main menu.
- Restart Game: After the game ends, press "Restart" to start a new game.

## Game Screens

- Main Menu: Start a new game, continue an existing game, view high scores, or access the help screen.
- Game Screen: The main gameplay area where you aim and shoot targets.
- High Scores Screen: View the top scores with detailed statistics.
- Help Screen: Read instructions on how to play the game.

## Database

The game uses SQLite to store high scores. The database file (`scores.db`) is created automatically when the game is run for the first time. 

## Customization

You can customize various game parameters in the main.py file:

- Screen Size: Adjust the SCREEN_WIDTH and SCREEN_HEIGHT constants.
- Game Duration: Change the GAME_TIME constant.
- Weapon Properties: Modify constants like BULLET_SPEED, LASER_VEL, BULLET_RADIUS, etc.

## Troubleshooting

- Missing Assets: Ensure all asset files (images for cannon, targets, bullets, etc.) are in the correct directory (`assets/`).
- Dependencies: If the game doesn't run, check that all required packages are installed and compatible with your Python version.