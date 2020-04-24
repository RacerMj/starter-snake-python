import os
import random

import cherrypy


"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


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
        return {"color": "#ff9900", "headType": "regular", "tailType": "regular"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        
        # Get the game data as a json string
        data = cherrypy.request.json
        
        height = data["board"]["height"]
        width = data["board"]["width"]
        
        #x = 0 
        #y = 0
        #board = []
        #for x in range(width):
        #    col = []
        #    for y in range(height):
        #        col.append(0)
        #    board.append(col)
        #snakes = data["board"]["snakes"]
        #currentSnake = 1
        #for s in snakes:
        #    body = s["body"]
        #    snakehead = True
        #    for segment in body:
        #        if snakehead:
        #            board[segment["x"]][segment["y"]] = "99"
        #        else:
        #            board[segment["x"]][segment["y"]] = currentSnake
        #        snakehead = False
        #    currentSnake = currentSnake + 1
                 
        # Get my data from the parsed data
        # Set the target square to my head for now
        me = data["you"]
        myId = me["id"]
        # Get my head coordinates
        for segment in me["body"]:
            headX = segment["x"]
            headY = segment["y"]
            break
        
        goodMove = False
    
        # Choose a direction to move in
    
        # find closest food
        # get foodstuffs
        foodstuffs = data["board"]["food"]
        # set distance to farthest possible on board
        distanceToFood = width * 2
        targetFoodX = 0
        targetFoodY = 0
        # calculate the distance to each piece of food
        targetFood = {}
        for f in foodstuffs:
            distance = abs(headX-f["x"])+abs(headY-f["y"])
            
            # if this piece is closer, make it the new target
            if distance < distanceToFood:
                distanceToFood = distance
                targetFoodX = f["x"]
                targetFoodY = f["y"]
    
        # moves to try in order
        moveXList = []
        moveYList = []
        moveList = ["", "", "", ""]
        moveListResults = ["","","",""]
                                
        # what direction should we try first
        if headX > targetFoodX:
            moveXList = ["left", "right"]
        else:
            moveXList = ["right", "left"]
    
        # y is largest difference
        if headY > targetFoodY:
            moveYList = ["up", "down"]
        else:
            moveYList = ["down", "up"]
        
        # try to move in direction of largest difference
        if abs(headX-targetFoodX) > abs(headY-targetFoodY):
            # X is largest difference
            moveList = [moveXList[0], moveYList[0], moveXList[1], moveYList[1]]
        else:
            # y is largest difference
            moveList = [moveYList[0], moveXList[0], moveYList[1], moveXList[1]]
        
        # start with the first move
        currentMove = 0
        
        while goodMove == False and currentMove < 4:                
            move = moveList[currentMove]
            goodMove = True
            moveListResults[currentMove] = "yes"
            
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
                    
            # If the move is bad, go back to start to try another
            if goodMove == False:
                # increment the move to try
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
                    if (abs(body[0]["x"]-targetX) < 2 and abs(body[0]["y"]-targetY) < 2 and currentMove < 3):
                        goodMove = False
                        moveListResults[currentMove] = "maybe"
        
                # If we suspect a head collision, don't bother with other tests
                if goodMove == False:
                    # exit the loop
                    break
        
                # See if we're going to hit a snake segment, including me
                for segment in body:
                    # check for an impact with any body segment
                    if segment["x"] == targetX and segment["y"] == targetY:
                        goodMove = False
                        moveListResults[currentMove] = "no"
                        # exit the loop
                        break
                    
                # If we have a body impact, don't bother with other tests
                if goodMove == False:
                    # exit the loop
                    break
    
            # don't enter a closed box
            # we just want to see if the surrounding spaces are open or occupied
            if goodMove:
                blocked = True
                # check up
                if targetY-1 >= 0:
                    if board[targetX][targetY-1] == 0:
                        blocked = False
                # check down
                if targetY+1 < height:
                    if board[targetX][targetY+1] == 0:
                        blocked = False
                # check left
                if targetX-1 >= 0:
                    if board[targetX-1][targetY] == 0:
                        blocked = False
                # check right
                if targetX+1 < width:
                    if board[targetX+1][targetY] == 0:
                        blocked = False
                    
                if blocked:
                    goodMove = False
                    moveListResults[currentMove] = "no"

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

        print(f"move: {move}")
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
