#/usr/bin/python
#-*- coding:utf-8 -*-
## requirements
# pip3 install tkinter
# pip3 install pynput
## local chess game ##
import threading
import time
import tkinter
from pynput import mouse, keyboard

# destroys frame
def end():
    main.destroy()   

# updates a label in menu bar - i = nth element in menubar, str = string to insert
def setLabel(i, newLabel):
    try:
        if not getLabel(i)==newLabel:
            mBar.entryconfig(i, label = newLabel)
    except:
        i = str(i)
        message = "error: could not insert", newLabel, "at", i + ". menu label"

# returns current i = nth menu label 
def getLabel(i):
    try:
        return mBar.entrycget(i, "label")
    except:
        i = str(i)
        message = "error: not able to retrieve", i + ". menu label"
    
# updates time passed since start
def updateTime():
    whitespace = str(" " * 100) # since a menuitem (used as clock) is not positionable, whitespaces are used to place clock further right
    seconds = 0
    minutes = 0
    while threading.main_thread().is_alive():
        # status[0:exit, 1:paused, 2:play]
        if status == 2:
            setLabel(4, "player greens turn" if turn%2!=0 else "player reds turn")
            time.sleep(1)
            seconds += 1
            if seconds == 60:
                seconds = 0
                minutes += 1
            timeStr = str(whitespace \
                        + "{:0>2}".format(minutes) + ":" \
                        + "{:0>2}".format(seconds))
            setLabel(2, timeStr)
        elif status==1:
            if not getLabel(4).endswith("wins"):
                setLabel(4, "paused")
        elif status == 0:
            return        

def pause():
    global status
    try:
        if getLabel(4).endswith("wins"):
            return
    except:
        return
    status = 1 if status==2 else 2

def getColors():
    # sets colors[][] for bgColor //yeah dirty here
    cur = 1
    colors = [[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)],[0 for i in range(8)]]
    for i in range(8):
        for j in range(8):
            if cur == 1:
                colors[i][j] = "#FFFFFF"
                cur = 0
            else:
                colors[i][j] = "#000000"
                cur = 1
        if cur == 1:
            cur = 0
        else:
            cur = 1
    return colors

# returns backround color relative to position
def getBgColor(colors, x, y):
    x = int(str(x)[0])
    y = int(str(y)[0])

    return colors[y][x]
    
# initialize and returns fields
def initFields():
    fields = [] # list to save label and coords for each field [lb, x, y, color]
    path = "art/empty_white_field.png"
    color = "#FFFFFF"
    x = int(0)
    y = int(0)
    for i in range(8):
        for j in range(8):
            image = tkinter.PhotoImage(file=path)
            lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg=color)
            lb.place(x=x, y=y, anchor="nw")
            fields.append([lb, x, y, color])

            if color == "#FFFFFF":
                color = "#000000"
                path = "art/empty_black_field.png"
            else:
                color = "#FFFFFF"
                path = "art/empty_white_field.png"
            
            x += 100
        
        x = 0
        y += 100
        if color == "#FFFFFF":
            color = "#000000"
            path = "art/empty_black_field.png"
        else:
            color = "#FFFFFF"
            path = "art/empty_white_field.png"
    
    return fields

# initializes and returns pieces 
def initPieces():
    pieces = [] # list to save label, position of pieces[piecenr][label, x, y, image, name, selected]
    colors = getColors()
    path = ["art/rook_red.png", "art/knight_red.png", "art/bishop_red.png", "art/queen_red.png", "art/king_red.png", "art/bishop_red.png", "art/knight_red.png", "art/rook_red.png", "art/pawn_red.png"]
    x = int(0)
    y = int(0)

    for h in range(2):
        for i in range(2):
            for j in range(8):
                if (h==0 and i==0) or (h==1 and i==1):
                    image = tkinter.PhotoImage(file=path[j])
                    name = path[j].replace("art/", "").replace(".png", "")
                else:
                    image = tkinter.PhotoImage(file=path[8])
                    name = path[8].replace("art/", "").replace(".png", "")
                lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg=getBgColor(colors,x,y))
                lb.place(x=x, y=y, anchor="nw")
                pieces.append([lb, x, y, image, name, False]) # last param is 'selected', a boolean determining if a piece is selected
                x += 100
            x = 0
            y += 100

        if h == 0:
            x = 0
            y += 400
        
        for i in range(len(path)):
            path[i] = path[i].replace("red", "green")
        
    return pieces

# get Coords of the field 
def getPos(x, y):
    wx = main.winfo_rootx() # position of chess-window
    wy = main.winfo_rooty()
    x = x - wx # relative position of window to screen
    y = y - wy 
    pos = [x, y]
    for i in range(len(pos)):
        if (pos[i] >= 0 and pos[i] <= 800):
            if len(str(pos[i])) < 3:
                pos[i] = 0
            else:
                pos[i] = int(str(pos[i])[0] + "00")
        else:
            pos = [-1, -1]
            return pos
    return pos

def move(piece, x, y):
    if (x >= 0 and x <= 800) and (y >= 0 and y <= 800):
        piece[1] = x
        piece[2] = y
        piece[0].destroy()
        piece[0] = tkinter.Label(main, image=piece[3], relief="ridge", bd=1, bg=getBgColor(getColors(),x,y))
        piece[0].place(x=x, y=y, anchor="nw")

## MouseListener
def on_click(x, y, button, pressed):
    global isPromoting, popuplabel

    check = False
    try:
        check = isTopLevel()
    except:
        return

    if not status==2 or not check:
        return

    pos = getPos(x, y)
    x = pos[0]
    y = pos[1]

    if isPromoting:
        for popup in popuplabel:
            if popup[1]==x and popup[2]==y:
                # promote pawn
                path = popup[3]
                image = tkinter.PhotoImage(file=path) 
                lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg="#123456")
                lb.image = image
                lb.place(x=pieces[popup[4]][1], y=0, anchor="nw")
                pieces[popup[4]][0] = lb
                pieces[popup[4]][3] = image
                pieces[popup[4]][4] = path.replace("art/", "").replace(".png", "")
                isPromoting = False
                # end turn
                move(pieces[popup[4]], popup[5], 0)
                isCheckMate("red" if pieces[popup[4]][4][-3]=="e" else "green")
                turnTable()
                fr.pack()
            popup[0].destroy()
        popuplabel = []
        return

    if pressed:         # mouse pressed
        for i in range(len(pieces)):
            if (pieces[i][1]==x and pieces[i][2]==y):   # checks if a piece got selected by the player
                pieces[i][5] = True                     # piece[5] = 'selected', a boolean property to determine if the piece is selected
    else:               # mouse released
        toMove = -1
        for i in range(len(pieces)):
            if pieces[i][5]==True:
                toMove = i
        if toMove != -1:
            pieces[toMove][5] = False
            # make turn validation with the chosen piece, targetX and targetY
            if validateTurn(pieces[toMove], x, y, test=False):
                # check if a pawn promoted
                if pieces[toMove][4].startswith("pawn") and y==0:
                    promotePawn(pieces[toMove], x)
                    isPromoting = True
                    return
                # move piece after validation
                move(pieces[toMove], x, y)
                # is check mate?
                isCheckMate("red" if pieces[toMove][4][-3]=="e" else "green")
                # turn table for next player
                turnTable()
                fr.pack()

# checks if chess frame is on top level
def isTopLevel():
    width, height, x, y = main.winfo_width(), main.winfo_height(), \
                              main.winfo_rootx(), main.winfo_rooty()

    if (width, height, x, y) != (1, 1, 0, 0):
            is_toplevel = main.winfo_containing(x + (width // 2),
                                                y + (height // 2)
                                                ) is not None
            return is_toplevel

# validate turn
def validateTurn(chosenPiece, targetX, targetY, test=False):
    name = str(chosenPiece[4])
    color = "green" if name.endswith("green") else "red"
    x = int(chosenPiece[1])
    y = int(chosenPiece[2])

    # check if the piece chosen belongs to the player at turn
    if turn%2==0 and color=="green" and not test:
        return False
    elif turn%2!=0 and color=="red" and not test:
        return False

    # no move made, return
    if x==targetX and y==targetY:
        return False

    # rook selected
    if name.startswith("rook"):
        if not validateRook(chosenPiece, targetX, targetY):
            return False
    # bishop selected     
    elif name.startswith("bishop"):
        if not validateBishop(chosenPiece, targetX, targetY):
            return False
    # knight selected
    elif name.startswith("knight"):
        if not validateKnight(chosenPiece, targetX, targetY):
            return False
    # queen selected
    elif name.startswith("queen"):
        if not (validateRook(chosenPiece, targetX, targetY) \
                or validateBishop(chosenPiece, targetX, targetY)):
            return False
    # king selected
    elif name.startswith("king"):
        if not validateKing(chosenPiece, targetX, targetY):
            return False
    # pawn selected
    elif name.startswith("pawn"):
        if not validatePawn(chosenPiece, targetX, targetY):
            return False

    # check if ally is already at position
    for piece in pieces:
        if piece[4].endswith(color):
            if piece[1]==targetX and piece[2]==targetY:
                return False

    # checks if an other piece is targeted - the piece first gets removed, but if the player remains checked, move will be undone
    hit = [False, 0] 
    for piece in pieces:
        if (piece[1]==targetX and piece[2]==targetY) and not piece[4].endswith(color):
            hit = [True, pieces.index(piece)]
            piece[1] = -1
            piece[2] = -1
            break

    chosenPiece[1] = targetX    # set position to target, to check if player would be checked after turn
    chosenPiece[2] = targetY
    # move gets undone - player is checked
    if isChecked(color):
        chosenPiece[1] = x
        chosenPiece[2] = y
        if hit[0]:
            pieces[hit[1]][1] = targetX
            pieces[hit[1]][2] = targetY
        return False
    # check if only valid because other player got checked
    else:
        # remove opp king to check if player would remain checked
        # without a king, opp cant be checked and not cause a negation of player being checked 
        color = "green" if color=="red" else "red" 
        king = str("king_"+color)
        for piece in pieces:
            if piece[4].endswith(king):
                kingIXY = [
                    pieces.index(piece),
                    piece[1],
                    piece[2]
                ]
                piece[1] = -1
                piece[2] = -1
                break
        color = "green" if color=="red" else "red" 
        # check if remained checked
        if isChecked(color):
            pieces[kingIXY[0]][1] = kingIXY[1] # reset
            pieces[kingIXY[0]][2] = kingIXY[2]
            chosenPiece[1] = x
            chosenPiece[2] = y
            if hit[0]:
                pieces[hit[1]][1] = targetX
                pieces[hit[1]][2] = targetY
            return False
        pieces[kingIXY[0]][1] = kingIXY[1]  # reset
        pieces[kingIXY[0]][2] = kingIXY[2]
        chosenPiece[1] = x
        chosenPiece[2] = y

    # move gets undone - it was just a valid test
    if test:
        if hit[0]:
            pieces[hit[1]][1] = targetX
            pieces[hit[1]][2] = targetY
    # move doesnt get undone - finalize
    else:
        if hit[0]:                                  # destroy if a piece was hit
            pieces[hit[1]][0].destroy()            

    return True

def validateRook(rook, targetX, targetY):
    x = rook[1]
    y = rook[2]
    # rook moving on y axis
    if (x==targetX and y!=targetY):
        # moving up 
        if (y > targetY):
            for piece in pieces:
                # check if other piece is in between
                if (piece[2] < y) and (piece[2] > targetY) and (piece[1] == x):
                    return False
        # moving down
        else:
            for piece in pieces:
                # check if other piece is in between
                if (piece[2] > y) and (piece[2] < targetY) and (piece[1] == x):
                    return False
    # rook moving on x axis
    elif (x!=targetX and y==targetY):
        # moving left 
        if (x > targetX):
            for piece in pieces:
                # check if other piece is in between
                if (piece[1] < x) and (piece[1] > targetX) and (piece[2] == y):
                    return False     
        # moving right
        else:
            for piece in pieces:
                # check if other piece is in between
                if (piece[1] > x) and (piece[1] < targetX) and (piece[2] == y):
                    return False
    # rook moving invalid
    else:
        return False
    
    return True

def validateBishop(bishop, targetX, targetY):
    x = bishop[1]
    y = bishop[2]
    xdif = max(x, targetX) - min(x, targetX)
    ydif = max(y, targetY) - min(y, targetY)
    # bishop moving diagonal
    if xdif == ydif:
        # moving left up
        if(x > targetX and y > targetY):
            # check if other piece is in the way
            for piece in pieces:
                xdif = max(piece[1], targetX) - min(piece[1], targetX)
                ydif = max(piece[2], targetY) - min(piece[2], targetY)
                if (xdif==ydif and (targetX-piece[1])<0 and (x-piece[1])>0 \
                    and (targetY-piece[2])<0 and (y-piece[2])>0):
                    return False
        # moving right up
        elif(x < targetX and y > targetY):
            # check if other piece is in the way
            for piece in pieces:
                xdif = max(piece[1], targetX) - min(piece[1], targetX)
                ydif = max(piece[2], targetY) - min(piece[2], targetY)
                if (xdif==ydif and (targetX-piece[1])>0 and (x-piece[1])<0 \
                    and (targetY-piece[2])<0 and (y-piece[2])>0):
                    return False
        # moving left down
        elif(x > targetX and y < targetY):
            # check if other piece is in the way
            for piece in pieces:
                xdif = max(piece[1], targetX) - min(piece[1], targetX)
                ydif = max(piece[2], targetY) - min(piece[2], targetY)
                if (xdif==ydif and (targetX-piece[1])<0 and (x-piece[1])>0 \
                    and (targetY-piece[2])>0 and (y-piece[2])<0):
                    return False
        # moving right down
        elif(x < targetX and y < targetY):
            # check if other piece is in the way
            for piece in pieces:
                xdif = max(piece[1], targetX) - min(piece[1], targetX)
                ydif = max(piece[2], targetY) - min(piece[2], targetY)
                if (xdif==ydif and (targetX-piece[1])>0 and (x-piece[1])<0 \
                    and (targetY-piece[2])>0 and (y-piece[2])<0):
                    return False
        # invalid move
        else:
            return False
    else:
        return False
    
    return True

def validateKnight(knight, targetX, targetY):
    x = knight[1]
    y = knight[2]
    # check if knight is moving valid
    if (targetX == x+200 or targetX == x-200) and (targetY == y+100 or targetY == y-100) \
        or (targetY == y+200 or targetY == y-200) and ((targetX == x+100) or (targetX == x-100)):
        return True
    # moving invalid
    else:
        return False

def validateKing(king, targetX, targetY):
    color = "green" if king[4].endswith("green") else "red"
    x = king[1]
    y = king[2]
    # check if moving only 1 field
    if (max(x, targetX) - min(x, targetX) <= 100) \
        and (max(y, targetY) - min(y, targetY) <= 100):
        # check if target field is checked by opponent
        if isChecked(color, targetX, targetY):
            return False
        else:
            return True
    # moving invalid
    else:
        return False

def validatePawn(pawn, targetX, targetY):
    global turn
    # check whos turn it is (if opps turn f.e. checking if pawn checks king - table is turned and other rules apply)
    color = "green" if turn%2!=0 else "red"
    x = pawn[1]
    y = pawn[2]
    if pawn[4].endswith(color):
        # moving backwards or more then two fields ahead or not at all
        if (y-targetY > 200 or y-targetY < 0 or y==targetY):
            return False
        # moving two fields ahead, from start position
        elif (x==targetX and y-targetY==200 and y==600):
            # check if piece blocks the way
            for piece in pieces:
                if piece[1]==x and (piece[2]==targetY or piece[2]==targetY+100):
                    return False
            return True
        # moving one field ahead
        elif (x==targetX and y-targetY==100):
            # check if field is occupied
            for piece in pieces:
                if piece[1]==targetX and piece[2]==targetY:
                    return False
            return True
        # moving more then one field sidewards or only sidewards
        elif (max(x, targetX) - min(x, targetX) > 100) or y==targetY:
            return False        
        # check if opponent is at target pos if moving diagonal
        elif x!=targetX and y-targetY==100:
            for piece in pieces:
                if piece[1]==targetX and piece[2]==targetY and piece[4][-3]!=pawn[4][-3]:
                    return True
            return False
    else:   
        # check if opponent is at target pos if moving diagonal
        if (max(targetX, x)-min(targetX, x))==100 and targetY-y==100:
            for piece in pieces:
                if piece[1]==targetX and piece[2]==targetY and piece[4][-3]!=pawn[4][-3]:
                    return True
            return False

    return False

def promotePawn(pawn, targetX):
    global popuplabel

    x = pawn[1]-100 if pawn[1]>=100 and pawn[1]<=500 else 200
    color = "green" if pawn[4].endswith("green") else "red"
    names = [
        "bishop",
        "knight",
        "queen",
        "rook"
    ]
    
    for name in names:
        path = "art/"+name+"_"+color+".png"
        image = tkinter.PhotoImage(file=path) 
        lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg="#123456")
        lb.image = image
        lb.place(x=x, y=0, anchor="nw")
        popuplabel.append([lb, x, 0, path, pieces.index(pawn), targetX])   # label, x, y, path, promotingPawnIndex, targetX
        x+=100
    
# check if a field is checked by the opponent
def isChecked(color, targetX=-1, targetY=-1):
    # if called without positional params, target is current king
    if targetX==-1:
        king = str("king_"+color)
        for piece in pieces:
            if piece[4].endswith(king):
                targetX = piece[1]
                targetY = piece[2]
    
    # check if opp is able to attack target
    for piece in pieces:
        if not piece[4].endswith(color):
            if validateTurn(piece, targetX, targetY, test=True):
                return True   

    return False

# check (after valid turn) if opponent is check mate
def isCheckMate(color):
    # player not checked - return
    if not isChecked(color):
        return

    # player is checked - check if player is able to cheat the gallows with any valid turn
    for piece in pieces:
        if piece[4].endswith(color):
            for field in fields:
                if validateTurn(piece, field[1], field[2], test=True):
                    saveXY = [piece[1], piece[2]]
                    piece[1] = field[1]
                    piece[2] = field[2]
                    # player not checked anymore
                    if not isChecked(color):
                        piece[1] = saveXY[0]
                        piece[2] = saveXY[1]
                        return
                    piece[1] = saveXY[0]
                    piece[2] = saveXY[1]

    # player is check mate
    checkMate()

# check mate - pause game and display winner
def checkMate():
    global status
    player = "green" if turn%2!=0 else "red"
    message = "check mate\nplayer "+player+" wins."
    print(message)
    message = "check mate! player "+player+" wins"
    setLabel(4, message)
    status = 1

# switch the board for the next player
def turnTable():
    global turn
    turn += 1
    reevaluatePieces()
    try:
        turnLabel = int((turn/2)+0.5)
        setLabel(3, turnLabel)
    except:
        message=("error: not able to update turn label item on menu bar")

# reevaluate position of pieces after each turn
def reevaluatePieces():
    global turn
    colors = getColors()
    # check xy coord and reevaluate them for the changed fields
    for piece in pieces:
        piece[0].destroy()      # destroy label, before rebuilding it
        if piece[1] >= 0:       # if smaller the piece got already destroyed
            for i in range(1,3,1):
                if piece[i]==700:
                    piece[i]=0
                elif piece[i]==600:
                    piece[i]=100
                elif piece[i]==500:
                    piece[i]=200
                elif piece[i]==400:
                    piece[i]=300
                elif piece[i]==300:
                    piece[i]=400
                elif piece[i]==200:
                    piece[i]=500
                elif piece[i]==100:
                    piece[i]=600
                elif piece[i]==0:
                    piece[i]=700
            ## put piece label back on top level
            image = piece[3]
            bgcolor = getBgColor(colors, piece[1], piece[2])
            lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg=bgcolor)
            lb.place(x=piece[1], y=piece[2], anchor="nw")
            piece[0] = lb

# start listener
listener = mouse.Listener(on_click=on_click)
listener.start()

# initialize frame
main = tkinter.Tk()
main.title("chess")
main.resizable(0, 0)
main.geometry("800x800+" + str(int(main.winfo_screenwidth()/2))+"+"+str(int(main.winfo_screenheight()/3))) # geometry(widthxheight+xoffset+yoffset) //offset to start from screen
## menu bar
# target for menu commands
fr = tkinter.Frame(main,  height=800, width=800, bg="#FFFFFF", bd=10)

# makes total menu bar
mBar = tkinter.Menu(main)
# makes objects for menu bar
mFile = tkinter.Menu(mBar)
mFile["tearoff"] = 0                    # menu not separable
mFile.add_command(label="new", command=turnTable)
mFile.add_command(label="pause/play", command=pause)
mFile.add_command(label="save")
mFile.add_separator()
mFile.add_command(label="close", command=end)

mBar.add_cascade(label="options", menu=mFile)
mView = tkinter.Menu(mBar)
mView["tearoff"] = 0                    # menu not separable
mBar.add_cascade(label="", menu=mView)  # time display generated empty, later updated with updateTime()
mBar.add_cascade(label="1", menu=mView) # turn display, initialized with '1', later updatet with var turn
mBar.add_cascade(label="", menu=mView)  # info display to update player on status

# add menu bar to frame
main["menu"] = mBar

##############################################################################################################################################################################################
## start game preparation
# chess board gets prepared... fields[i][label, x, y, color]
fields = initFields()
# pieces get prepared... pieces[i][label(in frame), x, y, image(rendered image), name(name of piece), selected(currently selected?)] 
pieces = initPieces()
turn = 1
isPromoting = False     # is a pawn promoting?
popuplabel = []         # to save (and destroy) labels for pawn promotion
## end game preparation
##############################################################################################################################################################################################

# start thread to show time in menu bar    
global status # 0 = exit, 1 = paused, 2 = play | flags for timethread
status = 2
timeThread = threading.Thread(name="timeThread", target=updateTime)
timeThread.start()

# put frame together and start mainloop
fr.pack()
main.mainloop()

### at this point the frame was closed ###
## if any, close all open instances
# stop time thread
status = 0
timeThread.killed = True
timeThread.join()
# stop listener
listener.stop()