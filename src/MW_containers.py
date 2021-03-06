import pygame
import xml.dom.minidom
import MW_global
import MW_editor
import MW_xml
import MW_entity
import os
from MW_datatypes import *
from MW_constants import *
import MW_constants
import MW_global

class SuperContainer:
    def __init__(self):
        self.duck = "quack"
        pass

class WomanContainer(SuperContainer):
    def __init__(self,controller):
        SuperContainer.__init__(self)
        self.enList = list()
        self.delList = list()
        self.p = controller
        self.createNew()
        
        self.shadowLady = MW_entity.WomanEn(self.p)
        self.shadowLady.teleport(SHADOW_LADY_START)
        self.shadowLady.input = blankfcn
        
    def update(self):
        if self.enList[len(self.enList)-1].anim.activeNode.state == "REALLYDEAD":
            self.createNew()
        self.enList[len(self.enList)-1].update()
        self.shadowLady.update()
    def getActiveWoman(self):
        return self.enList[len(self.enList)-1]
    def createNew(self):
        w = MW_entity.WomanEn(self.p)
        try:
            w.teleport(self.getActiveWoman().respawn)
            w.respawn = w.pos
        except: pass
        self.enList.append(w)
    def draw(self):
        for e in self.enList:
            e.draw()
        if MW_global.matrixcontainer.checkDraw(self.shadowLady):
            self.shadowLady.draw()
    def clearBodies(self):
        w = self.getActiveWoman()
        self.enList = list()
        self.enList.append(w)
    def deleteEntity(self,en):
        self.delList.append(en)
    def destroy(self):
        for e in self.enList:
            if e.destroy:
                self.delList.append(e)
        for e in self.delList:
            self.enList.remove(e)
        self.delList = list()
class MatrixContainer(SuperContainer):
    def __init__(self,dim,parent):
        SuperContainer.__init__(self)
        MW_global.matrixcontainer = self
        self.p = parent
        
        #these changes are overwridden by self.readXML
        self.width = dim[0]
        self.height = dim[1]
        self.startPos = Vector2d(0,0)
        self.wList = list()
        self.doorList = list()
        self.torchList = list()
        self.activeTorchList = list()
        for e in range(self.width*self.height):
            self.wList.append(None)
        self.length = len(self.wList)
	   
        if MW_global.gamemode == 2:
            self.edit = True
        else: self.edit = False
        self.editor = MW_editor.WallEditor(self)
        self.switchId = 0
        
        t = pygame.time.get_ticks()
        self.readXML(xml.dom.minidom.parse(os.path.join("data","testlevel.xml")))
	    #print "time to set up level", pygame.time.get_ticks() - t
    def update(self):
        if self.edit:
            self.editor.update()
        self.activeTorchList = self.getActiveTorches()
    def checkDraw(self,e):
        if not LIGHTING or (e.getName() == "TorchEn" and e.state == "BURNING"):
            return True
        
        #if we are dealing with walls
        if e.getName() == "WallEn":
            for f in self.p.getPlayerList():
                if lightingmode == 1 or self.p.getActivePlayer() == f:
                    if f.pos.distance(e.pos) < MW_constants.PLAYER_LIGHT_RADIUS[0] and f.anim.activeNode.state != "REALLYREALLYDEAD":
                        e.state = "LIGHT"
                        return True
            for f in self.activeTorchList:
                if f.pos.distance(e.pos) < MW_constants.TORCH_RADIUS[0]:
                    e.state = "LIGHT"
                    return True
            for f in self.p.getPlayerList():
                if lightingmode == 1 or self.p.getActivePlayer() == f:
                    if f.pos.distance(e.pos) < MW_constants.PLAYER_LIGHT_RADIUS[1] and f.anim.activeNode.state != "REALLYREALLYDEAD":
                        e.state = "DARK"
                        return True
            for f in self.activeTorchList:
                if f.pos.distance(e.pos) < MW_constants.TORCH_RADIUS[1]:
                    e.state = "DARK"
                    return True
            return False
                
        for f in self.p.getPlayerList():
            if lightingmode == 1 or self.p.getActivePlayer() == f:
                if f.pos.distance(e.pos) < MW_constants.PLAYER_LIGHT_RADIUS[0] and f.anim.activeNode.state != "REALLYREALLYDEAD":
                        return True
        for f in self.activeTorchList:
            if f.pos.distance(e.pos) < MW_constants.TORCH_RADIUS[0]:
                return True
        return False
    def draw(self):
        rect = self.getMatrixRect(MW_global.camera.rect)
        for r in range(rect.h):
            for c in range(rect.w):
                e = self.wList[self.getIndex((rect.x + c),(rect.y + r))]
                if e:
                    e.update()
                    if self.checkDraw(e):
                            e.draw()
        if self.edit: 
            pygame.draw.rect(MW_global.screen,COLOR_WHITE,MW_global.camera.convertCrds(self.getRect()),1)
            self.editor.draw()
    def addEn(self,en,pos):
        print en, "added"
        index = self.getIndex(*self.getMatrixPosition(pos))
        #print pos, TILING_SIZE, self.getMatrixPosition(pos)
        if self.wList[index] and self.wList[index].getName() == "TorchEn":
            self.torchList.remove(self.wList[index])
        if self.wList[index] and self.wList[index].getName() == "DoorEn":
            self.doorList.remove(self.wList[index])		 
        self.wList[index] = en
        if en and en.getName() == "TorchEn":
            self.torchList.append(en)
        elif en and en.getName() == "DoorEn":
            self.doorList.append(en)
            en.id = self.switchId
        elif en and en.getName() == "SwitchEn":
            self.switchId += 1
            en.id = self.switchId
    def getActiveTorches(self):
        return filter(isInRadius,filter(isActive,self.torchList))
    def getActiveTorchesOld(self):
        #print self.getMatrixRect(MW_global.camera.rect).inflate(TORCH_RADIUS/TILING_SIZE.x,TORCH_RADIUS/TILING_SIZE.y)
        #return self.getTypes(self.getMatrixRect(MW_global.camera.rect).inflate(TORCH_RADIUS/TILING_SIZE.x,TORCH_RADIUS/TILING_SIZE.y),"TorchEn")
        return filter(isActive,self.getTypesEn(self.getMatrixRect(MW_global.camera.rect).inflate(TORCH_RADIUS/TILING_SIZE.x,TORCH_RADIUS/TILING_SIZE.y),"TorchEn"))
    def getRespawnRects(self,rect):
        return self.getTypes(rect,"RespawnEn")
    def getTorchRects(self,rect):
        return self.getTypes(rect,"TorchEn")
    def getSpikeRects(self,rect):
        return self.getTypes(rect,"SpikeEn")
    def getSwitchRects(self,rect):
        return self.getTypes(rect,"SwitchEn")
    def getWallRects(self,rect):
        return self.getTypes(rect,("WallEn","DoorEn"))
    def getAtIndex(self,index):
        return self.wList[index]
    def getTypes(self,rect,type):
        ret = list()
        for r in range(rect.h):
            for c in range(rect.w):
                e = self.wList[self.getIndex((rect.x + c),(rect.y + r))]
                if e and e.getName() in type:
                    ret.append(e.getRect())
        return ret
    def getTypesEn(self,rect,type):
        ret = list()
        for r in range(rect.h):
            for c in range(rect.w):
                e = self.wList[self.getIndex((rect.x + c),(rect.y + r))]
                if e and e.getName() == type:
                    ret.append(e)
        return ret
        
    def setRectWalls(self,rect):
        rect = rect.inflate(TILING_SIZE.x,TILING_SIZE.y)
        for r in range(rect.h):
            for c in range(rect.w):
                self.setWall(self.getIndex((rect.x + c),(rect.y + r)))
                
    def setAllWalls(self):
        for i in range(self.length):
            if isinstance(self.wList[i],WallEn):
                self.setWall(self,getCart(i))

    
            
    def setWall(self, *args):
        if len(args == 1): x,y = args[0].x, args[0].y
        else: x,y = args[0],args[1]
        l = r = t = b = False
        if self.isInBound(x+1, y) and isinstance(self.wList[self.getIndex(x+1,y)],MW_entity.WallEn): r = True
        if self.isInBound(x-1, y) and isinstance(self.wList[self.getIndex(x-1,y)],MW_entity.WallEn): l = True
        if self.isInBound(x, y+1) and isinstance(self.wList[self.getIndex(x,y+1)],MW_entity.WallEn): b = True
        if self.isInBound(x, y-1) and isinstance(self.wList[self.getIndex(x,y-1)],MW_entity.WallEn): t = True
        #TODO decide how we want to generate tiles
    def isInBound(self,x,y):
        if x + y*self.width < self.length: return True
        return False
    def getIndex(self,x,y):
        i = x + y*self.width
        if i < self.length: return i
        else:
            #self.printXML()
            #TEMPORARY
            return (0)
            #raise Exception("out of index")
    def getRect(self):
        #print self.width,self.height
        #print self.width*TILING_SIZE.x,self.height*TILING_SIZE.y
        return pygame.Rect(self.startPos.x,self.startPos.y,self.width*TILING_SIZE.x,self.height*TILING_SIZE.y)
    def getCart(self,index):
        return index%self.width, int(index/self.width)
    def getMatrixRect(self,rect): #used for converting camera rect to matrix rect
        x,y = self.getMatrixPosition(rect)
        w = int(rect.w/TILING_SIZE.x)
        h = int(rect.h/TILING_SIZE.y)
        return pygame.Rect(x,y,w,h).inflate(1,1)
    def getScreenPosition(self,x,y):    #converts matrix coordinates to screen coordinates
        return Vector2d(self.startPos.x + x*TILING_SIZE.x, self.startPos.y + y*TILING_SIZE.y)
    def getMatrixPosition(self,pos):
        x = int((pos.x-self.startPos.x)/TILING_SIZE.x)
        y = int((pos.y-self.startPos.y)/TILING_SIZE.y)
        return x,y
    def getMatrixIndex(self,pos):
        return self.getIndex(*self.getMatrixPosition(pos))    
    def callList(self,rect,fcn,args=None):
        for r in range(rect.h):
            for c in range(rect.w):
                if args==None:
                    fcn(self.wList[(rect.x+c) + (rect.y + r)*self.width])
                else:
                    fcn(self.wList[(rect.x+c) + (rect.y + r)*self.width],*args)
    
    def printXML(self):
        exml = xml.dom.minidom.parseString("<p><walls></walls></p>").getElementsByTagName("walls")[0]
        c = xml.dom.minidom.parseString(
                                        "<p><size w=\""
                                        +str(self.width)+"\" h=\""
                                        +str(self.height)+"\" x=\""
                                        +str(self.startPos.x)+"\" y=\"" 
                                        +str(self.startPos.y)+"\"/></p>"
                                        ).getElementsByTagName("size")[0]

        exml.appendChild(c)
        for i in range(len(self.wList)):
            if self.wList[i]:
                idstr = ""
                if self.wList[i].getName() == "DoorEn" or  self.wList[i].getName() == "SwitchEn" or  self.wList[i].getName() == "RespawnEn" or  self.wList[i].getName() == "TorchEn":
                    idstr = "\" id=\"" + str(self.wList[i].id)
                #for permanently open doors, but we do not really need these
                #if self.wList[i].getName() == "DoorEn" and self.wList[i].type == "OPEN":
                    #idstr = "\" id=\"" + str(self.wList[i].id) + "\" id=\"" + self.wList[i].type 
                exml.appendChild(xml.dom.minidom.parseString("<p><"+self.wList[i].getName()+" i=\""
                                                             +str(i)+idstr+ "\"/></p>").getElementsByTagName(self.wList[i].getName())[0])
        print exml.toxml()
    def readXML(self,exml):
        size = exml.getElementsByTagName("size")[0]
        self.startPos = Vector2d(int(size.getAttribute("x")),int(size.getAttribute("y")))
        self.width = int(size.getAttribute("w"))
        self.height = int(size.getAttribute("h"))
        self.wList = list()
	t1 = pygame.time.get_ticks()
        for e in range(self.width*self.height):
            self.wList.append(None)
        self.length = len(self.wList)
	t2 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("WallEn"):
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.WallEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            self.wList[index].index = index
	t3 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("SpikeEn"):
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.SpikeEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            self.wList[index].index = index
	t4 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("TorchEn"):
            #print "making torch"
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.TorchEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            if e.hasAttribute("id"):
                self.wList[index].id = int(e.getAttribute("id"))
            if self.wList[index].id in MW_global.torchStateMap:
                self.wList[index].state = MW_global.torchStateMap[self.wList[index].id]
            else: self.wList[index].state = "DEFAULT" 
            self.torchList.append(self.wList[index])
            self.wList[index].index = index
	t5 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("DoorEn"):
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.DoorEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            self.wList[index].id = int(e.getAttribute("id"))
            self.doorList.append(self.wList[index])
            self.wList[index].index = index
	t6 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("SwitchEn"):
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.SwitchEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            self.wList[index].id = int(e.getAttribute("id"))
            self.wList[index].index = index
	t7 = pygame.time.get_ticks()
        for e in exml.getElementsByTagName("RespawnEn"):
            index = int(e.getAttribute("i"))
            self.wList[index] = MW_entity.RespawnEn()
            self.wList[index].teleport(self.getScreenPosition(index%self.width,int(index/self.width)))
            self.wList[index].id = int(e.getAttribute("id"))
            self.wList[index].index = index
            
	print "size", t2-t1, "walls", t3-t2, "spikes", t4-t3, "torches", t5-t4, "doors", t6-t5, "switches", t7-t6
    
class DoodadContainer(SuperContainer):
    def __init__(self):
        SuperContainer.__init__(self)
        self.enList = list()
        self.delList = list()
        self.edit = True
        self.editor = MW_editor.DooEditor(self)
    def update(self):
        if self.edit:
            self.editor.update()
        for e in self.enList:
            e.update()
    def draw(self):
        if self.edit:
            self.editor.draw()
        for e in self.enList:
            e.draw()
    def deleteEntity(self,en):
        self.delList.append(en)
    def destroy(self):
        for e in self.enList:
            if e.destroy:
                self.delList.append(e)
        for e in self.delList:
            self.enList.remove(e)
        self.delList = list()

def isInRadius(torch):
    #TODO use circle square collision for this
    return True
def isActive(torch):
    return torch.state == "BURNING" or torch.state == "LIGHT"
