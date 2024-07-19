SCREEN_WIDTH = 1024  # Width of the game screen in pixels
SCREEN_HEIGHT = 768  # Height of the game screen in pixels

FPS = 60  # Frames per second, which determines how often the screen updates

# Physics properties for bullets and bombs
BULLET_MASS = 1.0  # Mass of a bullet, which might affect its momentum and collision behavior
BOMB_MASS = 2.0  # Mass of a bomb, which might affect its momentum and collision behavior

# Size properties for bullets and bombs
BULLET_RADIUS = 5  # Radius of a bullet, likely used for collision detection and rendering
BOMB_RADIUS = 10  # Radius of a bomb, likely used for collision detection and rendering

# Laser properties
LASER_DIST = 500  # Maximum distance a laser can travel
LASER_IMPULSE = 100  # Impulse applied when a laser is fired, affecting its initial speed
LASER_VEL = 600  # Velocity of the laser, determining how fast it travels

# Bomb drilling property
BOMB_DRILL = 50  # Drill power of the bomb, potentially indicating how much damage or penetration it can cause

# Gravity setting for the game
GRAVITY = -100  # Gravity constant, affecting the acceleration of falling objects. Negative value implies downward acceleration.

# Game timing
GAME_TIME = 60  # Total game time in seconds, which might be the duration of a level or a match
