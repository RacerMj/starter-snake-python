import os
import random
import time
import cherrypy


"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""

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
            if (board[ts[0]][ts[1]] == 0 or board[ts[0]][ts[1]] %100 == 99) and not (fromX == ts[0] and fromY == ts[1]):
                # got an exit, so let's go that way
                if ts not in coordsList:
                    coordsList.append(ts)
                    # then recurse
                    getVolume(ts[0], ts[1], targetX, targetY, board, coordsList, maxVolume)
            
    
def possibleHeadCollision(targetX, targetY, fromX, fromY, board, snakeLengths):
    # default result is no potential head collision
    result = 0
    
    # Look for other snake heads around the target square
    testSquares = [[targetX, targetY-1], [targetX+1, targetY], [targetX, targetY+1], [targetX-1, targetY]]

    for ts in testSquares:
        # Both coords need to be on the board
        if ts[0] in range(len(board[0])) and ts[1] in range (len(board[0])):
            # the square is a head, and not the square I'm coming from (me)
            if (board[ts[0]][ts[1]] % 100 == 1) and not (fromX == ts[0] and fromY == ts[1]):
                # get the snake's length for our return
                temp = snakeLengths[int(board[ts[0]][ts[1]]/100)-1]
                if temp > result:
                    result = temp
    
    return result


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
        
        # get the time
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
    
        # Copy all snake data into the board. First snake is 100, second 200, etc. Tail is x99
        # Eg. First snake: 101, 102, 103, 199
        # Second snake: 201, 202, 203, 299
        # Unoccupied squares remain 0
        snakeLength = []
        snakes = data["board"]["snakes"]
        for s in range(len(snakes)):
            body = snakes[s]["body"]
            # save the length of each snake so we don't have to look it up again later
            snakeLength.append(len(body))
            
            # write the body bits into the board array
            for i in range(snakeLength[s]):
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
            if headX == 0:
                if headY == 0:
                    farTargetX = width-1
                    farTargetY = 0
                else:
                    farTargetX = 0
                    farTargetY = 0
    
            elif headX == width-1:
                if headY == height-1:
                    farTargetX = 0
                    farTargetY = height-1
                else:
                    farTargetX = width-1
                    farTargetY = height-1
    
            elif headY == 0:
                if headX == width-1:
                    farTargetX = width-1
                    farTargetY = height-1
                else:
                    farTargetX = width-1
                    farTargetY = 0
                   
            elif headY == height-1:
                if headX == 0:
                    farTargetX = 0
                    farTargetY = 0
                else:
                    farTargetX = 0
                    farTargetY = height-1
                   
            else:
                # we're not on one of the sides, so move to closest wall
                if headX < width/2:
                    farTargetX = 0
                else:
                    farTargetX = width-1
                if headY < height/2:
                    farTargetY = 0
                else:    
                    farTargetY = height-1
            
        # what direction should we try first
        if headX > farTargetX:
            moveXList = ["left", "right"]
        else:
            moveXList = ["right", "left"]
    
        # y 
        if headY > farTargetY:
            moveYList = ["up", "down"]
        else:
            moveYList = ["down", "up"]
    
         # try to move in direction of largest difference
        if abs(headX-farTargetX) > abs(headY-farTargetY):
            # X is largest difference
            moveList = [moveXList[0], moveYList[0], moveXList[1], moveYList[1]]
        else:
            # y is largest difference
            moveList = [moveYList[0], moveXList[0], moveYList[1], moveXList[1]]
       
        # start with the first move
        currentMove = 0
        print(moveList)
        
        # Possible moves from best to worst
        # 0 - Open square
        # 1 - Possible head collision if I am longer than other snake
        # 1 - Tail collision if I am shorter
        # 2 - Possible head collision if I am shorter
        # 2 - Tail collision if I am longer
        # 3 - Mostly blocked (no exit but more than half my volume)
        # 4 - Totally blocked (no exit and less than/equal to half my volume
        # 5 - Body collision
        # 6 - Wall collision
        
        #while goodMove == False and currentMove < 4:
        for currentMove in range(len(moveList)):                
            move = moveList[currentMove]
            goodMove = True
            moveListResults[currentMove] = 0
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
    
            coordsList = []
            getVolume(targetX, targetY, headX, headY, board, coordsList, myLength)
            blocked = len(coordsList)
            
            headBanger = possibleHeadCollision(targetX, targetY, headX, headY, board, snakeLength)
                        
            # Check for wall collision < 0 or greater than width
            if targetX not in range(width) or targetY not in range(width):
                print("Going to hit a wall")
                goodMove = False
                moveListResults[currentMove] = 999
                # Skip the rest of the while loop and start at the top again
                continue
    
            # Check for body collision               
            elif board[targetX][targetY] % 100 > 0:
                print("Going to hit a snake segment")
                goodMove = False
                moveListResults[currentMove] = 899
                # Skip the rest of the while loop and start at the top again
                continue
    
            # Check for mostly blocked where available path is < my body length              
            elif len(coordsList) < myLength:
                print("Target square is blocked")
                goodMove = False
                moveListResults[currentMove] = 100-len(coordsList)
                # Skip the rest of the while loop and start at the top again
                continue
    
            elif headBanger > 0 and headBanger >= myLength:
                print("Possible head collision")
                goodMove = False
                moveListResults[currentMove] = 2
                # Skip the rest of the while loop and start at the top again
                continue
                            
            # See if we're going to hit a snake segment, including me
            elif board[targetX][targetY] % 100 == 99: 
                print("Going to hit a snake tail")
                goodMove = False
                moveListResults[currentMove] = 1
                # Skip the rest of the while loop and start at the top again
                continue
            
        # Take the highest ranked move
        bestMove = 1001
        print(moveListResults)
        for r in range(len(moveListResults)):
            if moveListResults[r] < bestMove:
                bestMove = moveListResults[r]
                move = moveList[r]
    
        print("Best move is ", move)
    
        runTime = (int(round(time.time() * 1000))-runTime)
        if runTime > 500:
            stdout.write("run time too long: " + str(runTime) + "\n")
            
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
