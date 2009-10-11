import pygame
import MW_global
import MW_animator
import MW_xml
import math
import xml.dom.minidom
from MW_datatypes import *
from MW_constants import *
class Entity:
    def __init__(self):
        self.destroy = False
    def update(self):
        pass
    def draw(self):
        pass

class WallEn(Entity):
    def __init__(self,pos=Vector2d(0,0)):
        Entity.__init__(self)
        self.pos = pos
        self.image = pygame.image.load("basic_wall.png")
        self.highlight = False
    def teleport(self,pos):
        self.pos = pos
    def getRect(self):
        return pygame.Rect(self.pos.x,self.pos.y,TILING_SIZE.x,TILING_SIZE.y)
    def setType(self,l,r,t,b):
        sum = 0
        if l: sum += 1
        if r: sum += 1
        if t: sum += 1
        if b: sum += 1
        rotate = 0
        if sum == 4:
            self.image = pygame.image.load("wall_lrtb.png")
        elif sum == 3:
            self.image = pygame.image.load("wall_lrt.png")
            self.image = pygame.transform.rotate(self.image,rotate)
                
        pass
    
    def draw(self):
        MW_global.camera.drawOnScreen(self.image, self.pos)
        #check if covered by light
            #draw
        if self.highlight:
            dPos = MW_global.camera.convertCrds(self.pos)
            pygame.draw.rect(MW_global.screen,COLOR_WHITE,pygame.Rect(dPos.x,dPos.y,TILING_SIZE.x,TILING_SIZE.y),1)
        self.highlight = False
class PlayerEn(Entity):
    def __init__(self,controller):
        Entity.__init__(self)
        self.setupKeyMap()
        self.pos = Vector2d(0,0)
        self.hitOld = self.getRect()
        self.p = controller
        self.state = "STAND"
    
    def teleport(self,pos):
        self.pos = pos
        
    def setupKeyMap(self):
        self.keyMap = dict()
        keyList = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_x, pygame.K_z]
        for e in keyList:
            self.keyMap[e] = False
        
    def input(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.keyMap[e.key] = True
            elif e.type == pygame.KEYUP:
                self.keyMap[e.key] = False
    
    def getRect(self):
        return pygame.Rect(0,0,0,0)
    
    def checkProjected(self,projection):
        r = self.getRect().inflate(40,40)
        r.x += projection.x
        r.y += projection.y
        rect = self.p.cont.getMatrixRect(r)#arbitrary, can be more precise
        wallRects = self.p.cont.getWallRects(rect)
        selfRect = self.getRect()
        selfRect.x += projection.x
        selfRect.y += projection.y
        hits = selfRect.collidelistall(wallRects)
        if len(hits) > 0:
            return True
        else: return False
        
    def checkHitsIthoughtIGotIt(self):
        rect = pygame.Rect(0,0,50,50) #arbitrary, can be more precise
        wallRects = self.p.cont.getWallRects(rect)
        hits = self.getRect().collidelistall(wallRects)
        for i in hits:
            self.p.cont.wList[self.p.cont.getMatrixIndex(wallRects[i])].highlight = True
        #this could possible result in an infinite loop, just a warning.
        while len(hits) > 0 and not self.pos.__eq__(self.hitOld):
            pass
            #we parse the first rect, not that it's special or anything
            intersect = wallRects[hits[0]].clip(self.getRect())
            wrect = wallRects[hits[0]]
            rdiff = getRectDiff(self.hitOld,wrect)
            if math.fabs(rdiff.x) >  math.fabs(rdiff.y):    #we prioritize y direction
                pass
            
            
    def checkHits(self):
        rect = self.p.cont.getMatrixRect(self.getRect().inflate(40,40))  #arbitrary, can be more precise
        wallRects = self.p.cont.getWallRects(rect)
        hits = self.getRect().collidelistall(wallRects)
        for i in hits:
            self.p.cont.wList[self.p.cont.getMatrixIndex(wallRects[i])].highlight = True
        flag = False
        while len(hits) > 0:
            flag = True
            if (self.pos-self.hitOld).magnitude() > 0:
                if math.fabs((self.pos.y-self.hitOld.y)) >= math.fabs((self.pos.x-self.hitOld.x)):
                    self.pos.y -= (self.pos.y-self.hitOld.y)/math.fabs((self.pos.y-self.hitOld.y))
                else:
                    self.pos.x -= (self.pos.x-self.hitOld.x)/math.fabs((self.pos.x-self.hitOld.x))
            #TODO make sure to check only on ground hits
            hits = self.getRect().collidelistall(wallRects)
        #BAD should move to woman class
        if flag == True:
            if self.state == "JUMP" or self.state == "FALLING":
                if self.checkProjected(Vector2d(0,1)):
                    self.state = "STAND"
                else:
                    print "state fall"
                    self.state = "FALLING"
            self.anim.state = self.state
            self.anim.forceUpdate()
    def checkHitsOld(self):
        rect = pygame.Rect(0,0,50,50) #arbitrary, can be more precise
        wallRects = self.p.cont.getWallRects(rect)
        hits = self.getRect().collidelistall(wallRects)
        for i in hits:
            self.p.cont.wList[self.p.cont.getMatrixIndex(wallRects[i])].highlight = True
        if len(hits) > 0:
            #TODO make sure to check only on ground hits
            if self.state == "JUMP" or self.state == "FALLING":
                self.state = "STAND"
            #for now
            intersect = wallRects[hits[0]].clip(self.getRect())
            change = self.pos - self.hitOld
            if math.fabs(change.x/(intersect.w+0.000000001)) > math.fabs(change.y/(intersect.h+0.000000001)):
                if change.x > 0: self.pos.x -= intersect.w
                else: self.pos.x += intersect.w
            else:
                if change.y > 0: self.pos.y += intersect.h
                else: self.pos.y -= intersect.h
            if len(hits) == 1:
                pass
            else: pass
            

                
class WomanEn(PlayerEn):
    def __init__(self,controller):
        self.anim = MW_animator.Animator(MW_xml.getChildNodeWithAttribute(xml.dom.minidom.parse("characters.xml"), "sprite","name","woman"))
        PlayerEn.__init__(self,controller)
        
    def input(self, events):
        PlayerEn.input(self,events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    if self.state == "STAND" or self.state == "WALK":
                        self.state = "JUMP"
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    if self.state == "STAND" or self.state == "WALK":
                        self.state = "WALK"
                        if e.key == pygame.K_LEFT:
                            self.anim.dir = "LEFT"
                        else: self.anim.dir = "RIGHT"
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    if self.state == "WALK":
                        self.state = "STAND"
    def update(self):
        #print self.state, self.anim.activeNode.id
        self.hitOld = self.getRect()
        #get input, update and move character based on input, check hits, check if over ground, if so, will update next loop
        if self.p.activePlayer == self:
            self.input(MW_global.eventList)
        elif self.state == "WALK": self.state = "STAND"
        self.anim.state = self.state
        self.anim.update()
        self.pos += self.anim.getVelData()
        self.checkHits()
        #check if over ground
        if not self.checkProjected(Vector2d(0,1)):
            if self.state != "JUMP":
                self.state = "FALLING" 
    
    def draw(self):
        MW_global.camera.drawOnScreen(self.anim.getImage(), self.pos+self.anim.getDrawOffset(), self.anim.getDrawRect())
        #pygame.draw.rect(MW_global.screen,COLOR_WHITE,MW_global.camera.convertCrds(self.getRect()),1)
        #pygame.draw.rect(MW_global.screen,COLOR_WHITE,self.getRect().inflate(40,40),1)
    
    def getRect(self):
        r = pygame.Rect(self.anim.activeNode.hRect)
        r.x += self.pos.x
        r.y += self.pos.y
        return r
    
class ManEn(PlayerEn):
    def __init__(self,controller):
        self.anim = MW_animator.Animator(MW_xml.getChildNodeWithAttribute(xml.dom.minidom.parse("characters.xml"), "sprite","name","man"))
        PlayerEn.__init__(self,controller)
        
    def input(self, events):
        PlayerEn.input(self,events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    if self.state == "STAND" or self.state == "WALK":
                        self.state = "JUMP"
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    if self.state == "STAND" or self.state == "WALK":
                        self.state = "WALK"
                        if e.key == pygame.K_LEFT:
                            self.anim.dir = "LEFT"
                        else: self.anim.dir = "RIGHT"
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    if self.state == "WALK":
                        self.state = "STAND"
    def update(self):
        #print self.state, self.anim.activeNode.id
        self.hitOld = self.getRect()
        #get input, update and move character based on input, check hits, check if over ground, if so, will update next loop
        if self.p.activePlayer == self:
            self.input(MW_global.eventList)
        elif self.state == "WALK": self.state = "STAND"
        self.anim.state = self.state
        self.anim.update()
        self.pos += self.anim.getVelData()
        self.checkHits()
        #check if over ground
        if not self.checkProjected(Vector2d(0,1)):
            if self.state != "JUMP":
                self.state = "FALLING" 
    
    def draw(self):
        MW_global.camera.drawOnScreen(self.anim.getImage(), self.pos+self.anim.getDrawOffset(), self.anim.getDrawRect())
        #pygame.draw.rect(MW_global.screen,COLOR_WHITE,MW_global.camera.convertCrds(self.getRect()),1)
        #pygame.draw.rect(MW_global.screen,COLOR_WHITE,self.getRect().inflate(40,40),1)
    
    def getRect(self):
        r = pygame.Rect(self.anim.activeNode.hRect)
        r.x += self.pos.x
        r.y += self.pos.y
        return r
    


        
    