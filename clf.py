#! /usr/bin/python3

# Programmer: Eric Shumaker
# File: clf.py
# Language Version: Python 3.5.1
# Depends On:   Pygame 1.9.2,
#               treasures.txt, 
#               LiberationMono-Bold.ttf

import os, sys, pygame
from random import choice, randint
from pygame.locals import *

class GameSettings():
    """More like GameInitialization, but I'm sticking with GameSettings.
    Initializes pygame, and contains various values that need to be made available
    to other parts of the program, including the screen surface object."""
    def __init__(self, startMode):
        """Sets up a great deal of info the game needs, keeps it all in one place.
        The GameSettings object instance will get passed around A LOT by other
        methods and functions."""

        # Characteristics of the window the game is displayed in.
        self.winWidth = 640
        self.winHeight = 640
        self.winCaption = "Cyborg Locates Feline Game"

        # Characteristics of the grid of tiles the game take place on.
        self.gridWidth = 40
        self.gridHeight = 40
        self.cellWidth = 16
        self.cellHeight = 16

        # How big the writing should be.
        self.bigFontSize = 20
        self.littleFontSize = 16

        # The window background color
        self.bgColor = (51, 51, 51)

        # Treasures are the items spread around the screen for cyborg to examine.
        # Each one will look like a randomly selected character from the treasure symbols string.
        self.treasureSymbols = "`-=[]\;,./~_+{}|:<>?!#$%^&*()1234567890zxcvbnmasdfghjklqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP"
        self.numOfTreasures = 20

        # tresureList will contain the list of each tresure on the grid.
        self.treasureList = []
        # locationList will contain the location of each treasure in a list of 2 item lists.
        # Each item will be a 2 item list of the form [x, y]
        # This does not describe the pixel position but the grid position.
        # This list will be checked everytime an item is placed randomly on the screen so that
        # no 2 items are placed in the same place.
        self.locationList = []

        # gameMode is used so the program knows what to display and what
        # input to respond to while running different parts of the program.
        self.gameModes = ['splash', 'message', 'instructions', 'play', 'win', 'credits']
        # If the program just started this will set gameMode to 'splash'.
        # If the user is starting a new game after winning, it will set gameMode to 'play'.
        self.gameMode = startMode


        # set up pygame and the pygame window
        pygame.init()
        self.screenSurface = pygame.display.set_mode((self.winWidth, self.winHeight), 0, 32)
        pygame.display.set_caption(self.winCaption)

        # Now initialize things that couldn't be set up until after the pygame initialization.
        # Set up the fonts.
        try:
            self.bigFont = pygame.font.Font('LiberationMono-Bold.ttf', self.bigFontSize)
            self.littleFont = pygame.font.Font('LiberationMono-Bold.ttf', self.littleFontSize)
        except:
            self.bigFont = pygame.font.SysFont('monospace', self.bigFontSize, True, False)
            self.littleFont = pygame.font.SysFont('monospace', self.littleFontSize, True, False)


        # Get the contents of the ASCII text screens the game uses.
        self.screens = getASCIIScreens()

        # Render each screen's text as a surface that can be blitted to the screen.
        self.splashSurface = self.createTextSprite(self.screens['splash'])
        self.instructionsSurface = self.createTextSprite(self.screens['instructions'])
        self.winSurface = self.createTextSprite(self.screens['win'])
        self.creditsSurface = self.createTextSprite(self.screens['credits'])

        # Read the treasure descriptions from an external file.
        self.treasureTextList = self.readTreasureText('treasures.txt')

        # A clock to check/control framerate.
        self.clock = pygame.time.Clock()


    # The game might quit from a few different places, so I wrote the code to close just once.
    def quitGame(self):
        pygame.quit()
        sys.exit()


    # This function makes sure when we change the mode,
    # it is an actual mode the program knows what to do with.
    def changeMode(self, newMode):
        if newMode in self.gameModes:
            self.gameMode = newMode


    # When the player bumps into something, this function will return which item is is.
    def getTreasureItemAt(self, x, y):
        for treasure in self.treasureList:
            if treasure.x_coord == x and treasure.y_coord == y:
                return treasure


    # Each treasure will have a different color selected at random.
    def getRandomColor(self):
        color_opts = (102, 153, 204, 255)
        red = choice(color_opts)
        green = choice(color_opts)
        blue = choice(color_opts)
        return tuple([red, green, blue])


    # This will return a random grid location, for placing items on the board.
    def getRandomCoordinates(self):
        x_coord = choice(range(self.gridWidth))
        y_coord = choice(range(self.gridHeight))
        return x_coord, y_coord


    # Here we populate the treasureList with the items that cyborg will examine.
    def populateTreasureList(self, grid_obj):
        kitten_placed = False
        for i in range(self.numOfTreasures - 1):
            # Get a random location to place the new treasure in.
            x, y = self.getRandomCoordinates()
            # This loop makes sure the same location hasn't already been used.
            while [x, y] in self.locationList:
                x, y = self.getRandomCoordinates()
            # Place the new location in the locationList
            self.locationList.append([x, y])
            # place the whole treasure in the treasureList.
            if kitten_placed:
                treasure = Treasure(self, grid_obj, x, y, False, self.getRandomTreasureText())
            else:
                # The first item to place will be the feline.
                treasure = Treasure(self, grid_obj, x, y, True)
                treasure.text = "It is the feline! You are reunited!"
                kitten_placed = True
            self.treasureList.append(treasure)


    # This function reads each entry in the treasures.txt file.
    # Each entry is added to a list. Each element of the list is a
    # list of the lines in the entry. Some will have only one line,
    # some will have more. Each line has to be stored separately,
    # because each line must be rendered and blitted seperately.
    def readTreasureText(self, filename):
        try:
            # This is the list of all the lists.
            treasureDescripts = []
            textfile = open(filename,'r')
            lines = textfile.readlines()
            # This varibale will hold the list of lines
            # for a single entry from the treasures.txt file.
            description = []
            for line in range(len(lines)):
                if lines[line][0] == '#':       # '#' is ignored as a comment.
                    pass
                elif lines[line][0] != '\n':
                # if the line is not blank, it is appended to the current list.
                    description.append(lines[line].strip())
                elif lines[line][0] == '\n' and len(description) > 0:
                # if the line is blank and the list has something in it,
                # it is appended to the list of lists.
                    treasureDescripts.append(description)
                    description = []
            # This if statment makes sure the last entry is not ignored,
            # even if it is not followed by a blank line.
            if len(description) > 0:
                treasureDescripts.append(description)
        except FileNotFoundError:
            # In case the treasures.txt is not readable for some reason,
            # this will create a list of boring texts for the game items.
            treasureDescripts = [['This is not feline.']] * self.numOfTreasures

        return treasureDescripts


    # This will read a file containing text to be printed exactly as is.
    # It will return a list with each line as an entry.
    # They must be stored separately, because the have to be rendered and blitted separately.
    def readTextScreen(self, filename):
        screenText = []
        textfile = open(filename, 'r')
        lines = textfile.readlines()
        for line in lines:
            screenText.append(line[:-1])
        return screenText


    # This will return a random entry from the list returned by the readTreasureText() method.
    # It will be called everytime a new Treasure instance is created.
    def getRandomTreasureText(self):
        index = randint(0, len(self.treasureTextList) - 1)
        textToReturn = self.treasureTextList[index]
        del self.treasureTextList[index]
        return textToReturn


    # This method takes a list of strings and renders them one at a time. Then it blits each one
    # onto a surface which is returned and can be used to display the text onscreen.
    def createTextSprite(self, strToDraw):
        lineSurfaceList = []
        surfWidth = 0
        surfHeight = 0
        for line in strToDraw:
            lineSurface = self.bigFont.render(line, True, (255, 255, 255), (0, 0, 0))
            lineSurfaceList.append(lineSurface)
            surfHeight += lineSurface.get_height()
            if lineSurface.get_width() > surfWidth:
                surfWidth = lineSurface.get_width()
        fullSurface = pygame.Surface((surfWidth, surfHeight))
        fullSurfaceRect = fullSurface.get_rect()
        lineCount = 0
        y_coord = 0
        for surf in lineSurfaceList:
            fullSurface.blit(surf, ((fullSurfaceRect.centerx - surf.get_width() / 2), y_coord))
            lineCount += 1
            y_coord += surf.get_height()
        return fullSurface


    # Render the symbol of an object as a Surface that can be blitted to the screen.
    def createSymbolSprite(self, symbol_obj):
        symbolSurface = self.littleFont.render(symbol_obj.symbol, True, symbol_obj.color, self.bgColor)
        return symbolSurface


    def blitMessage(self, textSurface):
        # Get the rectangles of the message and screen,
        # so you can set them equal to one another before blitting.
        textRect = textSurface.get_rect()
        screenRect = self.screenSurface.get_rect()
        textRect.center = screenRect.center
        self.screenSurface.blit(textSurface, textRect)



    # This function draws the basic game screen.
    def drawScreen(self, hero_obj, grid_obj):
        self.screenSurface.fill(self.bgColor)
        for treasure in self.treasureList:
            grid_obj.blitSymbol(self, treasure.x_coord, treasure.y_coord, treasure.symbolSurface)
        grid_obj.blitSymbol(self, hero_obj.x_coord, hero_obj.y_coord, hero_obj.symbolSurface)


    # These special draw functions call the regular drawScreen function,
    # then blit whatever else they need on top of it.
    def drawScreenMessage(self, hero_obj, grid_obj, textSurface):
        self.drawScreen(hero_obj, grid_obj)
        self.blitMessage(textSurface)


    def drawScreenSplash(self, hero_obj, grid_obj):
        self.screenSurface.fill((0, 0, 0))
        self.blitMessage(self.splashSurface)


    def drawScreenInstructions(self, hero_obj, grid_obj):
        self.screenSurface.fill((0, 0, 0))
        self.blitMessage(self.instructionsSurface)


    def drawScreenWin(self, hero_obj, grid_obj):
        self.screenSurface.fill((0, 0, 0))
        self.blitMessage(self.winSurface)


    def drawScreenCredits(self, hero_obj, grid_obj):
        self.screenSurface.fill((0, 0, 0))
        self.blitMessage(self.creditsSurface)



class GridCell():
    """A single cell in the game grid. Defined by its x and y coordinates in the grid, its x and y coorinates on the screen,
    and by its Rect."""
    def __init__(self, settings_obj, x_loc, y_loc):
        self.width = settings_obj.cellWidth
        self.height = settings_obj.cellHeight
        self.x_coord = x_loc * settings_obj.cellWidth
        self.y_coord = y_loc * settings_obj.cellHeight
        self.box = Rect(self.x_coord, self.y_coord, self.width, self.height)


    # This method fills the cell with a specified color
    def fillBox(self, settings_obj, color):
        pygame.draw.rect(settings_obj.screenSurface, color, self.box)


    # This method will blit a specified surface onto the cell
    def blitSelf(self, settings_obj, symbolSurface):
        settings_obj.screenSurface.blit(symbolSurface, self.box)



class GameGrid():
    """The whole game grid. Contains a two-dimensional array of GridCell instances, and methods to deal with them."""
    def __init__(self, settings_obj):
        self.grid = {}
        for y in range(settings_obj.gridHeight):
            for x in range(settings_obj.gridWidth):
                coords = (x, y)
                cell = GridCell(settings_obj, x, y)
                self.grid[coords] = cell

    # Picks a cell at random and fills it with red.
    def fillRandomCell(self, settings_obj):
        randCell = (choice(range(settings_obj.gridWidth)), choice(range(settings_obj.gridHeight)))
        self.grid[randCell].fillBox(settings_obj, (255, 0, 0))

    # This will fill a specified cell with a specified color.
    def fillCell(self, settings_obj, x_coord, y_coord, color):
        self.grid[tuple([x_coord, y_coord])].fillBox(settings_obj, color)

    # This method blits a specified surface onto a specified cell
    def blitSymbol(self, settings_obj, x_coord, y_coord, symbolSurface):
        self.grid[tuple([x_coord, y_coord])].blitSelf(settings_obj, symbolSurface)



class Player():
    """Stores information about the player. Since it has only data and no methods,
    I would probably make this a dictionary in the GameSettings class if I started again."""
    def __init__(self, settings_obj, x_coord, y_coord):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.color = (255, 255, 255)
        self.symbol = '@'
        self.collidingWith = None
        self.symbolSurface = settings_obj.createSymbolSprite(self)
        self.moveUp = False
        self.moveDown = False
        self.moveLeft = False
        self.moveRight = False



class Treasure():
    """Stores information about one treasure item. Since it has only data and no methods,
    I would probably make this a dictionary in the GameSettings class if I started again."""
    def __init__(self, settings_obj, grid_obj, x_coord, y_coord, feline=False, text="This is a treasure."):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.color = settings_obj.getRandomColor()
        self.text = text
        self.feline = feline
        self.symbol = settings_obj.treasureSymbols[randint(0, len(settings_obj.treasureSymbols) - 1)]
        self.textSurface = settings_obj.createTextSprite(self.text)
        self.symbolSurface = settings_obj.createSymbolSprite(self)



# Here is a function for processing input while the game is in play mode.
def getInputEventsPlay(settings_obj, player_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        if event.type == KEYDOWN:
            if event.key == K_DOWN:
                player_obj.moveDown = True
            if event.key == K_UP:
                player_obj.moveUp = True
            if event.key == K_LEFT:
                player_obj.moveLeft = True
            if event.key == K_RIGHT:
                player_obj.moveRight = True
        if event.type == KEYUP:
            if event.key == K_DOWN:
                player_obj.moveDown = False
            if event.key == K_UP:
                player_obj.moveUp = False
            if event.key == K_LEFT:
                player_obj.moveLeft = False
            if event.key == K_RIGHT:
                player_obj.moveRight = False

    # player_dest will store the player's destination and check it before committing the move.
    player_dest = [player_obj.x_coord, player_obj.y_coord]

    # move the player, if the move won't put them off the screen.
    if player_obj.moveDown and player_obj.y_coord < settings_obj.gridHeight - 1:
        player_dest = [player_obj.x_coord, player_obj.y_coord + 1]
    if player_obj.moveUp and player_obj.y_coord > 0:
        player_dest = [player_obj.x_coord, player_obj.y_coord - 1]
    if player_obj.moveLeft and player_obj.x_coord > 0:
        player_dest = [player_obj.x_coord - 1, player_obj.y_coord]
    if player_obj.moveRight and player_obj.x_coord < settings_obj.gridWidth - 1:
        player_dest = [player_obj.x_coord + 1, player_obj.y_coord]

    # check if the player is bumping into any treasure items
    if player_dest not in settings_obj.locationList:
        # not colliding, so commit move
        player_obj.x_coord = player_dest[0]
        player_obj.y_coord = player_dest[1]
        player_obj.collidingWith = None
    else:
        # set all player movement directions to false.
        player_obj.moveUp = player_obj.moveDown = player_obj.moveLeft = player_obj.moveRight = False
        # colliding with something, check what it is.
        item = settings_obj.getTreasureItemAt(player_dest[0], player_dest[1])
        player_obj.collidingWith = item
        if not item.feline:
            # not colliding with feline, so go to message mode to show item's description
            settings_obj.changeMode('message')
        else:
            # colliding with feline, so go to win mode
            settings_obj.changeMode('win')

# Here is a function for processing input while in message mode.
# Pressing any key will continue the game.
def getInputEventsMessage(settings_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        elif event.type == KEYDOWN:
            settings_obj.changeMode('play')

# Here is a function for processing input while in splash mode.
# Pressing 'i' switches to instructions mode, any other key starts game.
def getInputEventsSplash(settings_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        elif event.type == KEYDOWN:
            if event.key == K_i:
                settings_obj.changeMode('instructions')
            else:
                settings_obj.changeMode('play')

# Here is a function for processing input while in instructions mode.
# Pressing any key will start the game.
def getInputEventsInstructions(settings_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        elif event.type == KEYDOWN:
            settings_obj.changeMode('play')

# Here is a function for processing input while in win mode.
# Pressing 'c' shows the credits, 'q' quits the program,
# any other key starts a new game.
def getInputEventsWin(settings_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        elif event.type == KEYDOWN:
            if event.key == K_c:
                settings_obj.changeMode('credits')
            elif event.key == K_q:
                settings_obj.quitGame()
            else:
                newGameStart('play')

# Here is a function for processing input in credits mode.
# Pressing any key takes you back to win mode.
def getInputEventsCredits(settings_obj):
    for event in pygame.event.get():
        if event.type == QUIT:
            settings_obj.quitGame()
        elif event.type == KEYDOWN:
                settings_obj.changeMode('win')

# Calling this starts a new game. Originally, this was main(), but I changed it, because now calling
# newGameStart(startMode) is the simplest way to start a new game after winning.
def newGameStart(startMode):
    # initialize game settings
    settings = GameSettings(startMode)

    # initialize the grid
    grid = GameGrid(settings)

    # make up and place all the treasures
    settings.populateTreasureList(grid)

    # get a random location for the player to start in.
    start_x, start_y = settings.getRandomCoordinates()
    while [start_x, start_y] in settings.locationList:
        start_x, start_y = settings.getRandomCoordinates()
    # create an instance of the Player object.
    hero = Player(settings, start_x, start_y)

    # Game loop calls the appropriate input and drawing functions for the current game mode.
    while True:
        if settings.gameMode == 'play':
            getInputEventsPlay(settings, hero)
            settings.drawScreen(hero, grid)
        elif settings.gameMode == 'message':
            getInputEventsMessage(settings)
            settings.drawScreenMessage(hero, grid, hero.collidingWith.textSurface)
        elif settings.gameMode == 'splash':
            getInputEventsSplash(settings)
            settings.drawScreenSplash(hero, grid)
        elif settings.gameMode == 'instructions':
            getInputEventsInstructions(settings)
            settings.drawScreenInstructions(hero, grid)
        elif settings.gameMode == 'win':
            getInputEventsWin(settings)
            settings.drawScreenWin(hero, grid)
        elif settings.gameMode == 'credits':
            getInputEventsCredits(settings)
            settings.drawScreenCredits(hero, grid)

        pygame.display.update()

        settings.clock.tick(15)

# This returns a dictionary with keys for the four screens described.
# The keys hold a list of strings, one for each line that will need to
# be rendered.
def getASCIIScreens():
    splash = [
        r"  ___  _   _____   ___  ____   ___  ",
        r" // \\ \\ //|| \\ // \\ || \\ // \\ ",
        r" ||     \V/ ||_// || || ||_// ||___ ",
        r" ||     //  || \\ || || ||\\  || || ",
        r" \\_// //   ||_// \\_// || \\ \\_// ",
        r"          _   _   _  ___ __  _      ",
        r"      |  / \ /   /_\  |  |_ /_      ",
        r"      |_ \_/ \_ /   \ |  |_ _/      ",
        r" _____ _____ _     _  ___  _  _____ ",
        r" ||    ||    ||    || ||\\ || ||    ",
        r" ||__  ||__  ||    || || \\|| ||__  ",
        r" ||    ||    ||    || ||  \|| ||    ",
        r" ||    ||___ ||___ || ||   || ||___ ",
        r"                                    ",
        r"      'I' for instructions.         ",
        r"     Any other key to start.        "
    ]
    instructions = [
        "You are cyborg. You look like this - @",
        "Your visual sensors are on the fritz.",
        "You see things, by can't identify them.",
        "What's worse, feline is missing!",
        "To find out what something is, use the arrow keys",
        "to move around until you bump into it.",
        "With persistence, you will find feline in no time!",
        " ",
        "Any key to start."
    ]
    win = [
        " It is feline! You are reunited at last! ",
        "                 __ __                   ",
        "                /##V##\   |              ",
        "           ^_^  \#####/   0              ",
        "           0 0   \###/  >-#-<            ",
        "          >\I/<   \#/    _^_             ",
        "                   V    (0o0)            ",
        "                                         ",
        "              'Q' to quit.               ",
        "            'C' for credits.             ",
        "      Any other key to play again.       "
    ]
    credits = [
        "Made by Eric Shumaker using",
        "Python 3.5.1, Pygame 1.9.2, and the",
        "LiberationMono-Bold.ttf font.",
        " ",
        "Inspired by 'robotfindskitten'",
        "by Leonard Richardson (crummy.com)."
    ]
    return {'splash': splash, 'instructions': instructions, 'win': win, 'credits': credits}


def main():
    newGameStart('splash')

main()
