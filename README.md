# SHAPER
FAI Project

## Abstract
In this project, we wish to simulate a set of robot arms that manipulate random polygons in a 2D space to reorient them to meet the goal orientation. The agents will be given the shape and the current orientation of the polygon and a random goal orientation. The agents will be expected to learn to work together to manipulate the polygon such that it lands in the goal state. These agents will learn to work together, overcoming external forces like gravity that act on the polygon. The agents will have control over the joint angles of the robot arms and the end effector, which can grasp and support the polygon. Their input will include the positions of other agents, the current polygon orientation, and the influence of external forces. Our goal is to track the agents' movements and the polygon's orientation while rewarding them for minimizing the difference between the current and goal orientations. This iterative process will continue until the agents can successfully manipulate any arbitrary polygon to the desired orientation. We will explore multiple possibilities to find the most effective solution to optimize the loss function. While our project will mainly be focused on 2D objects, our future scope involves expanding the project to 3D objects and introducing challenges such as jitter and backlash to further test the agents' capabilities.

## Team members
* Ashwin R Bharadwaj
* Aditya Ratan
* Andrea Pinto 
* Hasnain