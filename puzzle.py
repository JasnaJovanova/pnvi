# Memory Puzzle - Upgraded Version
# Includes: 10x10 board, new shape, new colors, hint highlight, streak scoring

import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 760
WINDOWHEIGHT = 780
REVEALSPEED = 8
BOXSIZE = 50
GAPSIZE = 15
BOARDWIDTH = 10
BOARDHEIGHT = 10
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, "Board must have even number of boxes"
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2) + 60

# Colors
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
PINK     = (114, 117, 166)
LIME     = (177, 255, 94)
TEAL     = (0, 200, 180)
GOLD     = (230, 210, 40)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

# Shapes
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'
BALL = 'ball'
TRIANGLE = 'triangle'   # NEW SHAPE

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, PINK, LIME, TEAL, GOLD)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL, BALL, TRIANGLE)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT

# ---------------- MAIN GAME ----------------

def main():
    global FPSCLOCK, DISPLAYSURF

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Memory Game")

    mousex = 0
    mousey = 0

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)
    firstSelection = None

    score = 0
    streak = 0

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        hintButton = drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

                # HINT CLICKED
                if hintButton.collidepoint(mousex, mousey) and firstSelection:
                    pair = findMatchingPair(mainBoard, firstSelection)
                    if pair:
                        # pass board and revealedBoxes into animation (DO NOT change revealedBoxes)
                        hintHighlightAnimation(mainBoard, revealedBoxes, firstSelection, pair)
                    continue

        boxx, boxy = getBoxAtPixel(mousex, mousey)

        if boxx is not None and boxy is not None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)

            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True

                if firstSelection is None:
                    firstSelection = (boxx, boxy)

                else:
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                        streak = 0
                    else:
                        streak += 1
                        score, earned = apply_score(score, streak)

                        if hasWon(revealedBoxes):
                            gameWonAnimation(mainBoard)
                            pygame.time.wait(1500)
                            mainBoard = getRandomizedBoard()
                            revealedBoxes = generateRevealedBoxesData(False)
                            streak = 0
                            drawBoard(mainBoard, revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1200)
                            startGameAnimation(mainBoard)

                    firstSelection = None

        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# ---------------- HINT LOGIC ----------------

def findMatchingPair(board, firstSel):
    shape, color = getShapeAndColor(board, firstSel[0], firstSel[1])
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if (x, y) != firstSel:
                s, c = getShapeAndColor(board, x, y)
                if s == shape and c == color:
                    return (x, y)
    return None

def hintHighlightAnimation(board, revealed, box1, box2):
    # Flash highlight, DO NOT reveal tiles and do NOT modify revealed.
    # We redraw board each frame so we need to pass board and revealed.
    for _ in range(4):
        drawBoard(board, revealed)  # redraw background + tiles/buttons/title
        drawHighlightBox(box1[0], box1[1])
        drawHighlightBox(box2[0], box2[1])
        pygame.display.update()
        pygame.time.wait(150)

        drawBoard(board, revealed)
        pygame.display.update()
        pygame.time.wait(100)

# ---------------- SCORING ----------------

def apply_score(score, streak):
    base_points = 1
    earned = base_points * (2 ** (streak - 1))
    return score + earned, earned

def drawScore(score):
    font = pygame.font.Font(None, 60)
    scoreSurf = font.render(f"Score: {score}", True, WHITE)
    DISPLAYSURF.blit(scoreSurf, (20, 10))

# ---------------- BOARD FUNCTIONS ----------------

def generateRevealedBoxesData(val):
    return [[val] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

def getRandomizedBoard():
    icons = [(shape, color) for color in ALLCOLORS for shape in ALLSHAPES]
    random.shuffle(icons)
    numIconsUsed = BOARDWIDTH * BOARDHEIGHT // 2
    icons = (icons[:numIconsUsed] * 2)
    random.shuffle(icons)

    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons.pop())
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    return [theList[i:i + groupSize] for i in range(0, len(theList), groupSize)]

def leftTopCoordsOfBox(boxx, boxy):
    left = XMARGIN + boxx * (BOXSIZE + GAPSIZE)
    top  = YMARGIN + boxy * (BOXSIZE + GAPSIZE)
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawIcon(shape, color, boxx, boxy):
    quarter = BOXSIZE // 4
    half = BOXSIZE // 2
    left, top = leftTopCoordsOfBox(boxx, boxy)

    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color,
                            [(left + half, top),
                             (left + BOXSIZE, top + half),
                             (left + half, top + BOXSIZE),
                             (left, top + half)])
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1),
                                            (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))
    elif shape == BALL:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
    elif shape == TRIANGLE:
        pygame.draw.polygon(DISPLAYSURF, color,
                            [(left + half, top),
                             (left + BOXSIZE, top + BOXSIZE),
                             (left, top + BOXSIZE)])

def getShapeAndColor(board, boxx, boxy):
    # returns (shape, color)
    return board[boxx][boxy]

def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, -REVEALSPEED - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    font = pygame.font.Font(None, 60)
    title = font.render("Memory Game", True, WHITE)
    DISPLAYSURF.blit(title, (WINDOWWIDTH // 2 - title.get_width() // 2, 10))

    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)

    return drawHintButton()

def drawHintButton():
    font = pygame.font.Font(None, 40)
    text = font.render("HINT", True, WHITE)
    button = pygame.Rect(WINDOWWIDTH - 160, 15, 120, 50)
    pygame.draw.rect(DISPLAYSURF, (200, 60, 60), button)
    DISPLAYSURF.blit(text, (button.x + 25, button.y + 10))
    return button

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR,
                     (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
    covered = generateRevealedBoxesData(False)
    boxes = [(x, y) for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT)]
    random.shuffle(boxes)
    groups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, covered)
    for group in groups:
        revealBoxesAnimation(board, group)
        coverBoxesAnimation(board, group)

def gameWonAnimation(board):
    covered = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for _ in range(12):
        color1, color2 = color2, color1
        DISPLAYSURF.fill(color1)
        drawBoard(board, covered)
        pygame.display.update()
        pygame.time.wait(200)

def hasWon(revealed):
    return all(all(row) for row in revealed)

if __name__ == "__main__":
    main()
