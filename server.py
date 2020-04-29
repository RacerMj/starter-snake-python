import os
import random
import time
import cherrypy


"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""

def pathBlocked(targetX, targetY, fromX, fromY, board, depth):
    # assume there are no exits to start
    blockExits = 0
    coords = []

    print("path check ", targetX, targetY)
    
    # This is a recursion limit check. Don't want to go too deep. Adjust as necessary
    if depth > 10:
        return False
            
    # Look for exits from the target square. If we find one, we'll follow it.
    # check up
    # not out of bounds
    if targetY-1 >= 0:
        # the square is empty, and not the square I'm coming from
        if board[targetX][targetY-1] == 0 and not (fromX == targetX and fromY == targetY-1):
            blockExits = blockExits + 1
            # got an exit, so let's go that way
            coords = [targetX, targetY-1]

    # check down
    if targetY+1 < len(board[0]):
        if board[targetX][targetY+1] == 0 and not (fromX == targetX and fromY == targetY+1):
            blockExits = blockExits + 1
            # got an exit, so let's go that way
            coords = [targetX, targetY+1]

    # check left
    if targetX-1 >= 0:
        if board[targetX-1][targetY] == 0 and not (fromX == targetX-1 and fromY == targetY):
            blockExits = blockExits + 1
            # got an exit, so let's go that way
            coords = [targetX-1, targetY]

    # check right
    if targetX+1 < len(board[0]):
        if board[targetX+1][targetY] == 0 and not (fromX == targetX+1 and fromY == targetY):
            blockExits = blockExits + 1
            # got an exit, so let's go that way
            coords = [targetX+1, targetY]

    # no exits found
    if blockExits > 1:
        return False
    elif blockExits == 1:
        return pathBlocked(coords[0], coords[1], targetX, targetY, board, depth+1)
    else:
        return True


# count the volume (number of squares available from the target square)
# this routine will keep counting until we have counted every square available
def getVolume(targetX, targetY, fromX, fromY, board, coordsList, maxVolume):
    # Look for exits from the target square. If we find one, we'll follow it.
    testSquares = [[targetX, targetY-1], [targetX+1, targetY], [targetX, targetY+1], [targetX-1, targetY]]
    
    for ts in testSquares:
        # don't bother checking further if we're already at the max volume we need
        if(len(coordsList) > maxVolume):
            return 

        # out of bounds?
        if not (ts[0] < 0 or ts[0] > len(board[0])-1  or ts[1] < 0 or ts[1] > len(board[0])-1):
            # the square is empty, and not the square I'm coming from
            if board[ts[0]][ts[1]] == 0 and not (fromX == ts[0] and fromY == ts[1]):
                # got an exit, so let's go that way
                if ts not in coordsList:
                    coordsList.append(ts)
                    # then recurse
                    getVolume(ts[0], ts[1], targetX, targetY, board, coordsList, maxVolume)
            
    
class Battlesnake(object):
    @cherrypy.expose
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return "Your Battlesnake is alive!"


    @cherrypy.expose
    def ping(self):
        # The Battlesnake engine calls this function to make sure your snake is working.
        return "Version 0.1"


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json
        print("START")
        return {"color": "#ffbf00", "headType": "bwc-earmuffs", "tailType": "shac-mouse"}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        
        # Get the game data as a json string
        data = cherrypy.request.json
        
        runTime = int(round(time.time() * 1000))

        height = data["board"]["height"]
        width = data["board"]["width"]
        
        # turn the board into an array for easier checking of blocked areas
        board = []
        for x in range(width):
            col = []
            for y in range(height):
                col.append(0)
            board.append(col)
    
        snakes = data["board"]["snakes"]
        for s in range(len(snakes)):
            body = snakes[s]["body"]
            for i in range(len(body)):
                if i == 0:
                    # head
                    board[body[i]["x"]][body[i]["y"]] = (s+1)*100+(i+1)
                    
                elif i == len(body)-1 and len(body)>1:
                    # tail
                    board[body[i]["x"]][body[i]["y"]] = (s+1)*100+99
                    
                else:
                    # body segment
                    board[body[i]["x"]][body[i]["y"]] = (s+1)*100+(i+1)
                    
        # Get my data from the parsed data
        # Set the target square to my head for now
        me = data["you"]
        myId = me["id"]
        myLength = len(me["body"])
        myHealth = me["health"]
        # Get my head coordinates
        for segment in me["body"]:
            headX = segment["x"]
            headY = segment["y"]
            break
        
        goodMove = False
    
        # Choose a direction to move in
        # moves to try in order
        moveXList = []
        moveYList = []
        moveList = ["", "", "", ""]
        moveListResults = ["","","",""]
                                
    
        # if we're hungry, or smaller than opponents, find closest food
        tooSmall = False
        snakes = data["board"]["snakes"]
        for s in range(len(snakes)):
            if snakes[s]["id"] != myId and myLength < len(snakes[s]["body"])+1:
                tooSmall = True
                break
                
        if myHealth < 10 or tooSmall :
            # get foodstuffs
            foodstuffs = data["board"]["food"]
            # set distance to farthest possible on board
            distanceToFood = width * 2
            farTargetX = 0
            farTargetY = 0
            # calculate the distance to each piece of food
            targetFood = {}
            for f in foodstuffs:
                distance = abs(headX-f["x"])+abs(headY-f["y"])
                
                # if this piece is closer, make it the new target
                if distance < distanceToFood:
                    distanceToFood = distance
                    farTargetX = f["x"]
                    farTargetY = f["y"]

        else:
            # Move clockwise if we're on a wall
            if headX == 1:
                if headY == 1:
                    farTargetX = width-2
                    farTargetY = 1
                else:
                    farTargetX = 1
                    farTargetY = 1

            elif headX == width-2:
                if headY == height-2:
                    farTargetX = 1
                    farTargetY = height-2
                else:
                    farTargetX = width-2
                    farTargetY = height-2

            elif headY == 1:
                if headX == width-2:
                    farTargetX = width-2
                    farTargetY = height-2
                else:
                    farTargetX = width-2
                    farTargetY = 1
                   
            elif headY == height-2:
                if headX == 1:
                    farTargetX = 1
                    farTargetY = 1
                else:
                    farTargetX = 1
                    farTargetY = height-2
                   
            else:
                # we're not on one of the sides, so move to closest wall
                if headX < width/2:
                    farTargetX = 1
                else:
                    farTargetX = width-1
                if headY < height/2:
                    farTargetY = 1
                else:    
                    farTargetY = height-2
            
        # what direction should we try first
        if headX > farTargetX:
            moveXList = ["left", "right"]
        else:
            moveXList = ["right", "left"]
    
        # y is largest difference
        if headY > farTargetY:
            moveYList = ["up", "down"]
        else:
            moveYList = ["down", "up"]
    
         # try to move in direction of largest difference
        if abs(headX-farTargetX) > abs(headY-farTargetY):
            # X is largest difference
            # if y difference is zero, make y moves second priority
            if (headY - farTargetY) == 0:
                moveList = [moveXList[0], moveYList[0], moveYList[1], moveXList[1]]
            else:
                moveList = [moveXList[0], moveYList[0], moveXList[1], moveYList[1]]
        else:
            # y is largest difference
            # if x difference is zero, make x moves second priority
            if (headX - farTargetX) == 0:
                moveList = [moveYList[0], moveXList[0], moveXList[1], moveYList[1]]
            else:
                moveList = [moveYList[0], moveXList[0], moveYList[1], moveXList[1]]
       
        # start with the first move
        currentMove = 0
        
        while goodMove == False and currentMove < 4:                
            move = moveList[currentMove]
            goodMove = True
            moveListResults[currentMove] = "yes"
            print("Trying move " + move)
            
            # Now adjust the target by the direction we're moving in             
            if move == "up":
                targetX = headX
                targetY = headY - 1
                
            elif move == "down":
                targetX = headX
                targetY = headY + 1
                
            elif move == "left":
                targetY = headY
                targetX = headX - 1
                
            else:
                targetY = headY
                targetX = headX + 1
                        
            # If the target is out of bounds, this is not a good move
            if targetX < 0 or targetY < 0 or targetX >= width or targetY >= height:
                goodMove = False
                print("Target square is out of bounds")
                # increment the move to try
                currentMove = currentMove + 1
                # Skip the rest of the while loop and start at the top again
                continue
    
             # See if we're going to hit a snake segment, including me
            if board[targetX][targetY] % 100 == 99: 
                print("Going to hit a snake tail")
                # maybe this should be a maybe
            elif board[targetX][targetY] % 100 > 0:
                goodMove = False
                moveListResults[currentMove] = "no"
                print("Going to hit a snake segment")
                currentMove = currentMove + 1
                # Skip the rest of the while loop and start at the top again
                continue
                
           # Get the snakes data from the parsed data
            snakes = data["board"]["snakes"]
            for s in snakes:
                body = s["body"]
    
                # We want to avoid contesting with another snakehead
                if s["id"] != myId:
                    # Check for these conditions:
                    # Another snake head is next to the target square
                    # I have moves left to try. I will only contest if it's my last choice
                    if (abs(body[0]["x"]-targetX) < 2 and abs(body[0]["y"]-targetY) < 2):
                        #if (len(body)+1 > myLength and currentMove < 3):
                        # slightly more aggressive version of line above, takes the square as long as we're bigger
                        if (len(body)+1 > myLength):
                            goodMove = False
                            moveListResults[currentMove] = "maybe"
                            print("Might hit a snakehead")
        
                # If we have an impact, don't bother with other tests
                if goodMove == False:
                    # exit the loop
                    break
    
            # don't enter a closed box
            # we  want to see if the surrounding spaces are open or occupied
            if goodMove:
                #blocked = pathBlocked(targetX, targetY, headX, headY, board, 1)
                blocked = False
                coordsList = []
                getVolume(targetX, targetY, headX, headY, board, coordsList, myLength)
                print(coordsList)
                if len(coordsList) < myLength:
                    blocked = True
                
                if blocked:
                    goodMove = False
                    moveListResults[currentMove] = "maybe"
                    print("Target square is blocked")

            # If the move hits another snake segment, this is not a good move
            if goodMove == False:
                # increment the move to try
                currentMove = currentMove + 1
    
        # If we don't have a good move, try a maybe
        if not goodMove:
            i = 0
            for i in range(len(moveListResults)):
                if moveListResults[i] == "maybe":
                    move = moveList[i] 
                    break
    
        runTime = (int(round(time.time() * 1000))-runTime)
        if runTime > 500:
            stdout.write("#### HURRY UP! Runtime: " + str(runTime) + "\n")
        return {"move":move}    


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json
        print("END")
        return "ok"


if __name__ == "__main__":
    random.seed()
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
