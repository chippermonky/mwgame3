import pygame
import MW_global
import MW_controller
import sys
from MW_constants import *
from MW_datatypes import *

mwc = MW_controller.ControllerController()
#mwc = MW_controller.oldController()
last = pygame.time.get_ticks()

while 1:
    #if time expired
    
    
    if(pygame.time.get_ticks() - last > MSPERFRAME):
        while(pygame.time.get_ticks() - last > MSPERFRAME):
            last += MSPERFRAME
        MW_global.screen.fill((0,0,0))
        t1 = pygame.time.get_ticks()
        mwc.loop()
        MW_global.frame += 1
        if pygame.time.get_ticks()%200 == 1:
            pass
            #print "cycle time", pygame.time.get_ticks() - t1
        if isFull:
            p = (MW_global.screen.get_width()/2-WIDTH/2,MW_global.screen.get_height()/2-HEIGHT/2)
            #MW_global.realscreen.blit(MW_global.screen,p)
            if sys.platform == 'win32' or sys.platform == 'darwin':
                pygame.display.flip()
            else:
                pygame.display.update(pygame.Rect(p[0],p[1],WIDTH,HEIGHT)) 
        else:
            pygame.display.flip()   #flip the screen
    #else wait the difference3
    else: 
        pygame.time.wait( MSPERFRAME - pygame.time.get_ticks() + last)
        
        
    #quit
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_F12]:
        pass
        #restart for installation
        MW_global.screen.fill((0,0,0))
        pygame.display.flip()
        mwc = MW_controller.ControllerController()
    if pygame.mouse.get_pressed()[0]:
        print "goodbye"
        del mwc
        pygame.quit()
        break

