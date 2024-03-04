
# libs
import dearpygui.dearpygui as dpg
import random
from creature import Creature
from neuron import Neuron
import math



# grid functions
def printGrid():
    for i in grid:
        print(i)

def displayGrid():
    for i in range(gridY):
        for j in range(gridX):
            dpg.draw_rectangle((10 + j * 20, 10 + i * 20), (20 + j * 20, 20 + i * 20), color=(255, 255, 255), parent=simArea)

def updateGrid():
    global simArea
    if dpg.does_item_exist(simArea):
        dpg.delete_item(simArea)
    with dpg.drawlist(width=920, height=920, tag="simArea", parent=gridWin) as simArea:
        dpg.draw_rectangle((10, 10), (910, 910), color=(255, 255, 255))
        dpg.draw_rectangle((aliveStartX+10, aliveStartY+10), (aliveEndX+10, aliveEndY+10), color=(0, 255, 0), fill=(0, 255, 0, 20), parent=simArea)
        for i, line in enumerate(grid):
            for j, index in enumerate(line):
                if grid[i][j] != 0:
                    dpg.draw_circle((20 + j * 20, 20 + i * 20), 10, color=(0, 0, 0, 0), fill=index.color, parent=simArea)
        showIds()

def showIds():
    global simArea
    if dpg.get_value(showIdsCb):
        for i in creatures:
            dpg.draw_text((i.pos[0] * 20 + 10, i.pos[1] * 20 + 10), text=str(i.cId), size=20, color=(0, 0, 0), parent=simArea)

# additional functions for creatures
def generateRandomHex(length):
    return ''.join(random.choice('0123456789abcdef') for i in range(length))

def readConnection(gene):
    binary = (str(bin(int(gene, 16))[2:])).rjust(32, "0")
    source = int(binary[1:8], 2)
    if binary[0] == "0": # 0 = sensory, 1 = internal
        sourceType = "sensory"
        sourceId = source % len(sensoryList)
    else:
        sourceType = "internal"
        sourceId = source % len(internalList)

    sink = int(binary[9:16], 2)
    if binary[8] == "0": # 0 = internal, 1 = action
        sinkType = "internal"
        sinkId = sink % len(internalList)
    else:
        sinkType = "action"
        sinkId = sink % len(actionList)

    #print(binary[18:])
    #print(int(binary[18:], 2)/4000)
    weight = int(binary[18:], 2) / 4000
    if binary[17] == "1":
        weight *= -1
    return sourceType, sourceId, sinkType, sinkId, weight

def gen50():
    for i in range(50):
        playGeneration()
        nextGeneration()

def generateBrains():
    with dpg.window(label='Brains', width=600, height=1000, pos=(1000, 0), collapsed=True):
        for i in creatures:
            with dpg.tree_node(label="Creature " + str(i.cId)):
                with dpg.tree_node(label="Sensory"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sourceType == "sensory":
                            dpg.add_text(sensoryList[sourceId].name + " -> " + actionList[sinkId].name + " " + str(weight))
                with dpg.tree_node(label="Internal"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sourceType == "internal":
                            dpg.add_text(internalList[sourceId].name + " -> " + actionList[sinkId].name + " " + str(weight))
                with dpg.tree_node(label="Action"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sinkType == "action":
                            dpg.add_text(actionList[sinkId].name + " " + str(weight))





def nextGeneration():
    global creatures, genNum, grid, currStep
    if currStep < steps:
        return
    currStep = 0
    genNum += 1
    dpg.set_value(generationText, "Generation: " + str(genNum))
    alive = []
    for i in creatures:
        if not i.eliminated:
            alive.append(i)
    creatures.clear()
    positions = []
    for i, cre in enumerate(alive):
        cre.color = (255, 0, 0)
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        while pos in positions:
            pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        cre.pos = pos
        cre.cId = i
        if random.randrange(0, mutation) == 0:
            index = random.randrange(0, 9)
            gene = random.choice(cre.genes)
            cre.genes.remove(gene)
            newGene = gene[:index] + generateRandomHex(1) + gene[index+1:]
            cre.genes.append(newGene)

        positions.append(pos)
        creatures.append(cre)
    for i in range(numCreatures-len(creatures)):
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        while pos in positions:
            pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        genes = random.choice(creatures).genes.copy()
        if random.randrange(0, mutation) == 0:
            index = random.randrange(0, 9)
            gene = random.choice(cre.genes)
            cre.genes.remove(gene)
            newGene = gene[:index] + generateRandomHex(1) + gene[index+1:]
            cre.genes.append(newGene)
        creatures.append(Creature(pos, genes, defaultAction, i + len(alive)))
    grid.clear()
    for i in range(gridY):
        column = []
        for j in range(gridX):
            column.append(0)
        grid.append(column)
    for i in creatures:
        grid[i.pos[1]][i.pos[0]] = i
    updateGrid()


def playGeneration():
    global currStep
    while currStep < steps:
        step()
        currStep += 1
    for i in creatures:
        if i.pos[0] >= aliveStartX/20 and i.pos[0] < aliveEndX/20 and i.pos[1] >= aliveStartY/20 and i.pos[1] < aliveEndY/20:
            i.color = (0, 255, 0)
        else:
            i.color = (255, 255, 0)
            i.eliminated = True
    updateGrid()

def step():
    global currStep
    if currStep >= steps:
        return
    for creature in creatures:
        connections = []
        print()
        print(creature.cId)
        for connection in creature.genes:
            sourceType, sourceId, sinkType, sinkId, weight = readConnection(connection)
            print(sourceType, sourceId, sinkType, sinkId, weight)
            if sourceType == "sensory":
                value = sensoryList[sourceId].computation(creature) * weight
            elif sourceType == "internal":
                value = creature.internalNeurons[sourceId] * weight

            
            


            if sourceType == "sensory":
                source = sensoryList[sourceId]
                value = source.computation(creature) * weight
            elif sourceType == "internal":
                source = internalList[sourceId]
                inputs = []
                for internalConnections in creature.genes:
                    sourceType, sourceId, sinkType, sinkId, weight = readConnection(internalConnections)
                    if sourceType == "sensory":
                        source2 = sensoryList[sourceId]
                        inputs.append(source2.computation(creature) * weight)
                    elif sourceType == "internal":
                        if sourceId == 1:
                            inputs.append(creature.internal1 * weight)
                        elif sourceId == 2:
                            inputs.append(creature.internal2 * weight)
                        elif sourceId == 3:
                            inputs.append(creature.internal3 * weight)
                        
                value = source.computation(inputs) * weight

            
            if sinkType == "internal": # fix internals
                if sinkId == 1:
                    creature.internal1 = value
                elif sinkId == 2:
                    creature.internal2 = value
                elif sinkId == 3:
                    creature.internal3 = value
            elif sinkType == "action":
                if value > 1:
                    value = 1
                if value > 0:
                    connections.append((value, sinkId))
        action = (0, 0)
        if creature.cId == 0:
            print(connections)
        for i in connections:
            if i[0] > action[0]:
                action = i
        creature.stepAction = actionList[action[1]].computation

    for creature in creatures:
        grid[creature.pos[1]][creature.pos[0]] = 0
        creature.stepAction(creature)
        grid[creature.pos[1]][creature.pos[0]] = creature

    currStep += 1
    updateGrid()

# sensory neurons functions
def randomSensory(*args):
    return random.random()

def ageSensory(*args):
    return currStep / steps

def northDistance(creature):
    return 1 - creature.pos[1] / gridX

def southDistance(creature):
    return creature.pos[1] / gridX

def eastDistance(creature):
    return creature.pos[0] / gridY

def westDistance(creature):
    return 1 - creature.pos[0] / gridY

def hasCoat(creature):
    if creature.coat:
        return 1
    else:
        return 0

# internal neuron functions
def internalCalculation(inputs):
    return math.tanh(sum(inputs))

# action neurons functions
def defaultAction(*args):
    return 0

def moveUp(creature):
    if creature.pos[1] > 0 and not grid[creature.pos[1] - 1][creature.pos[0]]:
        creature.pos[1] -= 1

def moveDown(creature):
    if creature.pos[1] < gridY - 1 and not grid[creature.pos[1] + 1][creature.pos[0]]:
        creature.pos[1] += 1

def moveLeft(creature):
    if creature.pos[0] > 0 and not grid[creature.pos[1]][creature.pos[0] - 1]:
        creature.pos[0] -= 1

def moveRight(creature):
    if creature.pos[0] < gridX - 1 and not grid[creature.pos[1]][creature.pos[0] + 1]:
        creature.pos[0] += 1

def moveRandom(creature):
    direction = random.choice(["up", "down", "left", "right"])
    if direction == "up":
        moveUp(creature)
    elif direction == "down":
        moveDown(creature)
    elif direction == "left":
        moveLeft(creature)
    elif direction == "right":
        moveRight(creature)

def awayFromWall(creature):
    if creature.pos[1] < gridY / 2:
        moveDown(creature)
    else:
        moveUp(creature)
    if creature.pos[0] < gridX / 2:
        moveRight(creature)
    else:
        moveLeft(creature)

def makeCoat(creature):
    creature.coat = True
    creature.color = (0, 0, 255)

global sensoryList, internalList, actionList
# sensory neurons
sensoryList = []
sensoryList.append(Neuron("Random", "Rnd", randomSensory, "sensory", 1))
sensoryList.append(Neuron("Age", "Age", ageSensory, "sensory", 2))
sensoryList.append(Neuron("North", "DiN", northDistance, "sensory", 3))
sensoryList.append(Neuron("South", "DiS", southDistance, "sensory", 4))
sensoryList.append(Neuron("East", "DiE", eastDistance, "sensory", 5))
sensoryList.append(Neuron("West", "DiW", westDistance, "sensory", 6))
sensoryList.append(Neuron("Coat", "Ct", hasCoat, "sensory", 7))

# internal neuron
internalList = []
internalList.append(Neuron("internal1", "N1", internalCalculation, "internal", 1))
internalList.append(Neuron("internal2", "N2", internalCalculation, "internal", 2))
internalList.append(Neuron("internal3", "N3", internalCalculation, "internal", 3))

# action neurons
actionList = []
actionList.append(Neuron("Default", "Def", defaultAction, "action", 0))
actionList.append(Neuron("Up", "MU", moveUp, "action", 1))
actionList.append(Neuron("Down", "MD", moveDown, "action", 2))
actionList.append(Neuron("Left", "ML", moveLeft, "action", 3))
actionList.append(Neuron("Right", "MR", moveRight, "action", 4))
actionList.append(Neuron("Random", "MRn", moveRandom, "action", 5))
actionList.append(Neuron("Coat", "MCo", makeCoat, "action", 6))
actionList.append(Neuron("Away", "AFW", awayFromWall, "action", 7))

global gridX, gridY, numCreatures, numOfConnections, creatures, grid, steps, currStep, genNum, mutation
gridX = 45
gridY = 45
numCreatures = 100
numOfConnections = 3
creatures = []
mutation = 300

if gridX * gridY < numCreatures:
    print("Too many creatures for the grid")
    exit()

grid = []
steps = 300
currStep = 0
genNum = 1

global aliveStartX, aliveStartY, aliveEndX, aliveEndY
aliveStartX = 0
aliveStartY = 0
aliveEndX = 200
aliveEndY = 900

for i in range(gridY):
    column = []
    for j in range(gridX):
        column.append(0)
    grid.append(column)

positions = []
for i in range(numCreatures):
    genes = []
    for j in range(numOfConnections):
        genes.append(generateRandomHex(8))
    pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
    while pos in positions:
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
    creatures.append(Creature(pos, genes, defaultAction, i))

for i in creatures:
    grid[i.pos[1]][i.pos[0]] = i


dpg.create_context()
dpg.create_viewport(title='Custom Title', width=1000, height=700)

with dpg.window(label='Grid', width=1000, height=1000) as gridWin:

    global simArea
    simArea = None
    """
    with dpg.drawlist(width=920, height=920) as simArea:
        dpg.draw_rectangle((10, 10), (910, 910), color=(255, 255, 255))
        dpg.draw_rectangle((aliveStartX+10, aliveStartY+10), (aliveEndX+10, aliveEndY+10), color=(0, 255, 0), fill=(0, 255, 0), parent=simArea)
    """
    generationText = dpg.add_text("Generation: " + str(genNum))
    dpg.add_button(label="Step", callback=step)
    dpg.add_button(label="Play", callback=playGeneration, pos=(50, 50))
    dpg.add_button(label="Next Gen", callback=nextGeneration, pos=(92, 50))
    dpg.add_button(label="50", callback=gen50, pos=(200, 50))
    showIdsCb = dpg.add_checkbox(label="Show ids", default_value=False, pos=(300, 50))
    dpg.add_button(label="Brains", callback=generateBrains, pos=(400, 50))

        



updateGrid()
#displayGrid()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()