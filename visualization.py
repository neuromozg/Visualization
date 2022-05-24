#!/usr/bin/env python3

import pygame
import os
import random
import threading
import numpy as np
import time
import requests
import json
from datetime import datetime

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

URL = 'http://10.10.0.166:31222/user?user=all'

WIDTH = 1920
HEIGHT = 1080
FPS = 25

POL_WIDTH = 1100
POL_HEIGHT = 1100

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (80, 80, 80)
LINE_COLOR = (0, 80, 0)


def getIP():
    #cmd = 'hostname -I | cut -d\' \' -f1'
    #ip = subprocess.check_output(cmd, shell = True) #получаем IP
    res = os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','') #получаем IP, удаляем \n
    return res

class ObjType:
    """ Класс c типами объектов """
    ROBOT = 0x00 
    COPTER = 0x01
    CAMERA_PTZ = 0x03
    VERTIPORT = 0x04
    START_ZONE = 0x05

class ObjFunc:
    """ Класс c функциональностью объектов """
    NONE = 0x00
    TRANSPORT = 0x01
    CANNON = 0x02

class VertiportState:
    EMPTY = 0x00
    PROD_READY = 0x01
    PROD_LOADED = 0x02
    

class CyberDromObject(pygame.sprite.Sprite):
    def __init__(self, fileImg, obj_id, number, objType, objFunc):
        pygame.sprite.Sprite.__init__(self)
        self.obj_id = obj_id
        self.number = number
        self.objType = objType
        self.objFunc = objFunc
        self.image = pygame.image.load(fileImg)
        self.rect = self.image.get_rect()
        #self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange((WIDTH-POL_WIDTH)/2+50, (WIDTH-POL_WIDTH)/2 + POL_WIDTH-50)
        self.rect.y = random.randrange((HEIGHT-POL_HEIGHT)/2+50, (HEIGHT-POL_HEIGHT)/2+POL_HEIGHT-50)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.cannon = 10
        self.cargo = False
        self.cargoColor = BLACK        
        self.height = 0
        self.lostCoord = False
        self.vertiportState = VertiportState.EMPTY
        self.balls = 0
        self.online = False
        self.posMetr = (0, 0, 0)

    def update(self):
        if self.objType in (ObjType.ROBOT, ObjType.COPTER):
            self.rect.x += self.speedx
            self.rect.y += self.speedy
            if self.rect.bottom > POL_HEIGHT or self.rect.top < HEIGHT-POL_HEIGHT:
                self.speedy = -self.speedy

            if self.rect.left < (WIDTH-POL_WIDTH)/2 or self.rect.right > (WIDTH-POL_WIDTH)/2 + POL_WIDTH:
                self.speedx = -self.speedx

    def rotate(self, grad):
        pass

class Pepe(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(104):
            self.images.append(pygame.image.load('img/pepe/frame_%.3d_delay-0.02s.gif' % i))
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = ( WIDTH/2, HEIGHT/2)

    def update(self):
        #when the update method is called, we will increment the index
        self.index += 1
 
        #if the index is larger than the total images
        if self.index >= len(self.images):
            #we will make the index to 0 again
            self.index = 0
        
        #finally we will update the image that will be displayed
        self.image = self.images[self.index]

class Zhdoon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/Homunculus_loxodontus.png')
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.count = 0
        self.direction = -1

    def update(self):
        if self.count == 30:
            self.direction *= -1
            self.count = 0
        self.count += 1    
        self.rect.y += self.direction

class CyberDromPolygon(pygame.sprite.Sprite):
    def __init__(self, image, number, type):
        pygame.sprite.Sprite.__init__(self)


class VisualisationFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, screen, fps, lock, **properties):
        super(VisualisationFactory, self).__init__(**properties)
        self.fps = fps
        self.number_frames = 0
        self.duration = 1 / self.fps * Gst.SECOND
        self.screen = screen
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             ' caps=video/x-raw,format=RGB,width={},height={},framerate={}/1 ' \
                             '! videorate ! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96'.format(self.screen.get_width(), self.screen.get_height(), self.fps)
        self._busLock = lock
        
    def do_create_element(self, url):
        print(self.launch_string)
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        #appsrc.set_property('block', False)
        #appsrc.set_property('is-live', True)
        #appsrc.set_property('format', 'GST_FORMAT_TIME')        
        appsrc.connect('need-data', self.on_need_data)

    def ndarray_to_gst_buffer(self, array):
        """Converts numpy array to Gst.Buffer"""
        return Gst.Buffer.new_wrapped(array.tobytes())

    def on_need_data(self, src, lenght):
        self._busLock.acquire()
        try:
            numpy_frame = pygame.surfarray.array3d(self.screen) #создаем numpy массив из экрана Pygame
        finally:
            self._busLock.release()
        numpy_frame = np.swapaxes(numpy_frame, 0, 1) #поворачиваем оси
        buf = self.ndarray_to_gst_buffer(numpy_frame)
        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp
        
        retval = src.emit('push-buffer', buf)
        self.number_frames += 1
        #print(self.number_frames)
        if retval != Gst.FlowReturn.OK:
            print(retval)
        return True

class GstRtspServer(GstRtspServer.RTSPServer):
    def __init__(self, screen, lock, **properties):
        super(GstRtspServer, self).__init__(**properties)
        self.factory = VisualisationFactory(screen, FPS, lock)
        self.factory.set_shared(True)
        self.get_mount_points().add_factory("/test", self.factory)
        self.attach(None)

        port_FrontServer = self.get_bound_port()
        print('RTSP server started: rtsp://%s:%d/test' % (getIP(), port_FrontServer))

def draw_text(surf, text, size, x, y, color = WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def convertMeterToPix(x, y):
    pix_x = int((WIDTH-POL_WIDTH)/2 + x*100)
    pix_y = int((HEIGHT-POL_HEIGHT)/2+POL_HEIGHT - y*100)
    return (pix_x, pix_y)
    

if __name__ == '__main__':
    
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Cyber Drom 2022')
    
    #font_name = pygame.font.match_font('arial')
    font_name = pygame.font.match_font('DejaVuSans')
    
    clock = pygame.time.Clock()
	
    screenLock = threading.Lock() #блокировка для раздельного доступа к screen

    GObject.threads_init()
    Gst.init(None)

    rtspServer = GstRtspServer(screen, screenLock)

    mainLoop = GObject.MainLoop()

    mainLoopThread = threading.Thread(target = mainLoop.run, daemon = True)
    mainLoopThread.start()

    all_objects = pygame.sprite.Group()

    vertiports = pygame.sprite.Group()
    for i in range(4):
        vertiport = CyberDromObject('img/vertiport.png', i, i+1, ObjType.VERTIPORT, ObjFunc.NONE)
        vertiports.add(vertiport)
        all_objects.add(vertiport)

    for i in range(4):
        vertiport = CyberDromObject('img/StartCopter%d.png' % (i+1), i+4,  i+1, ObjType.START_ZONE, ObjFunc.NONE)
        vertiports.add(vertiport)
        all_objects.add(vertiport)

    for i in range(4):
        vertiport = CyberDromObject('img/StartRobot%d.png' % (i+1), i+8, i+1, ObjType.START_ZONE, ObjFunc.NONE)
        vertiports.add(vertiport)
        all_objects.add(vertiport)

    objects = pygame.sprite.Group()
    for i in range(4):
        obj = CyberDromObject('img/drone_img.png', i, i+1, ObjType.COPTER, ObjFunc.TRANSPORT)
        if i == 0:
            obj.objFunc = ObjFunc.CANNON   
        objects.add(obj)
        all_objects.add(obj)

    for i in range(4):
        obj = CyberDromObject('img/robot_img.png', i+5, i+1, ObjType.ROBOT, ObjFunc.TRANSPORT)
        if i == 0:
            obj.objFunc = ObjFunc.CANNON
        objects.add(obj)
        all_objects.add(obj)

    #pepe = Pepe()
    #creating a group with our sprite
    #pepe_group = pygame.sprite.Group(pepe)

    zhdoon = Zhdoon()
    zhdoon_group = pygame.sprite.Group(zhdoon)
    
    ballsEdubot = 0
    ballsPioneer = 0

    debugMode = False
    debugFont = pygame.font.Font(font_name, 30)

    # Цикл игры
    running = True

    while running:
        # Держим цикл на правильной скорости
        clock.tick(FPS)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debugMode = not debugMode
                      
        try:
            objectData = requests.get(URL)
            
        except :
            #print ('error')
            objectData = None

        if (not objectData is None):
        
            
            #print(objectData)
            data = json.loads(objectData.text)

            ballsEdubot = data['balls_team_Edubot']
            ballsPioneer = data['balls_team_Pioneer']
            
            
            for vert in data['vertiports']:
                x, y, _ = data['vertiports'][vert]['position']
                try:
                    vertState = data['vertiports'][vert]['state']
                except:
                    vertState = VertiportState.EMPTY

                try:
                    cargoColor = data['vertiports'][vert]['cargo_color']
                except:
                    cargoColor = BLACK
                    
                for obj in vertiports:
                    if obj.obj_id == int(vert):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.vertiportState = vertState
                        obj.cargoColor = cargoColor
                        break

            for user in data['user']:
                #print(obj, data['user'][user]['position'])
                x, y, h, yaw = data['user'][user]['position']
                balls = data['user'][user]['balls_user']
                
                try:
                    cannon = data['user'][user]['bullets']
                except:
                    cannon = 0

                try:
                    cargo = data['user'][user]['cargo_status']
                except:
                    cargo = False

                try:
                    cargoColor = data['user'][user]['cargo_color']
                except:
                    cargoColor = BLACK

                try:
                    online = data['user'][user]['is_connected']
                except:
                    online = False
                    
                for obj in objects:
                    if obj.obj_id == int(user):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.cannon = cannon
                        obj.cargo = cargo
                        obj.balls = balls
                        obj.online = online
                        obj.cargoColor = cargoColor
                        obj.posMetr = (x, y, h)
                        break

        screenLock.acquire()
        try:
            if objectData is None:
                #pepe_group.update()
                zhdoon_group.update()

                # Рендеринг
                screen.fill(WHITE)
                #pepe_group.draw(screen)
                #draw_text(screen, 'СКОРО НАЧНЕМ', 70, pepe.rect.centerx, pepe.rect.bottom + 60, BLACK)
                zhdoon_group.draw(screen)
                draw_text(screen, 'СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)
            else:
                # Обновление координат и состояний объектов
                all_objects.update()

                # Рендеринг
                screen.fill(WHITE)
                
                pygame.draw.rect(screen, BLACK, ((WIDTH-POL_WIDTH)/2, (HEIGHT-POL_HEIGHT)/2, POL_WIDTH, POL_HEIGHT))


                #Результаты команд
                draw_text(screen, 'Команда КБЛА', 50, int((WIDTH-POL_WIDTH)/4), 20, BLACK)
                draw_text(screen, str(ballsPioneer), 70, int((WIDTH-POL_WIDTH)/4), 80, BLACK)
                
                draw_text(screen, 'Команда РТС', 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 20, BLACK)
                draw_text(screen, str(ballsEdubot), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 80, BLACK)
                
                #линии
                #вертикальные
                for x in range(int((WIDTH-POL_WIDTH)/2), int((WIDTH-POL_WIDTH)/2+POL_WIDTH), 100):
                    pygame.draw.line(screen, LINE_COLOR, (x, int(HEIGHT-POL_HEIGHT)/2), (x, int(HEIGHT-POL_HEIGHT)/2+POL_HEIGHT), 2)
                #горизонтальные
                for y in range(int((HEIGHT-POL_HEIGHT)/2), int((HEIGHT-POL_HEIGHT)/2+POL_HEIGHT), 100):
                    pygame.draw.line(screen, LINE_COLOR, (int((WIDTH-POL_WIDTH)/2), y), (int((WIDTH-POL_WIDTH)/2+POL_WIDTH), y), 2)
            
        
                #screen.blit(background, background_rect)
                all_objects.draw(screen) #отрисовываем все спрайты

                # отрисовка текста + графика
                for obj in all_objects:
                    #наименование аппарата сверху и баллы
                    if obj.objType == ObjType.ROBOT:
                        draw_text(screen, 'РТС %d' % obj.number, 15, obj.rect.centerx, obj.rect.top-15)
                        
                        draw_text(screen, 'PTC %d' % obj.number, 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (50 + obj.number*170), BLACK)
                        draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (110 + obj.number*170), BLACK)                       

                    #наименование аппарата сверху и баллы
                    elif obj.objType == ObjType.COPTER:
                        draw_text(screen, 'КБЛА %d' % obj.number, 15, obj.rect.centerx, obj.rect.top-15)

                        draw_text(screen, 'КБЛА %d' % obj.number, 50, int((WIDTH-POL_WIDTH)/4), (50 + obj.number*170), BLACK)
                        draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4), (110 + obj.number*170), BLACK)
                        
                    #подпись снизу
                    if obj.objFunc == ObjFunc.TRANSPORT:
                        if obj.cargo:
                            pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x - 5, obj.rect.y - 5, obj.rect.width + 10, obj.rect.height + 10), 2)
                            draw_text(screen, 'Загружен', 15, obj.rect.centerx, obj.rect.bottom+10)
                            
                    elif obj.objFunc == ObjFunc.CANNON:
                        draw_text(screen, 'Заряды %d' % obj.cannon , 15, obj.rect.centerx, obj.rect.bottom+10)
                        if obj.cannon > 0:
                            pygame.draw.circle(screen, RED, obj.rect.center, 50, 2)

                    #Перекрестье если пропали координаты, надпись OFFLINE
                    if obj.objType in (ObjType.ROBOT, ObjType.COPTER):
                        if obj.lostCoord:
                            pygame.draw.line(screen, RED, obj.rect.topleft, obj.rect.bottomright, 2)
                            pygame.draw.line(screen, RED, obj.rect.topright, obj.rect.bottomleft, 2)

                        if obj.online == False:
                            pygame.draw.rect(screen, GRAY, (obj.rect.centerx - 40, obj.rect.centery - 10, 80, 20))
                            draw_text(screen, 'OFFLINE', 20, obj.rect.centerx, obj.rect.centery-12, RED)

                    #Мигаем вертипортами
                    if obj.objType == ObjType.VERTIPORT:
                        if obj.vertiportState == VertiportState.PROD_LOADED:
                            #мигаем
                            if int(datetime.today().timestamp() % 2):
                                pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x+5, obj.rect.y+5, obj.rect.width - 10, obj.rect.height - 10), 5)
                            draw_text(screen, 'Продукция готова', 15, obj.rect.centerx, obj.rect.bottom+10)
                        elif obj.vertiportState == VertiportState.PROD_READY:
                            pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x+5, obj.rect.y+5, obj.rect.width - 10, obj.rect.height - 10), 5)
                            draw_text(screen, 'Загрузка', 15, obj.rect.centerx, obj.rect.bottom+10)

                    if debugMode:
                        if obj.objType in (ObjType.ROBOT, ObjType.COPTER):
                            text_surface = debugFont.render('%d [%.3f %.3f %.3f]' % (obj.number, obj.posMetr[0], obj.posMetr[1], obj.posMetr[2]), True, BLACK)
                            if obj.objType == ObjType.COPTER:
                                screen.blit(text_surface, (int((WIDTH-POL_WIDTH)/2) + POL_WIDTH+40, (900 + obj.number*30)))
                            elif obj.objType == ObjType.ROBOT:
                                screen.blit(text_surface, (40, (900 + obj.number*30)))

                    
                    
        finally:
            screenLock.release()
                    
        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()


    mainLoop.quit() #останавливаем MainLoop
    mainLoopThread.join() #ожидаем завершения работы потока

    pygame.quit()
