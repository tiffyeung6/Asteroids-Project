"""
Subcontroller module for Planetoids

This module contains the subcontroller to manage a single level (or wave) in the 
Planetoids game.  Instances of Wave represent a single level, and should correspond
to a JSON file in the Data directory. Whenever you move to a new level, you are 
expected to make a new instance of the class.

The subcontroller Wave manages the ship, the asteroids, and any bullets on screen. These 
are model objects. Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Ed Discussions and we will answer.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from game2d import *
from consts import *
from models import *
import random
import datetime

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Level is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)

class Wave(object):
    """
    This class controls a single level or wave of Planetoids.
    
    This subcontroller has a reference to the ship, asteroids, and any bullets on screen.
    It animates all of these by adding the velocity to the position at each step. It
    checks for collisions between bullets and asteroids or asteroids and the ship 
    (asteroids can safely pass through each other). A bullet collision either breaks
    up or removes a asteroid. A ship collision kills the player. 
    
    The player wins once all asteroids are destroyed.  The player loses if they run out
    of lives. When the wave is complete, you should create a NEW instance of Wave 
    (in Planetoids) if you want to make a new wave of asteroids.
    
    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 25 for an example.  This class will be similar to
    than one in many ways.
    
    All attributes of this class are to be hidden. No attribute should be accessed 
    without going through a getter/setter first. However, just because you have an
    attribute does not mean that you have to have a getter for it. For example, the
    Planetoids app probably never needs to access the attribute for the bullets, so 
    there is no need for a getter there. But at a minimum, you need getters indicating
    whether you one or lost the game.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # THE ATTRIBUTES LISTED ARE SUGGESTIONS ONLY AND CAN BE CHANGED AS YOU SEE FIT
    # Attribute _data: The data from the wave JSON, for reloading 
    # Invariant: _data is a dict loaded from a JSON file
    #
    # Attribute _ship: The player ship to control 
    # Invariant: _ship is a Ship object
    #
    # Attribute _asteroids: the asteroids on screen 
    # Invariant: _asteroids is a list of Asteroid, possibly empty
    #
    # Attribute _bullets: the bullets currently on screen 
    # Invariant: _bullets is a list of Bullet, possibly empty
    #
    # Attribute _lives: the number of lives left 
    # Invariant: _lives is an int >= 0
    #
    # Attribute _firerate: the number of frames until the player can fire again 
    # Invariant: _firerate is an int >= 0
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLives(self):
        """
        returns the hidden attribute _lives
        """
        return self._lives

    def setLives(self, lives): 
        """
        sets the hidden attribute _lives
        """
        assert lives >= 0
        self._lives = lives
    
    def getShip(self):
        """
        returns the hidden attribute _ship
        """
        return self._ship
    
    def getAsteroids(self): 
        """
        returns the hidden attribute _asteroids 
        """
        return self._asteroids
    
    
    # INITIALIZER (standard form) TO CREATE SHIP AND ASTEROIDS
    def __init__(self,jsonfile): 
        """
        initializes the attributes in the Wave class, creates the ship, 
        asteroids, and bullets. 
        
        Parameter jsonfile: the source data needed to create the ship,
        asteroid and bullet objects 
        jsonfile must be a json file
        """
        self._data = jsonfile
        pos = self._data['ship']['position']
        xpos = pos[0]
        ypos = pos[1]
        ang = self._data['ship']['angle']
        self._ship = Ship(x=xpos,y=ypos,width=SHIP_RADIUS*2,
                height=SHIP_RADIUS*2,source=SHIP_IMAGE,angle=ang)
        
        self._asteroids = []   
        for i in range(len(self._data['asteroids'])):
            pos = self._data['asteroids'][i]['position']
            xpos = pos[0]
            ypos = pos[1]
            dir = self._data['asteroids'][i]['direction']
            xdir = dir[0]
            ydir = dir[1]
            size = self._data['asteroids'][i]['size'] 
            if self._data['asteroids'][i]['size'] == SMALL_ASTEROID:
                asteroid = Asteroid(x=xpos,y=ypos,width=SMALL_RADIUS*2,
                    height=SMALL_RADIUS*2,source=SMALL_IMAGE,speed=SMALL_SPEED,
                    xdir=xdir,ydir=ydir,size=size)
                self._asteroids.append(asteroid)
            elif self._data['asteroids'][i]['size'] == MEDIUM_ASTEROID:
                asteroid = Asteroid(x=xpos,y=ypos,width=MEDIUM_RADIUS*2,
                    height=MEDIUM_RADIUS*2,source=MEDIUM_IMAGE,
                    speed=MEDIUM_SPEED,xdir=xdir,ydir=ydir,size=size)
                self._asteroids.append(asteroid)
            elif self._data['asteroids'][i]['size'] == LARGE_ASTEROID:
                asteroid = Asteroid(x=xpos,y=ypos,width=LARGE_RADIUS*2,
                    height=LARGE_RADIUS*2,source=LARGE_IMAGE,
                    speed=LARGE_SPEED,xdir=xdir,ydir=ydir,size=size)
                self._asteroids.append(asteroid)
            
        self._bullets = []
        self._fire = 0
        
        self._lives = 3
        
    # UPDATE METHOD TO MOVE THE SHIP, ASTEROIDS, AND BULLETS
    def update(self, dt, input): 
        """
        Updates the position of the ship, asteroids and bullets to create an 
        animation effect 
        
        Parameter dt: keeps track of the time between frames 
        dt is an int or float 
        
        Parameter input: keeps track of data about user keyboard/mouse input 
        input must be a GInput object 
        
        """
        self.leftright(input)
        self.up(input)
        
        self.animateastroids(input)
        self.createbullet(input)
        self.animatebullet(input)
            
        i = 0
        ast = []
        while i < len(self._asteroids):
            b=0
            while b < len(self._bullets):
                dist = math.sqrt(((self._asteroids[i].x - self._bullets[b].x)**2) 
                            + (self._asteroids[i].y - self._bullets[b].y)**2)
                if dist < BULLET_RADIUS + self._asteroids[i].getRadius():
                    if self._asteroids[i].getSize() == LARGE_ASTEROID:
                        self.largecollide(i, b, ast)
                    if self._asteroids[i].getSize() == MEDIUM_ASTEROID:
                        self.medcollide(i, b, ast)
                    del self._bullets[b]
                    del self._asteroids[i]
                    break
                else:
                    b += 1
            i+=1
        self._asteroids+=ast
                        
    # DRAW METHOD TO DRAW THE SHIP, ASTEROIDS, AND BULLETS
    def draw(self,view): 
        """
        Draws the ship, asteroids and bullets 
        
        Parameter view: passes information to the draw method
        view is a GView object 
            

        """
        self._ship.draw(view)
        for x in range(len(self._asteroids)): 
            self._asteroids[x].draw(view)
        for x in range(len(self._bullets)):
            self._bullets[x].draw(view)
        
    # RESET METHOD FOR CREATING A NEW LIFE
    def nextlife(self): 
        """
        Creates the next life after the intermediate pause screen when the
        player still has remaining lives 
        """
        pos = self._data['ship']['position']
        xpos = pos[0]
        ypos = pos[1]
        ang = self._data['ship']['angle']
        self._ship = Ship(x=xpos,y=ypos,width=SHIP_RADIUS*2,
                          height=SHIP_RADIUS*2,source=SHIP_IMAGE,angle=ang)
        
        self.bullets = []
            
    # HELPER METHODS FOR PHYSICS AND COLLISION DETECTION
    def leftright(self, input): 
        """
        Detects user input on the left/right arrows and turns the ship 
        accordingly 
        
        Parameter input: user keyboard/mouse input
        input must be a GInput object
        """
        da = 0
        if input.is_key_down('left') == True: 
            da += SHIP_TURN_RATE
        if input.is_key_down('right') == True: 
            da -= SHIP_TURN_RATE
        self._ship.turn(da)
    
    def up(self, input): 
        """
        Detects pressing of the up arrow and moves the ship accordingly 
        
        Parameter input: user keyboard/mouse input
        input must be a GInput object
        """
        if input.is_key_down('up') == True: 
            self._ship.impulse()
            self._ship.move()

    def animateastroids(self, input): 
        """
        Animates asteroid movement 
        
        Parameter input: user keyboard/mouse input
        input must be a GInput object
        """
        for x in range(len(self._asteroids)): 
            self._asteroids[x].move()
            
    def createbullet(self, input):
        """
        Creates a bullet
        
        Parameter input: user keyboard/mouse input
        input must be a GInput object
        """
        self._fire+=1
        if input.is_key_down('spacebar') and self._fire >= BULLET_RATE:
            self._fire = 0
            velocity = self._ship.bullvelocity()
            position = self._ship.placebullet()
            bullet = Bullet(position.x, position.y, velocity)
            self._bullets.append(bullet)
            
    def animatebullet(self, input):
        """
        Animates bullet movement 
        
        Parameter input: user keyboard/mouse input
        input must be a GInput object
        """
        i = 0
        while i < len(self._bullets):
            self._bullets[i].x += self._bullets[i].getVelocity().x
            self._bullets[i].y += self._bullets[i].getVelocity().y
            if self._bullets[i].y < -DEAD_ZONE or +\
                    self._bullets[i].y > GAME_HEIGHT+DEAD_ZONE or +\
                    self._bullets[i].x < -DEAD_ZONE or +\
                    self._bullets[i].x > GAME_WIDTH+DEAD_ZONE:
                del self._bullets[i]
            else:
                i += 1
        for i in range(len(self._asteroids)):
            distance = math.sqrt(((self._ship.x - self._asteroids[i].x)**2) + 
                                 (self._ship.y - self._asteroids[i].y)**2)
            if distance < SHIP_RADIUS + self._asteroids[i].getRadius():
                self._ship = None
                return
            
    def largecollide(self, i, b, ast): 
        """
        Animates collision between a large sized asteroid and a bullet 
        (asteroid split) 
        """
        angle = (2*math.pi)/3
        v1 = self._bullets[b].getVelocity().normal()
        v2 = Vector2(v1.x * math.cos(angle)-v1.y*math.sin(angle), 
                     v1.x*math.sin(angle)+v1.y+math.cos(angle))
        v3 = Vector2(v2.x * math.cos(angle)-v2.y*math.sin(angle), 
                     v2.x*math.sin(angle)+v2.y+math.cos(angle))
        center = Vector2(self._asteroids[i].x, self._asteroids[i].y)
        newcenter = MEDIUM_RADIUS * v1 + center
        xdir = v1.x * MEDIUM_SPEED
        ydir = v1.y * MEDIUM_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,
                    width=MEDIUM_RADIUS*2,height=MEDIUM_RADIUS*2,
                    source=MEDIUM_IMAGE,speed=MEDIUM_SPEED,xdir=xdir,ydir=ydir,
                    size=MEDIUM_ASTEROID)
        ast.append(asteroid)
        newcenter = MEDIUM_RADIUS * v2 + center
        xdir = v2.x * MEDIUM_SPEED
        ydir = v2.y * MEDIUM_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,
                    width=MEDIUM_RADIUS*2,height=MEDIUM_RADIUS*2,
                    source=MEDIUM_IMAGE,speed=MEDIUM_SPEED,xdir=xdir,
                    ydir=ydir,size=MEDIUM_ASTEROID)
        ast.append(asteroid)
        newcenter = MEDIUM_RADIUS * v3 + center
        xdir = v3.x * MEDIUM_SPEED
        ydir = v3.y * MEDIUM_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,width=MEDIUM_RADIUS*2,
                    height=MEDIUM_RADIUS*2,source=MEDIUM_IMAGE,
                    speed=MEDIUM_SPEED,xdir=xdir,ydir=ydir,
                    size=MEDIUM_ASTEROID)
        ast.append(asteroid)
        
    def medcollide(self, i, b, ast): 
        """
        Animates collision between a medium sized asteroid and a bullet 
        (asteroid split) 
        """
        angle = (2*math.pi)/3
        v1 = self._bullets[b].getVelocity().normal()
        v2 = Vector2(v1.x * math.cos(angle)-v1.y*math.sin(angle), 
                     v1.x*math.sin(angle)+v1.y+math.cos(angle))
        v3 = Vector2(v2.x * math.cos(angle)-v2.y*math.sin(angle), 
                     v2.x*math.sin(angle)+v2.y+math.cos(angle))
        center = Vector2(self._asteroids[i].x, self._asteroids[i].y)
        newcenter = SMALL_RADIUS * v1 + center
        xdir = v1.x * SMALL_SPEED
        ydir = v1.y * SMALL_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,width=SMALL_RADIUS*2,
                            height=SMALL_RADIUS*2,source=SMALL_IMAGE,
                            speed=SMALL_SPEED,xdir=xdir,ydir=ydir,
                            size=SMALL_ASTEROID)
        ast.append(asteroid)
        newcenter = SMALL_RADIUS * v2 + center
        xdir = v2.x * SMALL_SPEED
        ydir = v2.y * SMALL_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,width=SMALL_RADIUS*2,
                            height=SMALL_RADIUS*2,source=SMALL_IMAGE,
                            speed=SMALL_SPEED,xdir=xdir,ydir=ydir,
                            size=SMALL_ASTEROID)
        ast.append(asteroid)
        newcenter = SMALL_RADIUS * v3 + center
        xdir = v3.x * SMALL_SPEED
        ydir = v3.y * SMALL_SPEED
        asteroid = Asteroid(x=newcenter.x,y=newcenter.y,
                            width=SMALL_RADIUS*2,height=SMALL_RADIUS*2,
                            source=SMALL_IMAGE,speed=SMALL_SPEED,xdir=xdir,
                            ydir=ydir,size=SMALL_ASTEROID)
        ast.append(asteroid)
        
        