"""Showcase of flying arrows that can stick to objects in a somewhat 
realistic looking way.
"""
import sys
from typing import List
from Physics.arm import *
from Physics.utils import *
from Agent.agent import *
import random
from tqdm import tqdm

import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

def createPolygon():
    vs = [(-30, 0), (0, 3), (10, 0), (0, -3)]
    # mass = 1
    # moment = pymunk.moment_for_poly(mass, vs)
    arrow_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)

    arrow_shape = pymunk.Poly(arrow_body, vs)
    arrow_shape.friction = 0.5
    arrow_shape.collision_type = 1
    arrow_shape.density = 0.1
    return arrow_body, arrow_shape


def stick_arrow_to_target(space, arrow_body, target_body, position, flying_arrows):
    pivot_joint = pymunk.PivotJoint(arrow_body, target_body, position)
    phase = target_body.angle - arrow_body.angle
    gear_joint = pymunk.GearJoint(arrow_body, target_body, phase, 1)
    space.add(pivot_joint)
    space.add(gear_joint)
    try:
        flying_arrows.remove(arrow_body)
    except:
        pass


def post_solve_arrow_hit(arbiter, space, data):
    if arbiter.total_impulse.length > 300:
        a, b = arbiter.shapes
        position = arbiter.contact_point_set.points[0].point_a
        #b.collision_type = 0
        #b.group = 1
        b.color = (255, 255, 0, 255)
        other_body = a.body
        arrow_body = b.body

        if a == data["SafeWall"]:
            data["isArrowStopped"] = True
            #print("Hit a safe wall. Score the agent")
        
        if a == data["TargetWall"]:
            data["isArrowStopped"] = True
            #print("Hit a target wall. Punish the aagent")

        if a in data["OtherWalls"]:
            data["isArrowStopped"] = True
            #print("Hit a unnecessary wall. No points")

        if a in data["ArmShapes"]:
            data["isArrowStopped"] = True
            #print("Hit an arm section. Give some score.")
            data["score"] += 1.0

        if a == data["Cannon"]:
            data["isArrowStopped"] = True
            #print("Perfect strike. Give a huge reward.")

        #data["flying_arrows"].remove(arrow_body)
        ## Have a switch on the other bodies.
        ## Give score based on if the robot was able to deflect the arraow.
        ## High score to hit the red ball and stuff

        # space.add_post_step_callback(
        #     stick_arrow_to_target,
        #     arrow_body,
        #     other_body,
        #     position,
        #     data["flying_arrows"],
        # )
def dataForAgent(polygon):
    return [
        polygon.position[0],
        polygon.position[1],
        polygon.angle,
        polygon.angular_velocity 
    ]


offset = 150
def getRandomPositionForCannon():
    line = random.random()
    if line < 0.25:
        return offset + random.random()*(WIDTH-offset),offset, WALLBOTTOM
    elif line < 0.5:
        return (WIDTH-offset), offset + random.random()*(HEIGHT-offset), WALLLEFT
    elif line < 0.75:
        return offset + random.random()*(WIDTH-offset), (HEIGHT-offset), WALLTOP
    else: 
        return offset, offset + random.random()*(HEIGHT-offset), WALLRIGHT

## If display is true the game will be displayed
## If the agent is true we use the given agent to play the game, else the game will without any inputs
## If path is not none we will load the weights from the disk.
def play(display=True, agent=None, path=None, scoreFrameFunc=lambda:0, scoreFullGameFunc= lambda:0):
    maxFrames = 60*120

    if agent != None and path != None:
        agent.loaad(path)

    ### PyGame init
    if display:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 16)
    running = True
    

    ### Init the space
    space = pymunk.Space()
    space.gravity = 0, 500
    if display:
        draw_options = pymunk.pygame_util.DrawOptions(screen)

    ### Init the arms
    arm1 = Arm(space, (WIDTH/2, HEIGHT/2))
    arm1.addJoint(150)
    arm1.addJoint(100)
    arm1.addJoint(50, end=True)

    ### Init the box.
    ### Left, Top, Right, Bottom
    static: List[pymunk.Shape] = [
        pymunk.Segment(space.static_body, (50, HEIGHT-50), (50, 50), 5),
        pymunk.Segment(space.static_body, (50, 50), (WIDTH-50, 50), 5),
        pymunk.Segment(space.static_body, (WIDTH-50, 50), (WIDTH-50, HEIGHT-50), 5),
        pymunk.Segment(space.static_body, (50, HEIGHT-50), (WIDTH-50, HEIGHT - 50), 5),
    ]

    # "Cannon" that can fire arrows
    cannon_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    cannon_shape = pymunk.Circle(cannon_body, 25)
    #cannon_shape.sensor = True
    cannon_shape.color = (255, 50, 50, 255)
    cannon_body.position = 100, 500
    space.add(cannon_body, cannon_shape)

    ## Set the cannon position to a random position on the perimeter of the area.
    originalCannonPos = getRandomPositionForCannon()
    cannon_body.position = originalCannonPos[:-1]

    ## Set the target wall. This is based on the posiition of the cannon.
    ## The target wall is the wall that the polygons will try to hit
    targetWall = originalCannonPos[-1]
    static[wallKeyToIdx(targetWall)].color = (255, 0, 0, 255)

    ## Set the safe wall.
    ## This is the wall that the agent will try and deflect the arms to.
    safeWall = oppositeWall(targetWall)
    static[wallKeyToIdx(safeWall)].color = (255, 0, 255, 255)

    ## Set the other two walls.
    otherWalls = static.copy()
    otherWalls.remove(static[wallKeyToIdx(safeWall)])
    otherWalls.remove(static[wallKeyToIdx(targetWall)])

    ## Add the walls to the space
    for s in static:
        s.friction = 1.0
        s.group = 1
    space.add(*static)

    ## The polygon that will be firied.
    arrow_body, arrow_shape = createPolygon()
    space.add(arrow_body, arrow_shape)

    ## Active lisit of flying polygons.
    flying_arrows: List[pymunk.Body] = []

    ## The handler will be responsible for collisions and scoring the agent.
    handler = space.add_collision_handler(0, 1)

    ## Set the cannon and the bullets.
    handler.data["flying_arrows"] = flying_arrows
    handler.data["cannon"] = cannon_body

    ## Set the wall discription
    handler.data["TargetWall"] = static[wallKeyToIdx(targetWall)]
    handler.data["SafeWall"] = static[wallKeyToIdx(safeWall)]
    handler.data["OtherWalls"] = otherWalls

    ## Add the arm shape to the handler's data.
    handler.data["ArmShapes"] = [x["Shape"] for x in arm1.Objects]
    handler.data["Cannon"] = cannon_shape
    ## Init the score as 0 for all agents
    handler.data["score"] = 0.0

    handler.data["isArrowStopped"] = True

    handler.post_solve = post_solve_arrow_hit

    frameNumber = 0
    activePolygon = None
    start_time = 0
    while running:
        if frameNumber > maxFrames:
            running = False
        if handler.data["isArrowStopped"]:
            activePolygon = None
        if display:
            for event in pygame.event.get():
                if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
                ):
                    running = False
        if frameNumber%100 == 0:

            ## Choose a random angle. But make sure it is aimed at the target wall.
            cannon_body.angle = random.random()*2*PI
            # move the unfired arrow together with the cannon
            arrow_body.position = cannon_body.position + Vec2d(
                cannon_shape.radius + 40, 0
            ).rotated(cannon_body.angle)
            arrow_body.angle = cannon_body.angle

            ## Give a random ammout on impulse.
            power = 7500 + random.random()*10000
            impulse = power * Vec2d(1, 0)
            impulse = impulse.rotated(arrow_body.angle)
            arrow_body.body_type = pymunk.Body.DYNAMIC
            arrow_body.apply_impulse_at_world_point(impulse, arrow_body.position)

            # space.add(arrow_body)
            flying_arrows.append(arrow_body)
            handler.data["flying_arrows"] = flying_arrows
            activePolygon = arrow_body
            arrow_body, arrow_shape = createPolygon()
            space.add(arrow_body, arrow_shape)

            ## Indicates a polygon is still in flight.
            handler.data["isArrowStopped"] = False

        if activePolygon != None:
            inputVector = []
            inputVector += dataForAgent(activePolygon)
            armdData = arm1.physicsToAgent()
            for key in armdData:
                inputVector += armdData[key]
            inputVector = np.array(inputVector)
            if agent != None:
                rawOut = agent.forwardPass(inputVector)
                rawOut = rawOut[:-1]
                arm1.agentToPhysics(rawOut, maxSpeed=1.2)


        for flying_arrow in flying_arrows:
            drag_constant = 0.0002

            pointing_direction = Vec2d(1, 0).rotated(flying_arrow.angle)
            # print(pointing_direction.angle, flying_arrow.angle)
            flight_direction = Vec2d(*flying_arrow.velocity)
            flight_direction, flight_speed = flight_direction.normalized_and_length()

            dot = flight_direction.dot(pointing_direction)
            # (1-abs(dot)) can be replaced with (1-dot) to make arrows turn
            # around even when fired straight up. Might not be as accurate, but
            # maybe look better.
            drag_force_magnitude = (
                (1 - abs(dot)) * flight_speed ** 2 * drag_constant * flying_arrow.mass
            )
            arrow_tail_position = flying_arrow.position + Vec2d(-50, 0).rotated(
                flying_arrow.angle
            )
            flying_arrow.apply_impulse_at_world_point(
                drag_force_magnitude * -flight_direction, arrow_tail_position
            )

            flying_arrow.angular_velocity *= 0.5

        if display:
            screen.fill(pygame.Color("black"))
            space.debug_draw(draw_options)
            pygame.display.flip()

        ### Update physics
        fps = 60
        dt = 1.0 / fps
        space.step(dt)

        if display:
            clock.tick(fps)
        frameNumber += 1
    return handler.data["score"]


PopulationCount = 10
ChildrenCount = 6
ParentsCount = PopulationCount-ChildrenCount


def playGivenAgent(path):
    lAgent = Agent()
    lAgent.addLayer("Input", 22, None, False)
    lAgent.addLayer("H0", 512, Linear, False)
    lAgent.addLayer("H1", 256, Sigmoid, False)
    lAgent.addLayer("H2", 128, TanH, False)
    lAgent.addLayer("H3", 64, Sigmoid, False)
    lAgent.addLayer("Output", 4, None, True)
    
    lAgent.load(path)
    play(display=True, agent=lAgent)

#playGivenAgent("./TEST_24")

from matplotlib import pyplot as plt
if __name__ == "__main__":
    Agents = []
    avgScores = []
    for _ in range(PopulationCount):
        lAgent = Agent()
        lAgent.addLayer("Input", 22, None, False)
        lAgent.addLayer("H0", 512, Linear, False)
        lAgent.addLayer("H1", 256, Sigmoid, False)
        lAgent.addLayer("H2", 128, TanH, False)
        lAgent.addLayer("H3", 64, Sigmoid, False)
        lAgent.addLayer("Output", 4, None, True)
        Agents.append([lAgent, 0.0])

    generation = 0
    while True:
        for idx in tqdm(range(PopulationCount)):
            Agents[idx][1] = play(display=False, agent=Agents[idx][0])

        Agents.sort(key= lambda x: x[1])

        if (generation+1)%25 ==0:
            Agents[-1][0].save("Test_" + str(generation))

        avgScore = sum(list(map(lambda x: x[1], Agents)))/len(Agents)
        avgScores.append(avgScore)
        print("Scores: ", list(map(lambda x: x[1], Agents)),
              "Average score:", avgScore   
            )

        Parents = Agents[-ParentsCount:]
        Children = []

        for idx in range(ChildrenCount):
            lParents = random.sample(Parents, 2)
            lNewChild = crossover(*list(map(lambda x: x[0], lParents)))
            lNewChild.mutate()
            Children.append([lNewChild, 0.0])

        Agents = []
        Agents = Parents + Children
        generation += 1

        if generation%10 == 0:
            plt.plot(avgScores)
            plt.show()