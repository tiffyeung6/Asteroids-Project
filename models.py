"""
Models module for Planetoids

This module contains the model classes for the Planetoids game. Anything that you
interact with on the screen is model: the ship, the bullets, and the planetoids.

We need models for these objects because they contain information beyond the simple
shapes like GImage and GEllipse. In particular, ALL of these classes need a velocity
representing their movement direction and speed (and hence they all need an additional
attribute representing this fact). But for the most part, that is all they need. You
will only need more complex models if you are adding advanced features like scoring.

You are free to add even more models to this module. You may wish to do this when you
add new features to your game, such as power-ups. If you are unsure about whether to
make a new class or not, please ask on Ed Discussions.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from consts import *
from game2d import *
from introcs import *
import math

# PRIMARY RULE: Models are not allowed to access anything in any module other than
# consts.py. If you need extra information from Gameplay, then it should be a 
# parameter in your method, and Wave should pass it as a argument when it calls 
# the method.

# START REMOVE
# HELPER FUNCTION FOR MATH CONVERSION
def degToRad(deg):
    """
    Returns the radian value for the given number of degrees
    
    Parameter deg: The degrees to convert
    Precondition: deg is a float
    """
    return math.pi*deg/180
# END REMOVE

def wrap(self): 
    """
    animates the wrapping movement of the ship and asteroids on screen
    """
    if self.x < -DEAD_ZONE:
        self.x += GAME_WIDTH+2*DEAD_ZONE
    elif self.x > GAME_WIDTH+DEAD_ZONE:
        self.x -= GAME_WIDTH+2*DEAD_ZONE

    if self.y < -DEAD_ZONE:
        self.y += GAME_HEIGHT+2*DEAD_ZONE
    elif self.y > GAME_HEIGHT+DEAD_ZONE:
        self.y -= GAME_HEIGHT+2*DEAD_ZONE

class Bullet(GEllipse):
    """
    A class representing a bullet from the ship
    
    Bullets are typically just white circles (ellipses). The size of the bullet is 
    determined by constants in consts.py. However, we MUST subclass GEllipse, because 
    we need to add an extra attribute for the velocity of the bullet.
    
    The class Wave will need to look at this velocity, so you will need getters for
    the velocity components. However, it is possible to write this assignment with no 
    setters for the velocities. That is because the velocity is fixed and cannot change 
    once the bolt is fired.
    
    In addition to the getters, you need to write the __init__ method to set the starting
    velocity. This __init__ method will need to call the __init__ from GEllipse as a
    helper. This init will need a parameter to set the direction of the velocity.
    
    You also want to create a method to update the bolt. You update the bolt by adding
    the velocity to the position. While it is okay to add a method to detect collisions
    in this class, you may find it easier to process collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    # INITIALIZER TO SET THE POSITION AND VELOCITY
    def __init__(self, x, y, velocity):
        super().__init__(x=x, y=y, width=BULLET_RADIUS*2, 
                         height=BULLET_RADIUS*2, fillcolor=BULLET_COLOR)
        self._velocity = velocity

    def getVelocity(self):
        return self._velocity
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)


class Ship(GImage):
    """
    A class to represent the game ship.
    
    This ship is represented by an image. The size of the ship is determined by constants 
    in consts.py. However, we MUST subclass GEllipse, because we need to add an extra 
    attribute for the velocity of the ship, as well as the facing vecotr (not the same)
    thing.
    
    The class Wave will need to access these two values, so you will need getters for 
    them. But per the instructions,these values are changed indirectly by applying thrust 
    or turning the ship. That means you won't want setters for these attributes, but you 
    will want methods to apply thrust or turn the ship.
    
    This class needs an __init__ method to set the position and initial facing angle.
    This information is provided by the wave JSON file. Ships should start with a shield
    enabled.
    
    Finally, you want a method to update the ship. When you update the ship, you apply
    the velocity to the position. While it is okay to add a method to detect collisions 
    in this class, you may find it easier to process collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # _velocity: tells us the magnitude and direction of the ship
    # _velocity invariant: must be a Vector2 object 
    
    # _facing: tells us the direction in which the ship is facing
    # _facing invariant: must be a Vector2 object 
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getVelocity(self):
        """
        returns the velocity of the ship through hidden attribute _velocity
        """
        return self._velocity
    
    def getFacing(self): 
        """
        returns the facing vector of the ship through hidden attribute 
        _facing
        """
        return self._facing
    
    # INITIALIZER TO CREATE A NEW SHIP
    def __init__(self, x, y, width, height, source, angle): 
        """
        initizlizes a new ship object with its attributes 
        """
        super().__init__(x=x, y=y, width=width, height=height, source=source, 
                         angle=angle)
        self._velocity = introcs.Vector2(x=0, y=0)
        anglerad = degToRad(self.angle)
        self._facing = introcs.Vector2(x=math.cos(anglerad), 
                                       y=math.sin(anglerad))
        
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)        
    def turn(self, da): 
        """
        animates the turning motion of the ship
        
        Parameter da: change in angle, in degrees
        da must be an int
        """
        self._facing.rotate(degToRad(da))
        self.angle += da
    
    def impulse(self):
        """
        calculates the impulse of the ship, and the resulting change in 
        velocity
        """
        self._velocity = self._velocity + (self._facing * SHIP_IMPULSE)
        
        if self._velocity.length() > SHIP_MAX_SPEED: 
            self._velocity = self._velocity.normalize()
            self._velocity *= SHIP_MAX_SPEED
            
    def move(self):
        """
        animates the movement of the ship i.e. the change in position
        """
        self.x += self._velocity.x
        self.y += self._velocity.y
        wrap(self)
        
    def placebullet(self):
        """
        calculates and returns the position of the bullet
        """
        bulletpos = self._facing * SHIP_RADIUS + Vector2(self.x, self.y)
        return bulletpos
        
    def bullvelocity(self):
        """
        calculates and returns the bullet velocity
        """
        bulletvelocity = self._facing * BULLET_SPEED
        return bulletvelocity
        
    
class Asteroid(GImage):
    """
    A class to represent a single asteroid.
    
    Asteroids are typically are represented by images. Asteroids come in three 
    different sizes (SMALL_ASTEROID, MEDIUM_ASTEROID, and LARGE_ASTEROID) that 
    determine the choice of image and asteroid radius. We MUST subclass GImage, because 
    we need extra attributes for both the size and the velocity of the asteroid.
    
    The class Wave will need to look at the size and velocity, so you will need getters 
    for them.  However, it is possible to write this assignment with no setters for 
    either of these. That is because they are fixed and cannot change when the planetoid 
    is created. 
    
    In addition to the getters, you need to write the __init__ method to set the size
    and starting velocity. Note that the SPEED of an asteroid is defined in const.py,
    so the only thing that differs is the velocity direction.
    
    You also want to create a method to update the asteroid. You update the asteroid 
    by adding the velocity to the position. While it is okay to add a method to detect 
    collisions in this class, you may find it easier to process collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getSize(self):
        """
        returns the size of the asteroid from hidden attribute _size
        """
        return self._size
    
    def getVelocity(self):
        """
        returns the velocity of the asteroid from hidden attribute _velocity
        """
        return self._velocity
    
    def getRadius(self):
        """
        returns the radius of the asteroid from hidden attribute _radius
        """
        return self._radius
    
    # INITIALIZER TO CREATE A NEW ASTEROID
    def __init__(self, x, y, width, height, source, speed, xdir, ydir, size):
        """
        initinalizes a new asteroid object and its attributes 
 
        """
        super().__init__(x=x,y=y,width=width,height=height,source=source)
        self._size = size
        self._radius = width/2
        direction = introcs.Vector2(xdir, ydir)
        if xdir == 0 and ydir == 0:
            self._velocity = 0
        else:
            direction.normalize()
            self._velocity = direction * speed

    def move(self):
        """
        animates the movement of the asteroid by changing its position  
        """
        self.x += self._velocity.x
        self.y += self._velocity.y 
        wrap(self)
            
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)


# IF YOU NEED ADDITIONAL MODEL CLASSES, THEY GO HERE
