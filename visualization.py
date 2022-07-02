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
<<<<<<< HEAD
import time
=======
>>>>>>> origin/main

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
<<<<<<< HEAD
from gi.repository import Gst, GstRtspServer, GLib

URL = 'http://10.10.0.166:31222/user?user=all'
HTTP_REUEST_TIMEOUT = 3

FileFrozenImg = 'img/frozen_img.png'
=======
from gi.repository import Gst, GstRtspServer, GObject

URL = 'http://10.10.0.166:31222/user?user=all'
>>>>>>> origin/main

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
<<<<<<< HEAD
LIGHT_BLUE = (0, 191, 255)
=======
>>>>>>> origin/main
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
    
<<<<<<< HEAD
=======

>>>>>>> origin/main
class CyberDromObject(pygame.sprite.Sprite):
    def __init__(self, fileImg, obj_id, number, objType, objFunc):
        pygame.sprite.Sprite.__init__(self)
        self.obj_id = obj_id
        self.number = number
        self.objType = objType
        self.objFunc = objFunc
<<<<<<< HEAD
        self.baseImg = pygame.image.load(fileImg)
        self.frozenImg = pygame.image.load(FileFrozenImg)
        self.image = self.baseImg
=======
        self.image = pygame.image.load(fileImg)
>>>>>>> origin/main
        self.rect = self.image.get_rect()
        #self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange((WIDTH-POL_WIDTH)/2+50, (WIDTH-POL_WIDTH)/2 + POL_WIDTH-50)
        self.rect.y = random.randrange((HEIGHT-POL_HEIGHT)/2+50, (HEIGHT-POL_HEIGHT)/2+POL_HEIGHT-50)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.cannon = 10
<<<<<<< HEAD
        self.fire = False
=======
>>>>>>> origin/main
        self.cargo = False
        self.cargoColor = BLACK        
        self.height = 0
        self.lostCoord = False
        self.vertiportState = VertiportState.EMPTY
        self.balls = 0
        self.online = False
        self.posMetr = (0, 0, 0)
<<<<<<< HEAD
        self.blocked = False
        self.disqualified = False

    def update(self):
        if self.objType in (ObjType.ROBOT, ObjType.COPTER):
            if self.blocked:
                self.image = self.frozenImg
            else:
                self.image = self.baseImg
            
                
=======

    def update(self):
        if self.objType in (ObjType.ROBOT, ObjType.COPTER):
>>>>>>> origin/main
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

<<<<<<< HEAD
class ScreenSaver(pygame.sprite.Sprite):
    def __init__(self, fileImg, shift = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(fileImg)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2 + shift)
=======
class Zhdoon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/Homunculus_loxodontus.png')
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
>>>>>>> origin/main
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

<<<<<<< HEAD
def draw_text(surf, text, size, x, y, color = WHITE, backgound = None):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color, backgound)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
    return text_rect
=======
def draw_text(surf, text, size, x, y, color = WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
>>>>>>> origin/main

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

<<<<<<< HEAD
    #GLib.threads_init()
=======
    GObject.threads_init()
>>>>>>> origin/main
    Gst.init(None)

    rtspServer = GstRtspServer(screen, screenLock)

<<<<<<< HEAD
    mainLoop = GLib.MainLoop()
=======
    mainLoop = GObject.MainLoop()
>>>>>>> origin/main

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

<<<<<<< HEAD
    obj = CyberDromObject('img/camera_img.png', 4, 5, ObjType.CAMERA_PTZ, ObjFunc.NONE)
    objects.add(obj)
    all_objects.add(obj)
        
=======
>>>>>>> origin/main
    for i in range(4):
        obj = CyberDromObject('img/robot_img.png', i+5, i+1, ObjType.ROBOT, ObjFunc.TRANSPORT)
        if i == 0:
            obj.objFunc = ObjFunc.CANNON
        objects.add(obj)
        all_objects.add(obj)

<<<<<<< HEAD
    obj = CyberDromObject('img/camera_img.png', 9, 5, ObjType.CAMERA_PTZ, ObjFunc.NONE)
    objects.add(obj)
    all_objects.add(obj)

=======
>>>>>>> origin/main
    #pepe = Pepe()
    #creating a group with our sprite
    #pepe_group = pygame.sprite.Group(pepe)

<<<<<<< HEAD
    #screenSaver = ScreenSaver('img/Homunculus_loxodontus.png')
    screenSaver = ScreenSaver('img/cyber_drom_logo.png', -50)
    screenSaver_group = pygame.sprite.Group(screenSaver)

    img_cyberdrom = pygame.image.load('img/cyber_drom_background.png')
=======
    zhdoon = Zhdoon()
    zhdoon_group = pygame.sprite.Group(zhdoon)
>>>>>>> origin/main
    
    ballsEdubot = 0
    ballsPioneer = 0

    debugMode = False
    debugFont = pygame.font.Font(font_name, 30)

<<<<<<< HEAD
    start_time = time.time()
    counter = 0

    # Цикл игры
    running = True

    oldStatusGame = 0
    showTextStartTime = time.time()
    showText = ''
    showTextDelay = 0

    while running:

=======
    # Цикл игры
    running = True

    while running:
        # Держим цикл на правильной скорости
        clock.tick(FPS)
 
>>>>>>> origin/main
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debugMode = not debugMode
                      
        try:
<<<<<<< HEAD
            #objectData = requests.get(URL, timeout = HTTP_REUEST_TIMEOUT)
            objectData = requests.get(URL)
            
            #print(objectData.status_code)

            data = json.loads(objectData.text)
=======
            objectData = requests.get(URL)
            
>>>>>>> origin/main
        except :
            #print ('error')
            objectData = None

<<<<<<< HEAD
        showScreenSaver = True
        
        if not objectData is None:
            showScreenSaver = False
            
            data = json.loads(objectData.text)
            
            ballsEdubot = data['balls_team_Edubot']
            ballsPioneer = data['balls_team_Pioneer']
            foulTeamPioneer = data['foul_team_Pioneer']
            foulTeamEdubot = data['foul_team_Edubot']
            gameTime = data['game_time']
            statusGame = data['status_server'] #статус игры 1 - ждем подключения, 2 - обратный отсчет, 3 - играем, 4 - закончили
            maxFoul = data['max_foul'] #максимальное количество блокировок за игру
=======
        if (not objectData is None):
        
            
            #print(objectData)
            data = json.loads(objectData.text)

            ballsEdubot = data['balls_team_Edubot']
            ballsPioneer = data['balls_team_Pioneer']
>>>>>>> origin/main
            
            
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
<<<<<<< HEAD

                try:
                    fire = data['user'][user]['is_shoting']
                except:
                    fire = False

                try:
                    blocked = data['user'][user]['block_status']
                except:
                    blocked = False

                try:
                    disqualified = data['user'][user]['server_block']
                except:
                    disqualified = False
=======
>>>>>>> origin/main
                    
                for obj in objects:
                    if obj.obj_id == int(user):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.cannon = cannon
                        obj.cargo = cargo
                        obj.balls = balls
                        obj.online = online
                        obj.cargoColor = cargoColor
                        obj.posMetr = (x, y, h)
<<<<<<< HEAD
                        obj.fire = fire
                        obj.blocked = blocked
                        obj.disqualified = disqualified
=======
>>>>>>> origin/main
                        break

        screenLock.acquire()
        try:
<<<<<<< HEAD
            if showScreenSaver:
                # Держим цикл на правильной скорости
                clock.tick(FPS)
                
                #pepe_group.update()
                screenSaver_group.update()
=======
            if objectData is None:
                #pepe_group.update()
                zhdoon_group.update()
>>>>>>> origin/main

                # Рендеринг
                screen.fill(WHITE)
                #pepe_group.draw(screen)
                #draw_text(screen, 'СКОРО НАЧНЕМ', 70, pepe.rect.centerx, pepe.rect.bottom + 60, BLACK)
<<<<<<< HEAD
                #zhdoon_group.draw(screen)
                #draw_text(screen, 'БОСС, СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)

                screen.blit(img_cyberdrom, (0, 0))

                screenSaver_group.draw(screen)
                #draw_text(screen, 'БОСС, СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)
                
=======
                zhdoon_group.draw(screen)
                draw_text(screen, 'СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)
>>>>>>> origin/main
            else:
                # Обновление координат и состояний объектов
                all_objects.update()

                # Рендеринг
                screen.fill(WHITE)
                
                pygame.draw.rect(screen, BLACK, ((WIDTH-POL_WIDTH)/2, (HEIGHT-POL_HEIGHT)/2, POL_WIDTH, POL_HEIGHT))

<<<<<<< HEAD
                #Результаты команд
                draw_text(screen, 'Команда КБЛА', 50, int((WIDTH-POL_WIDTH)/4), 20, BLACK)
                draw_text(screen, str(ballsPioneer), 70, int((WIDTH-POL_WIDTH)/4), 80, BLACK)
                if foulTeamPioneer > maxFoul:
                    draw_text(screen, 'Дисквалификация', 40, int((WIDTH-POL_WIDTH)/4), 180, BLACK)
                else:
                    draw_text(screen, 'Нарушения: %d из %d' % (foulTeamPioneer, maxFoul), 40, int((WIDTH-POL_WIDTH)/4), 180, BLACK)
                
                
                draw_text(screen, 'Команда РТС', 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 20, BLACK)
                draw_text(screen, str(ballsEdubot), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 80, BLACK)
                if foulTeamEdubot > maxFoul:
                    draw_text(screen, 'Дисквалификация', 40, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 180, BLACK)
                else:
                    draw_text(screen, 'Нарушения: %d из %d' % (foulTeamEdubot, maxFoul), 40, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 180, BLACK)
=======

                #Результаты команд
                draw_text(screen, 'Команда КБЛА', 50, int((WIDTH-POL_WIDTH)/4), 20, BLACK)
                draw_text(screen, str(ballsPioneer), 70, int((WIDTH-POL_WIDTH)/4), 80, BLACK)
                
                draw_text(screen, 'Команда РТС', 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 20, BLACK)
                draw_text(screen, str(ballsEdubot), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 80, BLACK)
>>>>>>> origin/main
                
                #линии
                #вертикальные
                for x in range(int((WIDTH-POL_WIDTH)/2), int((WIDTH-POL_WIDTH)/2+POL_WIDTH), 100):
                    pygame.draw.line(screen, LINE_COLOR, (x, int(HEIGHT-POL_HEIGHT)/2), (x, int(HEIGHT-POL_HEIGHT)/2+POL_HEIGHT), 2)
                #горизонтальные
                for y in range(int((HEIGHT-POL_HEIGHT)/2), int((HEIGHT-POL_HEIGHT)/2+POL_HEIGHT), 100):
                    pygame.draw.line(screen, LINE_COLOR, (int((WIDTH-POL_WIDTH)/2), y), (int((WIDTH-POL_WIDTH)/2+POL_WIDTH), y), 2)
<<<<<<< HEAD


                #линии ограничения зоны полетов-заездов
                pygame.draw.line(screen, BLUE, convertMeterToPix(3, 0), convertMeterToPix(3, 11), 5)
                pygame.draw.line(screen, RED, convertMeterToPix(7.5, 0), convertMeterToPix(7.5, 11), 5)


                #линии разделения текста по бокам
                lines = range(250, 1080, 170)
                for y in lines:
                    pygame.draw.line(screen, BLUE, (10, y), ((WIDTH-POL_WIDTH)/2 - 10, y), 5)
                    pygame.draw.line(screen, RED, (10 + (WIDTH-POL_WIDTH)/2 + POL_WIDTH, y), (WIDTH - 10, y), 5)
                
=======
            
        
>>>>>>> origin/main
                #screen.blit(background, background_rect)
                all_objects.draw(screen) #отрисовываем все спрайты

                # отрисовка текста + графика
                for obj in all_objects:
<<<<<<< HEAD

                    backgroundColor = WHITE
                    if obj.blocked:
                        backgroundColor = LIGHT_BLUE        
                    if not obj.online:
                        backgroundColor = RED
                    
                    #наименование аппарата сверху и баллы
                    if obj.objType == ObjType.ROBOT:
                        draw_text(screen, 'РТС %d' % obj.number, 15, obj.rect.centerx, obj.rect.top-15)

                        name_rect = draw_text(screen, '  PTC %d  ' % obj.number, 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (100 + obj.number*170), BLACK, backgroundColor)
                        if obj.disqualified:
                            pygame.draw.line(screen, RED, name_rect.topleft, name_rect.bottomright, 7)
                            pygame.draw.line(screen, RED, name_rect.topright, name_rect.bottomleft, 7)
                            
                        if obj.objFunc == ObjFunc.TRANSPORT:
                            draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (110+50 + obj.number*170), BLACK)
                        elif obj.objFunc == ObjFunc.CANNON:
                            draw_text(screen, 'Заряды: %d' % obj.cannon, 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (110+50 + obj.number*170), BLACK)
                        
=======
                    #наименование аппарата сверху и баллы
                    if obj.objType == ObjType.ROBOT:
                        draw_text(screen, 'РТС %d' % obj.number, 15, obj.rect.centerx, obj.rect.top-15)
                        
                        draw_text(screen, 'PTC %d' % obj.number, 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (50 + obj.number*170), BLACK)
                        draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (110 + obj.number*170), BLACK)                       
>>>>>>> origin/main

                    #наименование аппарата сверху и баллы
                    elif obj.objType == ObjType.COPTER:
                        draw_text(screen, 'КБЛА %d' % obj.number, 15, obj.rect.centerx, obj.rect.top-15)

<<<<<<< HEAD
                        name_rect = draw_text(screen, '  КБЛА %d  ' % obj.number, 50, int((WIDTH-POL_WIDTH)/4), (100 + obj.number*170), BLACK, backgroundColor)
                        if obj.disqualified:
                            pygame.draw.line(screen, RED, name_rect.topleft, name_rect.bottomright, 7)
                            pygame.draw.line(screen, RED, name_rect.topright, name_rect.bottomleft, 7)
                        
                        if obj.objFunc == ObjFunc.TRANSPORT:
                            draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4), (110+50 + obj.number*170), BLACK)
                        elif obj.objFunc == ObjFunc.CANNON:
                            draw_text(screen, 'Заряды: %d' % obj.cannon, 50, int((WIDTH-POL_WIDTH)/4), (110+50 + obj.number*170), BLACK)


                    ### КОСТЫЛИ !!!!!!!!!!!!! 
                    elif obj.objType == ObjType.CAMERA_PTZ:
                        draw_text(screen, 'КАМЕРА', 15, obj.rect.centerx, obj.rect.top-15)
                        if obj.obj_id == 4: #камера КБЛА
                            draw_text(screen, '  КАМЕРА  ', 50, int((WIDTH-POL_WIDTH)/4), (100 + obj.number*170), BLACK, backgroundColor)
                        elif obj.obj_id == 9: #камера РТС
                            draw_text(screen, '  КАМЕРА  ', 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, (100 + obj.number*170), BLACK, backgroundColor)
                            
=======
                        draw_text(screen, 'КБЛА %d' % obj.number, 50, int((WIDTH-POL_WIDTH)/4), (50 + obj.number*170), BLACK)
                        draw_text(screen, str(obj.balls), 70, int((WIDTH-POL_WIDTH)/4), (110 + obj.number*170), BLACK)
                        
>>>>>>> origin/main
                    #подпись снизу
                    if obj.objFunc == ObjFunc.TRANSPORT:
                        if obj.cargo:
                            pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x - 5, obj.rect.y - 5, obj.rect.width + 10, obj.rect.height + 10), 2)
                            draw_text(screen, 'Загружен', 15, obj.rect.centerx, obj.rect.bottom+10)
                            
                    elif obj.objFunc == ObjFunc.CANNON:
                        draw_text(screen, 'Заряды %d' % obj.cannon , 15, obj.rect.centerx, obj.rect.bottom+10)
                        if obj.cannon > 0:
<<<<<<< HEAD
                            if obj.fire:
                                pygame.draw.circle(screen, RED, obj.rect.center, 50)
                                draw_text(screen, 'БУМ', 40, obj.rect.centerx, obj.rect.centery-20, YELLOW)
                                
                            pygame.draw.circle(screen, RED, obj.rect.center, 50, 2)
                            

                    #Перекрестье если заблокирован сервером, надпись OFFLINE
                    if obj.objType in (ObjType.ROBOT, ObjType.COPTER, ObjType.CAMERA_PTZ):
                        if obj.disqualified:
                            pygame.draw.line(screen, RED, obj.rect.topleft, obj.rect.bottomright, 4)
                            pygame.draw.line(screen, RED, obj.rect.topright, obj.rect.bottomleft, 4)

                        if obj.online == False:
                            pygame.draw.rect(screen, GRAY, (obj.rect.centerx - 40, obj.rect.centery - 10, 80, 21))
                            draw_text(screen, 'OFFLINE', 18, obj.rect.centerx, obj.rect.centery-9, RED)
=======
                            pygame.draw.circle(screen, RED, obj.rect.center, 50, 2)

                    #Перекрестье если пропали координаты, надпись OFFLINE
                    if obj.objType in (ObjType.ROBOT, ObjType.COPTER):
                        if obj.lostCoord:
                            pygame.draw.line(screen, RED, obj.rect.topleft, obj.rect.bottomright, 2)
                            pygame.draw.line(screen, RED, obj.rect.topright, obj.rect.bottomleft, 2)

                        if obj.online == False:
                            pygame.draw.rect(screen, GRAY, (obj.rect.centerx - 40, obj.rect.centery - 10, 80, 20))
                            draw_text(screen, 'OFFLINE', 20, obj.rect.centerx, obj.rect.centery-12, RED)
>>>>>>> origin/main

                    #Мигаем вертипортами
                    if obj.objType == ObjType.VERTIPORT:
                        if obj.vertiportState == VertiportState.PROD_LOADED:
                            #мигаем
                            if int(datetime.today().timestamp() % 2):
<<<<<<< HEAD
                                pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height), 9)
                            draw_text(screen, 'Продукция готова', 15, obj.rect.centerx, obj.rect.bottom+10)
                        '''
                        elif obj.vertiportState == VertiportState.PROD_READY:
                            pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height), 9)
                            draw_text(screen, 'Загрузка', 15, obj.rect.centerx, obj.rect.bottom+10)
                        '''
                    '''    
=======
                                pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x+5, obj.rect.y+5, obj.rect.width - 10, obj.rect.height - 10), 5)
                            draw_text(screen, 'Продукция готова', 15, obj.rect.centerx, obj.rect.bottom+10)
                        elif obj.vertiportState == VertiportState.PROD_READY:
                            pygame.draw.rect(screen, obj.cargoColor, (obj.rect.x+5, obj.rect.y+5, obj.rect.width - 10, obj.rect.height - 10), 5)
                            draw_text(screen, 'Загрузка', 15, obj.rect.centerx, obj.rect.bottom+10)

>>>>>>> origin/main
                    if debugMode:
                        if obj.objType in (ObjType.ROBOT, ObjType.COPTER):
                            text_surface = debugFont.render('%d [%.3f %.3f %.3f]' % (obj.number, obj.posMetr[0], obj.posMetr[1], obj.posMetr[2]), True, BLACK)
                            if obj.objType == ObjType.COPTER:
<<<<<<< HEAD
                                screen.blit(text_surface, (40, (900 + obj.number*30)))
                            elif obj.objType == ObjType.ROBOT:
                                screen.blit(text_surface, (int((WIDTH-POL_WIDTH)/2) + POL_WIDTH+40, (900 + obj.number*30)))
                    '''
                    
                    #статус игры 1 - ждем подключения, 2 - обратный отсчет, 3 - играем, 4 - закончили
                    if statusGame == 1:
                        draw_text(screen, ' ОЖИДАЕМ ПОДКЛЮЧЕНИЯ УЧАСТНИКОВ ', 50, int(WIDTH/2), int(HEIGHT/2)-25, WHITE, BLACK)
                    elif statusGame == 2:
                        draw_text(screen, gameTime, 200, int(WIDTH/2), int(HEIGHT/2)-100, WHITE, BLACK)
                    elif statusGame == 3:
                        draw_text(screen, gameTime, 80, int(WIDTH/2), 20, WHITE)
                    elif statusGame == 4:
                        draw_text(screen, ' ИГРА ОКОНЧЕНА ', 80, int(WIDTH/2), int(HEIGHT/2)-40, WHITE, BLACK)

                    
                    if oldStatusGame != statusGame:
                       oldStatusGame = statusGame
                       if statusGame == 3:
                           showTextStartTime = time.time()
                           showText = 'СТАРТ'
                           showTextDelay = 3

                    if (time.time() - showTextStartTime) < showTextDelay : #Если время на показ текста не закончилось, то показываем    
                           draw_text(screen, showText, 200, int(WIDTH/2), int(HEIGHT/2)-100, RED, BLACK)
                        

            counter += 1
            if (time.time() - start_time) > 1 : #замеряем секунду
                currentFPS = (counter / (time.time() - start_time))
                #print("FPS: %.2f" % currentFPS)
                counter = 0
                start_time = time.time()

            if debugMode:
                draw_text(screen, "FPS: %.2f" % currentFPS, 50, WIDTH/2, 110, WHITE)
=======
                                screen.blit(text_surface, (int((WIDTH-POL_WIDTH)/2) + POL_WIDTH+40, (900 + obj.number*30)))
                            elif obj.objType == ObjType.ROBOT:
                                screen.blit(text_surface, (40, (900 + obj.number*30)))

                    
>>>>>>> origin/main
                    
        finally:
            screenLock.release()
                    
        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()


    mainLoop.quit() #останавливаем MainLoop
    mainLoopThread.join() #ожидаем завершения работы потока

    pygame.quit()
