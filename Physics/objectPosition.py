
def hitEdge(width, height, posX, posY, objPixel):
    if posX + objPixel >= width or posX <= 0: 
        ball_XChange *= -1
    if posY + objPixel >= height or posY <= 0: 
        ball_YChange *= -1
    return posX, posY