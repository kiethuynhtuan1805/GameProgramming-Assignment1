# Library
import pygame
import random


class BackGround:
    def __init__(self):
        self.img_background = pygame.image.load('./images/begin2.png')

    def start(self):
        self.img_background = pygame.image.load('./images/background.png')

    def finished(self):
        self.img_background = pygame.image.load('./images/finish.png')


class Character:
    def __init__(self):
        self.img_character_1 = pygame.image.load('./images/mole_1.png')
        self.img_character_11 = pygame.image.load('./images/mole_11.png')
        self.img_character_12 = pygame.image.load('./images/mole_12.png')
        self.img_character_2 = pygame.image.load('./images/mole_2.png')
        self.img_character_21 = pygame.image.load('./images/mole_21.png')
        self.img_character_22 = pygame.image.load('./images/mole_22.png')
        self.data = []
        self.data.append(self.img_character_11.subsurface(0, 0, 80, 90))
        self.data.append(self.img_character_12.subsurface(0, 0, 80, 90))
        self.data.append(self.img_character_1.subsurface(0, 0, 80, 90))
        self.data.append(self.img_character_2.subsurface(0, 0, 80, 90))
        self.data.append(self.img_character_21.subsurface(0, 0, 80, 90))
        self.data.append(self.img_character_22.subsurface(0, 0, 80, 90))


class GameManager():
    def __init__(self):
        # Variables for the window game
        # self.SCREEN_WIDTH = 1280
        # self.SCREEN_HEIGHT = 720
        self.SCREEN_WIDTH = 993
        self.SCREEN_HEIGHT = 477
        self.FPS = 60
        self.CHARACTER_WIDTH = 80
        self.CHARACTER_HEIGHT = 90
        self.FONT_TOP_MARGIN = 30
        self.LEVEL_SCORE_GAP = 4
        self.GAME_TITLE = "Assignment1"

        # Variables for the main game
        self.time_left = 61
        self.count_down = 5
        self.count_down_time = self.count_down
        self.score = 0
        self.miss = 0
        self.rate = 0
        self.level = 0
        self.start_game = False
        self.in_game = False
        self.game_over = False

        # Font object for displaying text
        self.font_obj = pygame.font.SysFont('comicsansms', 24)
        self.font_coor = pygame.font.SysFont('comicsansms', 12)

        # Possible hole positions
        self.hole_positions = [
            (105, 0),
            (105, 150),
            (105, 300),
            (420, 0),
            (420, 150),
            (420, 300),
            (730, 0),
            (730, 150),
            (730, 300)
        ]

        # Initialize screen
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)
        pygame.mouse.set_cursor(pygame.cursors.arrow)

        # Initialize background
        self.bg = BackGround()
        self.screen.blit(self.bg.img_background, (0, 0))

        # Character
        self.character = Character()

        # Sound
        self.soundEffect = SoundEffect()

    # Calculate the player level according to his current score & the LEVEL_SCORE_GAP constant

    def level_up(self):
        newLevel = 1 + int(self.score / self.LEVEL_SCORE_GAP)
        if newLevel != self.level:
            # if player get a new level play this sound
            self.soundEffect.playLevelUp()
        return 1 + int(self.score / self.LEVEL_SCORE_GAP)

    # Get the new duration between the time the character pop up and down the holes
    # It's in inverse ratio to the player's current level
    def get_interval_by_level(self, initial_interval):
        new_interval = initial_interval - self.level * 0.15
        if new_interval > 0:
            return new_interval
        else:
            return 0.05

    # Check whether the mouse click hit the character or not
    def is_character_hit(self, mouse_position, current_hole_position):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        current_hole_x = current_hole_position[0]
        current_hole_y = current_hole_position[1]
        if (mouse_x > current_hole_x) and (mouse_x < current_hole_x + self.CHARACTER_WIDTH) and (mouse_y > current_hole_y) and (mouse_y < current_hole_y + self.CHARACTER_HEIGHT):
            return True
        else:
            return False

    # Update the game states, re-calculate the player's score, miss, level

    def update(self, s_time):
        self.screen.blit(pygame.image.load(
            './images/background2.png'), (860, 0))
        # Update time
        current_time_string = "TIME: " + \
            str(int(self.time_left - (pygame.time.get_ticks() - s_time)/1000))
        time_text = self.font_obj.render(
            current_time_string, True, (255, 255, 255))
        time_text_pos = time_text.get_rect()
        time_text_pos.center = (self.SCREEN_WIDTH - 70, self.FONT_TOP_MARGIN)
        self.screen.blit(time_text, time_text_pos)
        # Update the player's score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(
            current_score_string, True, (255, 255, 255))
        score_text_pos = score_text.get_rect()
        score_text_pos.center = (
            self.SCREEN_WIDTH - 70, self.FONT_TOP_MARGIN * 3)
        self.screen.blit(score_text, score_text_pos)
        # Update the player's miss
        current_miss_string = "MISS: " + str(self.miss)
        miss_text = self.font_obj.render(
            current_miss_string, True, (255, 255, 255))
        miss_text_pos = miss_text.get_rect()
        miss_text_pos.center = (
            self.SCREEN_WIDTH - 70, self.FONT_TOP_MARGIN * 4)
        self.screen.blit(miss_text, miss_text_pos)
        # Update the player's level
        current_level_string = "LEVEL: " + str(self.level)
        level_text = self.font_obj.render(
            current_level_string, True, (255, 255, 255))
        level_text_pos = level_text.get_rect()
        level_text_pos.center = (
            self.SCREEN_WIDTH - 70, self.FONT_TOP_MARGIN * 5)
        self.screen.blit(level_text, level_text_pos)

    # Start the game's main loop
    def start(self):
        # Variables of the loop function
        cycle_time = 0
        num = -1
        is_down = False
        interval = 0.1
        initial_interval = 1
        frame_num = 0
        stage = True

        # Set FPS
        fpsClock = pygame.time.Clock()

        # Create rect of the play_box and play_again components
        play_box = pygame.Rect(0, 0, 170, 60)
        play_again = []
        play_again.append(pygame.image.load('./images/playagain1.png'))
        play_again.append(pygame.image.load('./images/playagain2.png'))
        play_again_rect = pygame.Rect(400, 355, 187, 57)
        play_box.move_ip(410, 360)

        # To make the function called just once
        hover = 0
        finish = 0
        finish_hover = 0

        # The start time based on pygame.time.get_ticks()
        s_time = 0

        # Loop
        while stage:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stage = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_game == False and event.button == 1:
                        if play_box.collidepoint(pygame.mouse.get_pos()):
                            self.start_game = True
                            s_time = pygame.time.get_ticks()
                    elif self.in_game == True and self.game_over == False and event.button == 1:
                        if self.is_character_hit(pygame.mouse.get_pos(), self.hole_positions[frame_num]) and num > 0:
                            num = 3
                            is_down = False
                            interval = 0
                            self.score += 1
                            self.level = self.level_up()
                            # Stop popping sound effect
                            self.soundEffect.stopPop()
                            self.soundEffect.playHammer()
                            self.update(s_time)
                        else:
                            self.soundEffect.playMiss()
                            self.miss += 1
                            self.update(s_time)
                    elif self.game_over == True and event.button == 1:
                        if play_again_rect.collidepoint(pygame.mouse.get_pos()):
                            # Set initial variables
                            self.start_game = True
                            self.in_game = False
                            self.game_over = False
                            self.score = 0
                            self.miss = 0
                            self.level = 0
                            # Set variables of the loop function
                            cycle_time = 0
                            num = -1
                            is_down = False
                            interval = 0.1
                            initial_interval = 1
                            frame_num = 0
                            finish = 0
                            finish_hover = 0

                            # Start time
                            s_time = pygame.time.get_ticks()

            if self.start_game == False:
                if play_box.collidepoint(pygame.mouse.get_pos()):
                    if hover == 0:
                        pygame.mouse.set_cursor(pygame.cursors.broken_x)
                        self.bg.img_background = pygame.image.load(
                            './images/begin4.png')
                        self.screen.blit(self.bg.img_background, (0, 0))
                        hover = 1
                else:
                    if hover == 1:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
                        self.bg.img_background = pygame.image.load(
                            './images/begin2.png')
                        self.screen.blit(self.bg.img_background, (0, 0))
                        hover = 0

            elif self.in_game == False:
                self.bg.start()
                self.screen.blit(self.bg.img_background, (0, 0))
                font_count_down = pygame.font.SysFont('comicsansms', 60)
                # Countdown
                self.count_down_time = int(
                    self.count_down - (pygame.time.get_ticks() - s_time)/1000)
                count_down_string = str(self.count_down_time)
                count_down_text = font_count_down.render(
                    count_down_string, True, (255, 255, 255))
                count_down_text_pos = count_down_text.get_rect()
                count_down_text_pos.center = (
                    self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
                self.screen.blit(count_down_text, count_down_text_pos)
                if (self.count_down_time == 0):
                    self.in_game = True
                    s_time = pygame.time.get_ticks()

            elif self.game_over == True:
                if finish == 0:
                    # Set arrow
                    pygame.mouse.set_cursor(pygame.cursors.arrow)
                    # Set background
                    self.bg.finished()
                    self.screen.blit(self.bg.img_background, (0, 0))
                    # Update the final score
                    final_score_string = "SCORE: " + str(self.score)
                    final_score_text = self.font_obj.render(
                        final_score_string, True, (255, 255, 255))
                    final_score_text_pos = final_score_text.get_rect()
                    final_score_text_pos.center = (520, 210)
                    self.screen.blit(final_score_text, final_score_text_pos)
                    # Update the final miss
                    final_miss_string = "MISS: " + str(self.miss)
                    final_miss_text = self.font_obj.render(
                        final_miss_string, True, (255, 255, 255))
                    final_miss_text_pos = final_miss_text.get_rect()
                    final_miss_text_pos.center = (520, 250)
                    self.screen.blit(final_miss_text, final_miss_text_pos)
                    # Update the final rate
                    if self.score + self.miss == 0:
                        rate = 0
                    elif self.score == 0:
                        rate = 100
                    else:
                        rate = round(
                            self.score/(self.score + self.miss) * 100, 2)
                    final_rate_string = "RATE: " + str(rate) + ' %'
                    final_rate_text = self.font_obj.render(
                        final_rate_string, True, (255, 255, 255))
                    final_rate_text_pos = final_rate_text.get_rect()
                    final_rate_text_pos.center = (520, 290)
                    self.screen.blit(final_rate_text, final_rate_text_pos)
                    self.screen.blit(play_again[0], (400, 355))

                    finish = 1
                elif finish == 1:
                    if play_again_rect.collidepoint(pygame.mouse.get_pos()):
                        if finish_hover == 0:
                            pygame.mouse.set_cursor(pygame.cursors.broken_x)
                            self.screen.blit(play_again[1], (400, 355))
                            finish_hover = 1
                    else:
                        if finish_hover == 1:
                            pygame.mouse.set_cursor(pygame.cursors.arrow)
                            self.screen.blit(play_again[0], (400, 355))
                            finish_hover = 0
            else:
                if num > 5:
                    self.screen.blit(self.bg.img_background, (0, 0))
                    self.update(s_time)
                    num = -1

                if num == -1:
                    self.screen.blit(self.bg.img_background, (0, 0))
                    self.update(s_time)
                    num = 0
                    is_down = False
                    interval = 0.5
                    frame_num = random.randint(0, 8)

                # Reset character
                mil = fpsClock.tick(self.FPS)
                sec = mil / 1000.0
                cycle_time += sec
                if cycle_time > interval:
                    self.screen.blit(self.bg.img_background, (0, 0))
                    self.screen.blit(
                        self.character.data[num], (self.hole_positions[frame_num][0], self.hole_positions[frame_num][1]))
                    self.update(s_time)
                    if is_down is False:
                        num += 1
                    else:
                        num -= 1
                    if num == 4:
                        interval = 0.3
                    elif num == 3:
                        num -= 1
                        is_down = True
                        self.soundEffect.playPop()
                        # get the newly decreased interval value
                        interval = self.get_interval_by_level(initial_interval)
                    else:
                        interval = 0.1
                    cycle_time = 0

                if (int(self.time_left - (pygame.time.get_ticks() - s_time - 5)/1000) == 0):
                    self.game_over = True
                    # Set the theme sound
                    pygame.mixer.music.unload()
                    pygame.mixer.music.load("music/themesong.wav")
                    pygame.mixer.music.play(-1)
                else:
                    if (int(self.time_left - (pygame.time.get_ticks() - s_time - 5)/1000) == 10):
                        pygame.mixer.music.unload()
                        pygame.mixer.music.load("sounds/count_down.wav")
                        pygame.mixer.music.play(-1)
                    self.update(s_time)

                # Set coordinates counter
                coordinates_x, coordinates_y = pygame.mouse.get_pos()
                textCoor = self.font_coor.render(
                    'x: ' + str(coordinates_x) + ', y: ' + str(coordinates_y), True, (255, 255, 255))
                textCoor_pos = textCoor.get_rect()
                textCoor_pos.centerx = self.SCREEN_WIDTH - 50
                textCoor_pos.centery = self.SCREEN_HEIGHT - 20
                self.screen.blit(textCoor, textCoor_pos)

            pygame.display.update()


class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("music/themesong.wav")
        self.countDownSound = pygame.mixer.Sound('sounds/count.wav')
        self.hammerSound = pygame.mixer.Sound('sounds/hammering.wav')
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.missSound = pygame.mixer.Sound("sounds/miss.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)

    def playCountDown(self):
        self.countDownSound.play()

    def stopCountDown(self):
        self.countDownSound.stop()

    def playHammer(self):
        self.hammerSound.play()

    def stopHammer(self):
        self.hammerSound.stop()

    def playPop(self):
        self.popSound.play()

    def stopPop(self):
        self.popSound.stop()

    def playMiss(self):
        self.missSound.play()

    def stopMiss(self):
        self.missSound.stop()

    def playLevelUp(self):
        self.levelSound.play()

    def stopLevelUp(self):
        self.levelSound.stop()


###############################################################
# Initialize the game
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

# Run the main loop
my_game = GameManager()
my_game.start()
# Exit the game if the main loop ends
pygame.quit()