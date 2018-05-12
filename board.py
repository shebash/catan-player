# This file contains classes for the Catan board.

import re
import ast
from enum import Enum, unique
from collections import Counter
from collections import OrderedDict
from player import *


@unique
class Card(Enum):
    KNIGHT = 1
    RESOURCE = 2
    ROAD_BUILDING = 3
    YEAR_OF_PLENTY = 4
    MONOPOLY = 5

    def FromString(s):
        s = s.upper()
        for c in Card:
            if c.name == s:
                return c
        return False


@unique
class Resource(Enum):
    ORE = 1
    BRICK = 2
    GRAIN = 3
    LUMBER = 4
    WOOL = 5

    def FromString(s):
        s = s.upper()
        for r in Resource:
            if r.name == s:
                return r
        return False


class Node:
    def __init__(self):
        self.owner = None  # color, or none
        self.structure = 0  # 0, 1 for settlement, 2 for city none
        self.port = None  # port type or None
        self.returns = {}  # dict of num:resource, or probability of resource
        self.neighbors = {}  # {neighborNode:edgeColor}


class CatanBoard:
    def __init__(self):
        self.nodelist = {}  # location:node. 54 total nodes
        self.edgelist = {}  # edgename:color ?? or color:[(locA,locB)]
        self.players = OrderedDict()  # color:player
        self.deck = []  # stack of dev cards
        self.winner = False

    def play(self):
        # Setup
        self.setTerrain(self.buildTileList())
        self.addPorts()
        # Assign player colors
        players = input(
            "Enter color of other players in clockwise order, starting to your left "
            "(comma separated like red,white,orange): ")
        clrList = players.split(",")
        self.addPlayers(clrList)
        compColor = input("Which color am I playing as? ")
        self.players[compColor] = Computer(compColor)
        playerIndex = self.initialPlacement()
        print("Finished Initial Placement")
        # TODO Added playing of each turn
        while not self.winner:
            current_player = list(self.players.values())[
                playerIndex % len(self.players)]
            current_player.playTurn(self)
            playerIndex += 1

    def initialPlacement(self):
        print("running inital placement")
        pFirst = input("Who is first? ")
        iFirst = list(self.players.keys()).index(pFirst)
        for i in range(iFirst, iFirst + ((2 * len(self.players)) - 1)):
            current_player = list(self.players.values())[i % len(self.players)]
            print("Current Turn: Player {}".format(current_player.color))
            current_player.initPlace(self)
        return iFirst

    def buildTileList(self):
        tList = []
        lMap = {'g': 'grain', 'b': 'brick', 'o': 'ore',
                'l': 'lumber', 'w': 'wool', 'd': 'desert'}
        while True:
            com = input('Next Tile:')
            if com == "build":
                return tList
            if com == "undo":
                tList.pop()
            if com == "default":
                tList = [
                    ('ore', 10), ('wool', 2), ('lumber', 9), ('grain', 12), ('brick', 6),
                    ('wool', 4), ('brick', 10), ('grain', 9), ('lumber', 11), ('desert', 0),
                    ('lumber', 3), ('ore', 8), ('lumber', 8), ('ore', 3), ('grain', 4),
                    ('wool', 5), ('brick', 5), ('grain', 6), ('wool', 11)]
                return tList
            else:
                resource = lMap.get(com[-1:], 'desert')
                number = int(com[0:-1])
                tList.append((resource, number))

    def addPlayers(self, colorList):
        for color in colorList:
            self.players[color] = Human(color)

    def addPort(self, location, portType):
        self.nodelist[location].port = portType

    def addPorts(self):
        preset = input("To set default ports, type 'default'. Any other key for custom.  ")
        if preset == "default":
            for loc in [(2,1),(3,0),(5,0),(6,1),(10,7),(10,9),(2,15),(3,16)]:
                self.addPort(loc, "ANYTHING")
            #Sheep
            self.addPort((8,3),"WOOL")
            self.addPort((9,4),"WOOL")
            #BRICK
            self.addPort((1,4),"BRICK")
            self.addPort((1,6),"BRICK")
            #LUMBER
            self.addPort((1,10),"LUMBER")
            self.addPort((1,12),"LUMBER")
            #ORE
            self.addPort((9,12),"ORE")
            self.addPort((8,13),"ORE")
            #GRAIN
            self.addPort((5,16),"GRAIN")
            self.addPort((6,15),"GRAIN")
        else:
            for i in range(18):
                location = inValLoc("What's the location of the port node? (x,y)port. OR type 'default' to set default ports ")
                portType = input("What resource? (BRICK, ORE, ETC. OR ANYTHING)")
                # TODO gotta make "portType" convert to and check for enum
                self.addPort(location, portType)

    def buildDev(self, color):
        print("build dev card")
        # subtract resources, add dev card to hand

    def addNode(self, location):
        self.nodelist[location] = Node()

    def buildSettle(self, color, location):
        # this needs to use resources
        selecNode = self.nodelist[location]
        selecNode.owner = color
        selecNode.structure = 1
        player = self.players[color]
        player.victoryPoints += 1  # this is faster than running the function

    def buildCity(self, location):
        selecNode = self.nodelist[location]
        selecNode.structure = 2
        self.players[selecNode.owner].updateVPs()

    def buildRoad(self, color, fromLoc, toLoc):
        fromNode = self.nodelist[fromLoc]
        toNode = self.nodelist[toLoc]
        fromNode.neighbors[toNode] = color
        toNode.neighbors[fromNode] = color
    
    def validInitSetPlace(self):
        openNodes = [key for key in self.nodelist if self.nodelist[key].owner == None]
        realOptions = [loc for loc in openNodes if len([n for n in self.nodelist[loc].neighbors if n.owner!=None])==0]
        print("Possible Settlement Locations: {}".format(realOptions))
        return realOptions

    def setTerrain(self, tileList):
        # list tiles left->right and top->bottom
        # These tupes are x/y coordinates of tile centers
        tileLocs = [(3, 14), (5, 14), (7, 14),
                    (2, 11), (4, 11), (6, 11), (8, 11),
                    (1, 8), (3, 8), (5, 8), (7, 8), (9, 8),
                    (2, 5), (4, 5), (6, 5), (8, 5),
                    (3, 2), (5, 2), (7, 2)]
        for index, item in enumerate(tileList):
            tl = tileLocs[index]
            x = tl[0]
            y = tl[1]
            nodeLocs = [(x - 1, y + 1), (x, y + 2), (x + 1, y + 1),
                        (x - 1, y - 1), (x, y - 2), (x + 1, y - 1)]
            for loc in nodeLocs:
                if loc not in self.nodelist:
                    self.addNode(loc)
                self.nodelist[loc].returns[item[1]] = item[0]
                for adj in [
                        (loc[0] + 1, loc[1] - 1), (loc[0], loc[1] - 2), (loc[0] - 1, loc[1] - 1),
                        (loc[0] - 1, loc[1] + 1), (loc[0], loc[1] + 2), (loc[0] + 1, loc[1] + 1)]:
                    if adj in self.nodelist:
                        # assign adjacent neighbors
                        self.nodelist[loc].neighbors[self.nodelist[adj]] = None
