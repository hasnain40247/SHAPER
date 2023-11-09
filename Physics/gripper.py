from Physics.utils import *
from Physics.ball import *

class Gripper(Ball):
    def __init__(self, space, postion):
        super().__init__(space, postion)
        
    def rough(self):
        self.shape.friction = 1

    def smooth(self):
        self.shape.friction = 0.25
    
    def draw(self, display):
        super().draw(display, (0, 255, 0))

    def grab(self):
        ## Check if the gripper is touching the polygon
        ## If it is add the pivot joint to between them and return them
        ## We incorporate it with PyMunk and it should work
        pass


