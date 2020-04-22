import os
import random

import cherrypy
import json


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
        
        board = data["board"]
        height = board["height"]
        width = board["width"]
        
        # Get my data from the parsed data
        # Set the target square to my head for now
        me = data["you"]
        myBody = me["body"]
        for segment in myBody:
            headX = segment["x"]
            headY = segment["y"]
            break
        
        goodMove = False

        triedMoves = []
        possible_moves = ["right", "up", "down", "left"]
        while goodMove == False and len(triedMoves) < 4:
            
            if len(triedMoves) < 4: 
                # Choose a direction to move in
                while goodMove == False:
                    move = random.choice(possible_moves)
                    try:
                        # see if we've tried it already
                        moveIndex = triedMoves.index(move)
                    except ValueError:
                        # we got an error, indicating it wasn't in our triedMoves list
                        goodMove = True

                # Now adjust the target by the direction we're moving in             
                if move == "up":
                    targetY = headY - 1
                    
                elif move == "down":
                    targetY = headY + 1
                    
                elif move == "left":
                    targetX = headX - 1
                    
                else:
                    targetX = headX + 1
                    
                # If the target is out of bounds, this is not a good move
                if targetX < 0 or targetY < 0 or targetX >= width or targetY >= height:
                    goodMove = False
                    # Add the out of bounds move to the tried moves list
                    triedMoves.append(move)
                else:
                    goodMove = True
                
                # If the move is bad, go back to start to try another
                if goodMove == False:
                    # Skip the rest of the while loop and start at the top again
                    continue

                # Get the snakes data from the parsed data
                snakes = board["snakes"]
                for s in snakes:
                    body = s["body"]
                    for b in body:
                        if b["x"] == targetX and b["y"] == targetY:
                            goodMove = False
                            triedMoves.append(move)
                            break
                        
                    if goodMove == False:
                        break

                # If the move is bad, go back to start to try another
                if goodMove == False:
                    # Skip the rest of the while loop and start at the top again
                    continue

                # Get my own data from the parsed data
                snakes = data["you"]
                body = s["body"]
                for b in body:
                    if b["x"] == targetX and b["y"] == targetY:
                        goodMove = False
                        triedMoves.append(move)
                        break
            else:
                # no moves left, return whatever we have and die
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
