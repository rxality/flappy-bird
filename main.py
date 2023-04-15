### IMPORTS ###
import random
from typing import List

import pygame

### INITIALIZATION ###

pygame.init()
pygame.font.init()
pygame.mixer.init()

### FUNCTIONS ###


def random_choice(sequence: List[int]) -> int:
    """Return a random element from a non-empty sequence."""
    return sequence[random.randrange(len(sequence))]


### CONSTANTS ###

# Colors
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Display
DISPLAY_WIDTH = 576
DISPLAY_HEIGHT = 768
PIXEL_SIZE = 64
DIMENSIONS = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
DISPLAY = pygame.display.set_mode(DIMENSIONS)  # formerly screen

HIDDEN_DISPLAY = DISPLAY.copy()  # formerly debug_surface
X_AXIS = [x for x in range(0, DISPLAY_WIDTH, PIXEL_SIZE)]
Y_AXIS = [y for y in range(0, DISPLAY_HEIGHT, PIXEL_SIZE)]

# Framerate
CLOCK = pygame.time.Clock()
FPS = 60

# Font
FONT_SIZE = PIXEL_SIZE
FONT = pygame.font.Font(pygame.font.get_default_font(), size=FONT_SIZE)

# Assets
BACKGROUND = pygame.image.load("assets/background/background.jpg")

GROUND_SURFACE = pygame.image.load("assets/background/ground.jpg")
GROUND_BELOW_SURFACE = (222, 216, 149)

START_BUTTON = pygame.image.load("assets/foreground/start_button.png")
PIPE_BASE = pygame.image.load("assets/foreground/pipe_base.png")
PIPE_TOP = pygame.image.load("assets/foreground/pipe_top.png")

PLAYER_DEFAULT = pygame.image.load("assets/player/flap1.png")
PLAYER_FLAP = pygame.image.load("assets/player/flap2.png")

# Foreground asset positions
GROUND_PIPE_Y_POS = 576
CEILING_PIPE_Y_POS = 0
CEILING_HEIGHT_LIMIT = -32

# Sounds
FLAP_AUDIO = pygame.mixer.Sound("assets/sounds/flap.mp3")
SCORE_AUDIO = pygame.mixer.Sound("assets/sounds/score.mp3")
DEATH_AUDIO = pygame.mixer.Sound("assets/sounds/death.mp3")

# Display settings

pygame.display.set_icon(pygame.transform.scale(PLAYER_FLAP, (32, 32)))
pygame.display.set_caption("Flappy")



class Flappy:
    def __init__(self):
        self.velocity = 0
        self.flap_height = 100
        self.flap_speed = 10
        self.player_x = DISPLAY_WIDTH / 2
        self.player_y = (DISPLAY_HEIGHT / 2) - PIXEL_SIZE

        self.running = True
        self.paused = False
        self.active_game = False
        self.spacebar_down = False

        self.ground_surface_hitboxes = []
        self.pipe_x_pos = DISPLAY_WIDTH + (PIXEL_SIZE * 8)

        self.ground_pipe_y_pos = 576
        self.ceiling_pipe_y_pos = 0

        self.ground_pipe_extensions = [
            extension
            for extension in range(512, random_choice([448, 384]), -PIXEL_SIZE)
        ]
        self.ceiling_pipe_extensions = [
            extension
            for extension in range(PIXEL_SIZE, random_choice([128, 192]), PIXEL_SIZE)
        ]

        self.score = 0
        self.highscore = 0

    def start_game(self):
        """
        This function runs the game loop and handles events, rendering, gravity, pipes, score, and
        screen refreshing.
        """
        while self.running:
            self.event_handler()

            if not self.active_game:
                self.start_screen()

            self.render()
            if self.active_game:
                self.handle_gravity()
                self.create_pipes()

            score_text = FONT.render(str(self.score), False, WHITE)
            DISPLAY.blit(score_text, (DISPLAY_WIDTH * 0.69 - (PIXEL_SIZE * 2), 0))

            self.start_screen()
            self.refresh_screen()

    def event_handler(self):
        """
        This function handles events such as quitting the game and detecting key presses for flapping
        the game character.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN and not self.paused:
                if event.key == pygame.K_SPACE and not self.spacebar_down:
                    self.spacebar_down = True
                    self.velocity = -self.flap_speed
                    pygame.mixer.Sound.set_volume(FLAP_AUDIO, 0.2)
                    FLAP_AUDIO.play(maxtime=1000)

            elif event.type == pygame.KEYUP and not self.paused:
                if event.key == pygame.K_SPACE:
                    self.spacebar_down = False

    def start_screen(self):
        """
        The function displays the start screen of a game and checks if the start button is clicked to
        start the game.
        """
        cursor_hitbox = pygame.draw.circle(
            HIDDEN_DISPLAY, RED, (pygame.mouse.get_pos()), 5
        )

        if not self.active_game:
            start_button = DISPLAY.blit(
                START_BUTTON,
                (DISPLAY_WIDTH / 2 - PIXEL_SIZE, DISPLAY_HEIGHT / 2 - PIXEL_SIZE),
            )
            start_button_hitbox = pygame.draw.circle(
                HIDDEN_DISPLAY,
                RED,
                (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2),
                PIXEL_SIZE,
            )

            highscore_text = FONT.render(
                "Highscore: " + str(self.highscore), False, WHITE
            )
            DISPLAY.blit(highscore_text, (0, DISPLAY_HEIGHT - 72))

            if (
                start_button_hitbox.contains(cursor_hitbox)
                and start_button.contains(cursor_hitbox)
                and pygame.mouse.get_pressed()[0]
            ):
                self.player_y = (DISPLAY_HEIGHT / 2) - PIXEL_SIZE
                self.pipe_x_pos = DISPLAY_WIDTH + (PIXEL_SIZE * 8)
                self.velocity = 0
                self.flap_height = 100
                self.flap_speed = 10
                self.highscore = (
                    self.score if self.score > self.highscore else self.highscore
                )
                self.score = 0

                self.active_game = True

    def render(self):
        """
        This function renders the game display and checks for collisions between the player and the
        ground surface.
        """
        for y in Y_AXIS:
            for x in X_AXIS:
                if any(y / row == 1 for row in Y_AXIS[-1:]):
                    pygame.draw.rect(
                        DISPLAY, GROUND_BELOW_SURFACE, (x, y, PIXEL_SIZE, PIXEL_SIZE)
                    )

                elif y / Y_AXIS[-2] == 1:
                    ground = DISPLAY.blit(GROUND_SURFACE, (x, y))
                    if ground not in self.ground_surface_hitboxes:
                        self.ground_surface_hitboxes.append(ground)

        pygame.draw.line(
            DISPLAY,
            BLACK,
            (0, Y_AXIS[-2]),
            (DISPLAY_WIDTH, Y_AXIS[-2]),
            1,
        )

        DISPLAY.blit(BACKGROUND, (0, 0))

        self.player_hitbox = pygame.draw.circle(
            HIDDEN_DISPLAY,
            RED,
            (PIXEL_SIZE, self.player_y + PIXEL_SIZE),
            PIXEL_SIZE / 2,
        )

        if self.spacebar_down and not self.paused:
            self.player_pos = DISPLAY.blit(PLAYER_FLAP, (0, self.player_y))

        else:
            self.player_pos = DISPLAY.blit(PLAYER_DEFAULT, (0, self.player_y))

        if (
            self.player_pos.collidelist(self.ground_surface_hitboxes) != -1
            and self.player_y > 560
        ):
            self.active_game = False

    def handle_gravity(self):
        """
        This function handles the gravity and vertical movement of a player character in a game.
        """
        self.player_y += self.velocity
        self.velocity += 1

        if self.player_y < CEILING_HEIGHT_LIMIT:
            self.player_y = CEILING_HEIGHT_LIMIT
        elif self.player_y > DISPLAY_HEIGHT - PLAYER_DEFAULT.get_height() - 72:
            self.player_y = DISPLAY_HEIGHT - PLAYER_DEFAULT.get_height() - 72

    def create_pipes(self):
        """
        This function creates and updates the hitboxes for the pipes and handles
        collisions between the player and the pipes.
        """
        pipe_hitboxes = []

        ground_pipe_y = DISPLAY.blit(PIPE_BASE, (self.pipe_x_pos, GROUND_PIPE_Y_POS))
        ground_pipe_hitbox = pygame.draw.line(
            HIDDEN_DISPLAY,
            RED,
            ground_pipe_y.topleft,
            ground_pipe_y.bottomleft,
            width=4,
        )

        pipe_hitboxes.append(ground_pipe_hitbox)

        for extension in self.ground_pipe_extensions:
            ground_pipe_extension = DISPLAY.blit(
                PIPE_BASE, (self.pipe_x_pos, extension)
            )
            ground_pipe_extension_hitbox = pygame.draw.line(
                HIDDEN_DISPLAY,
                RED,
                ground_pipe_extension.topleft,
                ground_pipe_extension.bottomleft,
                width=4,
            )

            pipe_hitboxes.append(ground_pipe_extension_hitbox)

        ground_top_pipe_y = DISPLAY.blit(
            PIPE_TOP, (self.pipe_x_pos, self.ground_pipe_extensions[-1] - PIXEL_SIZE)
        )
        ground_top_pipe_y_hitbox = pygame.draw.lines(
            HIDDEN_DISPLAY,
            RED,
            False,
            [
                ground_top_pipe_y.bottomleft,
                ground_top_pipe_y.topleft,
                ground_top_pipe_y.topright,
            ],
            width=4,
        )

        pipe_hitboxes.append(ground_top_pipe_y_hitbox)

        ceiling_pipe_y = DISPLAY.blit(PIPE_BASE, (self.pipe_x_pos, CEILING_PIPE_Y_POS))
        ceiling_pipe_y_hitbox = pygame.draw.line(
            HIDDEN_DISPLAY,
            RED,
            ceiling_pipe_y.topleft,
            ceiling_pipe_y.bottomleft,
            width=4,
        )

        pipe_hitboxes.append(ceiling_pipe_y_hitbox)

        for extension in self.ceiling_pipe_extensions:
            ceiling_pipe_extension = DISPLAY.blit(
                PIPE_BASE, (self.pipe_x_pos, extension)
            )
            ceiling_pipe_extension_hitbox = pygame.draw.line(
                HIDDEN_DISPLAY,
                RED,
                ceiling_pipe_extension.topleft,
                ceiling_pipe_extension.bottomleft,
                width=4,
            )

            pipe_hitboxes.append(ceiling_pipe_extension_hitbox)

        ceiling_bottom_pipe_y = DISPLAY.blit(
            pygame.transform.flip(PIPE_TOP, False, True),
            (self.pipe_x_pos, self.ceiling_pipe_extensions[-1] + PIXEL_SIZE),
        )
        ceiling_bottom_pipe_y_hitbox = pygame.draw.lines(
            HIDDEN_DISPLAY,
            RED,
            False,
            [
                ceiling_bottom_pipe_y.topleft,
                ceiling_bottom_pipe_y.bottomleft,
                ceiling_bottom_pipe_y.bottomright,
            ],
            width=4,
        )

        pipe_hitboxes.append(ceiling_bottom_pipe_y_hitbox)

        if self.pipe_x_pos != -PIXEL_SIZE:
            if self.pipe_x_pos + 320 == int(self.player_x):
                self.score += 1
                for audio in [FLAP_AUDIO, DEATH_AUDIO]:
                    audio.stop()

                pygame.mixer.Sound.set_volume(SCORE_AUDIO, 0.3)
                SCORE_AUDIO.play()

            self.pipe_x_pos -= 8

        else:
            self.pipe_x_pos = DISPLAY_WIDTH

            self.ground_pipe_extensions = [
                extension
                for extension in range(512, random_choice([448, 384]), -PIXEL_SIZE)
            ]
            self.ceiling_pipe_extensions = [
                extension
                for extension in range(
                    PIXEL_SIZE, random_choice([128, 192]), PIXEL_SIZE
                )
            ]

        for pipe_hitbox in pipe_hitboxes:
            if self.player_hitbox.clip(pipe_hitbox):
                FLAP_AUDIO.stop()
                self.active_game = False
                pygame.mixer.Sound.set_volume(DEATH_AUDIO, 0.3)
                DEATH_AUDIO.play()
                while self.player_y <= 560:
                    self.player_y += 16
                    self.render()
                    self.refresh_screen()

                self.pipe_x_pos = DISPLAY_WIDTH

                self.ground_pipe_extensions = [
                    extension
                    for extension in range(512, random_choice([448, 384]), -PIXEL_SIZE)
                ]
                self.ceiling_pipe_extensions = [
                    extension
                    for extension in range(
                        PIXEL_SIZE, random_choice([128, 192]), PIXEL_SIZE
                    )
                ]

                self.highscore = (
                    self.score if self.score > self.highscore else self.highscore
                )

    def refresh_screen(self):
        """
        This function refreshes the screen and sets the frame rate to 60 frames per second.
        """
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    flappy = Flappy()
    flappy.start_game()
