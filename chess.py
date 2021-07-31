#/usr/bin/python
#-*- coding:utf-8 -*-
# pip3 install tkinter
# pip3 install pynput
## lokales Schachspiel ##
import threading
import time
import tkinter
from pynput import mouse, keyboard

# destroys frame
def end():
    main.destroy()   

# updates time passed since start
def updateTime():
    whitespace = str(" " * 20) # since a menuitem (used as clock) is not positionable, whitespaces are used to place clock further right
    seconds = 0
    minutes = 0
    while threading.main_thread().is_alive():
        # status[0:exit, 1:paused, 2:play]
        if status == 2:
            time.sleep(1)
            seconds += 1
            if seconds == 60:
                seconds = 0
                minutes += 1
            timeStr = str(whitespace \
                        + "{:0>2}".format(minutes) + ":" \
                        + "{:0>2}".format(seconds))
            try:
                mBar.entryconfig(2, label = timeStr)
            except:
                continue
        elif status == 0:
            return

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
    
def initField():
    ## bereite Spielbrett vor
    # platziere Felder
    path = "art/empty_white_field.png"
    color = "#FFFFFF"
    x = int(0)
    y = int(0)
    for i in range(8):
        for j in range(8):
            image = tkinter.PhotoImage(file=path)
            lb = tkinter.Label(main, image=image, relief="ridge", bd=1, bg=color)
            lb.place(x=x, y=y, anchor="nw")

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

##initializes and returns pieces 
def initPieces():
    pieces = [] # hier werden die Labels der Bilder gespeichert samt x und y-Koordinate und dem gerenderten Bild pieces[piecenr][label, x, y, image, name, selected]
    colors = getColors()
    path = ["art/tower_red.png", "art/horse_red.png", "art/bishop_red.png", "art/queen_red.png", "art/king_red.png", "art/bishop_red.png", "art/horse_red.png", "art/tower_red.png", "art/pawn_red.png"]
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
# TO:DO evaluate piece to move
#       function for replacing pieces
#                   for logic checks 
def on_click(x, y, button, pressed):
    if isTopLevel():
        pos = getPos(x, y)
        x = pos[0]
        y = pos[1]
        if pressed:         # mouse pressed
            for i in range(len(pieces)):
                if (pieces[i][1]==x and pieces[i][2]==y):   # checks if a piece gets selcted by the player
                    pieces[i][5] = True                     # piece[5] = 'selected', a boolean property to determine if the piece is selected
        else:               # mouse released
            toMove = -1
            for i in range(len(pieces)):
                if pieces[i][5]==True:
                    toMove = i
            if toMove != -1:
                pieces[toMove][5] = False
                # make turn validation with the chosen piece, targetX and targetY
                if validateTurn(pieces[toMove], x, y):
                    # move piece after validation
                    move(pieces[toMove], x, y)
                    fr.pack()

# checkt ob Fenster im Vordergrund ist
def isTopLevel():
    width, height, x, y = main.winfo_width(), main.winfo_height(), \
                              main.winfo_rootx(), main.winfo_rooty()

    if (width, height, x, y) != (1, 1, 0, 0):
            is_toplevel = main.winfo_containing(x + (width // 2),
                                                y + (height // 2)
                                                ) is not None
            return is_toplevel

# validiere Zug
def validateTurn(chosenPiece, targetX, targetY):
    name = str(chosenPiece[4])
    x = int(chosenPiece[1])
    y = int(chosenPiece[2])
    print("x",x,"y",y,"targetX",targetX,"targetY",targetY)

    # no move made, return
    if x==targetX and y==targetY:
        return False

    # tower selected
    if name.startswith("tower"):
        if not validateTower(chosenPiece, targetX, targetY):
            return False
    # bishop selected     
    elif name.startswith("bishop"):
        if not validateBishop(chosenPiece, targetX, targetY):
            return False
    # horse selected
    elif name.startswith("horse"):
        if not validateHorse(chosenPiece, targetX, targetY):
            return False
    # queen selected
    elif name.startswith("queen"):
        if not (validateTower(chosenPiece, targetX, targetY) \
                or validateBishop(chosenPiece, targetX, targetY)):
            return False
    elif name.startswith("king"):
        if not validateKing(chosenPiece, targetX, targetY):
            return False
    elif name.startswith("pawn"):
        print

    # checks if an other piece is targeted
    for piece in pieces:
        if (piece[1]==targetX and piece[2]==targetY) and (piece[0]!=chosenPiece[0]):
            # target is of the same color
            if (name[-3]==piece[4][-3]):
                return False
            else:
                piece[0].destroy()
                piece[1] = -1
                piece[2] = -1

    print("valid: True")
    return True

def validateTower(tower, targetX, targetY):
    x = tower[1]
    y = tower[2]
    # tower moving on y axis
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
    # tower moving on x axis
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
    # tower moving invalid
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
                    print("piece between")
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

def validateHorse(horse, targetX, targetY):
    x = horse[1]
    y = horse[2]
    # check if horse is moving valid
    if (targetX == x+200 or targetX == x-200) and (targetY == y+100 or targetY == y-100) \
        or (targetY == y+200 or targetY == y-200) and ((targetX == x+100) or (targetX == x-100)):
        return True
    # moving invalid
    else:
        return False

def validateKing(king, targetX, targetY):
    x = king[1]
    y = king[2]
    # check if moving only 1 field
    if (max(x, targetX) - min(x, targetX) <= 100) \
        and (max(y, targetY) - min(y, targetY) <= 100):
        print("ok")
        return True
    else:
        return False

# starte Listener
listener = mouse.Listener(on_click=on_click)
listener.start()

# Erstelle Frame
main = tkinter.Tk()
main.title("chess")
main.resizable(0, 0)
main.geometry("800x800+" + str(int(main.winfo_screenwidth()/2))+"+"+str(int(main.winfo_screenheight()/3))) # geometry(widthxheight+xoffset+yoffset) //offset to start from screen
## Menueleiste
# Zielobjekt der Menuebefehle
fr = tkinter.Frame(main,  height=800, width=800, bg="#FFFFFF", bd=10)

# erzeugt gesamte Menueleiste
mBar = tkinter.Menu(main)
# erzeugt Menueobjekte der Menueleiste
mFile = tkinter.Menu(mBar)
mFile["tearoff"] = 0 # Menue nicht abtrennbar
mFile.add_command(label="neu")
mFile.add_command(label="laden")
mFile.add_command(label="speichern")

mBar.add_cascade(label="Datei", menu=mFile)
mView = tkinter.Menu(mBar)
mView["tearoff"] = 0 # Menue nicht abtrennbar
mBar.add_cascade(label="00:00", menu=mView)

# füge Menueleiste dem Fenster hinzu
main["menu"] = mBar

##############################################################################################################################################################################################
## Vorbereitung Spiel
# Spielfeld wird vorbereitet
initField()
# Figuren werden vorbereitet und pieces freigegeben pieces[i][label(Label im Frame), x, y, image(gerendertes Bild), name(Figurname), selected(gerade ausgewählt?)] 
pieces = initPieces()
## Ende Spielvorbereitung
##############################################################################################################################################################################################

# starte Thread um Zeit in der Menueleiste anzuzeigen    
global status # 0 = exit, 1 = paused, 2 = play | flag für Zeitthread [...]
status = 2
timeThread = threading.Thread(name="timeThread", target=updateTime)
timeThread.start()

# setze Frame zusammen und starte mainloop
fr.pack()
main.mainloop()

### Frame wurde geschlossen
## schließe ggf. offene Instanzen
# stoppe Zeitthread
status = 0
timeThread.killed = True
timeThread.join()
# stoppe Listener
listener.stop()