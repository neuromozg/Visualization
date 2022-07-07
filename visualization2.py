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
import time
import argparse
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

URL = 'http://10.10.1.94:31222/user?user=all'
HTTP_REUEST_TIMEOUT = 1

FileFrozenImg = 'img/frozen_img.png'
OrtoFotoplanImg = 'img/Orto1100x1100_4.jpg'

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
LIGHT_BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
GRAY = (80, 80, 80)
LINE_COLOR = (0, 80, 0)

GT_LOGISTIC = 'LOGISTIC'
GT_FIREMAN = 'FIREMAN'


def getIP():
    # cmd = 'hostname -I | cut -d\' \' -f1'
    # ip = subprocess.check_output(cmd, shell = True) #получаем IP
    res = os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n', '')  # получаем IP, удаляем \n
    return res


'''
class GameType:
    """ Тип игры """
    LOGISTIC = 0x00
    FIREMAN = 0x01
'''


class ObjType:
    """ Класс c типами объектов """
    ROBOT = 0x00
    COPTER = 0x01
    CAMERA_PTZ = 0x03
    VERTIPORT = 0x04
    START_ZONE = 0x05
    VILLAGE = 0x06
    FIRE = 0x07


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
        self.baseImg = pygame.image.load(fileImg)
        self.frozenImg = pygame.image.load(FileFrozenImg)
        self.image = self.baseImg
        self.rect = self.image.get_rect()
        # self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(int((WIDTH - POL_WIDTH) / 2) + 50, int((WIDTH - POL_WIDTH) / 2) + POL_WIDTH - 50)
        self.rect.y = random.randrange(int((HEIGHT - POL_HEIGHT) / 2) + 50,
                                       int((HEIGHT - POL_HEIGHT) / 2) + POL_HEIGHT - 50)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.cannon = 10
        self.fire = False
        self.cargo = False
        self.cargoColor = BLACK
        self.height = 0
        self.lostCoord = False
        self.vertiportState = VertiportState.EMPTY
        self.balls = 0
        self.online = False
        self.posMetr = (0, 0, 0)
        self.blocked = False
        self.disqualified = False
        self.warehouse = (0, 0, 0, 0)
        self.typeCargo = 0
        self.detected = False

    def update(self):
        if self.objType in (ObjType.ROBOT, ObjType.COPTER):
            if self.blocked:
                self.image = self.frozenImg
            else:
                self.image = self.baseImg

            self.rect.x += self.speedx
            self.rect.y += self.speedy
            if self.rect.bottom > POL_HEIGHT or self.rect.top < HEIGHT - POL_HEIGHT:
                self.speedy = -self.speedy

            if self.rect.left < (WIDTH - POL_WIDTH) / 2 or self.rect.right > (WIDTH - POL_WIDTH) / 2 + POL_WIDTH:
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
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):
        # when the update method is called, we will increment the index
        self.index += 1

        # if the index is larger than the total images
        if self.index >= len(self.images):
            # we will make the index to 0 again
            self.index = 0

        # finally we will update the image that will be displayed
        self.image = self.images[self.index]


class ScreenSaver(pygame.sprite.Sprite):
    def __init__(self, fileImg, shift=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(fileImg)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2 + shift)
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
                             '! rtph264pay config-interval=1 name=pay0 pt=96'.format(self.screen.get_width(),
                                                                                     self.screen.get_height(), self.fps)
        self._busLock = lock

    def do_create_element(self, url):
        print(self.launch_string)
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        # appsrc.set_property('block', False)
        # appsrc.set_property('is-live', True)
        # appsrc.set_property('format', 'GST_FORMAT_TIME')
        appsrc.connect('need-data', self.on_need_data)

    def ndarray_to_gst_buffer(self, array):
        """Converts numpy array to Gst.Buffer"""
        return Gst.Buffer.new_wrapped(array.tobytes())

    def on_need_data(self, src, lenght):
        self._busLock.acquire()
        try:
            numpy_frame = pygame.surfarray.array3d(self.screen)  # создаем numpy массив из экрана Pygame
        finally:
            self._busLock.release()
        numpy_frame = np.swapaxes(numpy_frame, 0, 1)  # поворачиваем оси
        buf = self.ndarray_to_gst_buffer(numpy_frame)
        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp

        retval = src.emit('push-buffer', buf)
        self.number_frames += 1
        # print(self.number_frames)
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


def draw_text(surf, text, size, x, y, color=WHITE, backgound=None):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color, backgound)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
    return text_rect

def draw_text_left(surf, text, size, x, y, color=WHITE, backgound=None):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color, backgound)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surf.blit(text_surface, text_rect)
    return text_rect



def convertMeterToPix(x, y):
    pix_x = int(x * 100)
    pix_y = int((HEIGHT - POL_HEIGHT) / 2 + POL_HEIGHT - y * 100)
    return (pix_x, pix_y)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Visualisation Kiberdrom 2022',
        description='Визуализация игрового процесса Кибердром 2022'
    )
    parser.add_argument('-t', '--type', choices=[GT_LOGISTIC, GT_FIREMAN], default=GT_LOGISTIC,
                        help='Список типов соревнований')
    args = parser.parse_args()

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Cyber Drom 2022')

    # font_name = pygame.font.match_font('arial')
    font_name = pygame.font.match_font('DejaVuSans')

    clock = pygame.time.Clock()

    screenLock = threading.Lock()  # блокировка для раздельного доступа к screen

    # GLib.threads_init()
    Gst.init(None)

    rtspServer = GstRtspServer(screen, screenLock)

    mainLoop = GLib.MainLoop()

    mainLoopThread = threading.Thread(target=mainLoop.run, daemon=True)
    mainLoopThread.start()

    all_objects = pygame.sprite.Group()

    drones = pygame.sprite.Group()
    for i in range(4):
        # drone = CyberDromObject('img/robot_img.png', i, i+1, ObjType.COPTER, ObjFunc.TRANSPORT)
        drone = CyberDromObject('img/drone.png', i, i + 1, ObjType.COPTER, ObjFunc.TRANSPORT)
        drones.add(drone)
        all_objects.add(drone)

    # стартовые позиции
    start_positions = pygame.sprite.Group()
    for i in range(4):
        start_pos = CyberDromObject('img/StartCopter%d.png' % (i + 1), i + 8, i + 1, ObjType.START_ZONE, ObjFunc.NONE)
        start_positions.add(start_pos)
        all_objects.add(start_pos)

    # фабрики с продукцией
    fabrics = pygame.sprite.Group()
    for i in range(4):
        fabric = CyberDromObject('img/vertiport.png', i, i + 1, ObjType.VERTIPORT, ObjFunc.NONE)
        fabrics.add(fabric)
        all_objects.add(fabric)

    villages = pygame.sprite.Group()
    for i in range(4):
        village = CyberDromObject('img/village.png', i + 4, i + 1, ObjType.VILLAGE, ObjFunc.NONE)
        villages.add(village)
        all_objects.add(village)

    if args.type == GT_FIREMAN:
        fires = pygame.sprite.Group()
        for i in range(10):
            fire = CyberDromObject('img/fire.png', i, i + 1, ObjType.FIRE, ObjFunc.NONE)
            fires.add(fire)
            all_objects.add(fire)

    # pepe = Pepe()
    # creating a group with our sprite
    # pepe_group = pygame.sprite.Group(pepe)

    # screenSaver = ScreenSaver('img/Homunculus_loxodontus.png')
    screenSaver = ScreenSaver('img/cyber_drom_logo.png', -50)
    screenSaver_group = pygame.sprite.Group(screenSaver)

    img_cyberdrom = pygame.image.load('img/cyber_drom_background_1.png')

    imgOrtofotoplan = pygame.image.load(OrtoFotoplanImg)

    debugMode = False
    debugFont = pygame.font.Font(font_name, 30)

    start_time = time.time()
    counter = 0

    # Цикл игры
    running = True

    oldStatusGame = 0
    showTextStartTime = time.time()
    showText = ''
    showTextDelay = 0

    print('Start')

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debugMode = not debugMode

        try:
            objectData = requests.get(URL, timeout=HTTP_REUEST_TIMEOUT)
            #objectData = requests.get(URL)

            # print(objectData)

            #data = json.loads(objectData.text)
        except:
            # print ('error')
            objectData = None

        showScreenSaver = True

        if not objectData is None:
            showScreenSaver = False

            data = json.loads(objectData.text)

            balls = data['game_status']['balls']
            gameTime = data['game_status']['time']
            statusGame = data['game_status'][
                'game_status']  # статус игры 1 - ждем подключения, 2 - обратный отсчет, 3 - играем, 4 - закончили
            teamName = data['game_status']['team_name']  # название команды

            for fabric in data['fabric']:
                x, y, _ = data['fabric'][fabric]['pos']
                try:
                    numCargo = data['fabric'][fabric]['num_cargo']
                except:
                    numCargo = 0
                try:
                    typeCargo = data['fabric'][fabric]['type_cargo']
                except:
                    typeCargo = None

                for obj in fabrics:
                    if obj.obj_id == int(fabric):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.numCargo = numCargo
                        obj.typeCargo = typeCargo
                        break

            for village in data['village']:
                x, y, _ = data['village'][village]['pos']

                try:
                    warehouse = data['village'][village]['cargo']
                except:
                    warehouse = None

                for obj in villages:
                    if obj.obj_id == int(village):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.warehouse = warehouse
                        break

            for takeoff_area in data['takeoff_area']:
                x, y, _ = data['takeoff_area'][takeoff_area]['pos']
                for obj in start_positions:
                    if obj.obj_id == int(takeoff_area):
                        obj.rect.center = convertMeterToPix(x, y)
                        break

            if args.type == GT_FIREMAN:
                for fire in data['fire']:
                    x, y, _ = data['fire'][fire]['pos']
                    detected = data['fire'][fire]['detected']

                    for obj in fires:
                        if obj.obj_id == int(fire):
                            obj.rect.center = convertMeterToPix(x, y)
                            obj.detected = detected
                            break

            for drone in data['pioneer_status']:
                # print(obj, data['user'][user]['position'])
                x, y, h = data['pioneer_status'][drone]['pos']

                try:
                    typeCargo = data['pioneer_status'][drone]['type_cargo']
                except:
                    typeCargo = None

                try:
                    cargo = data['pioneer_status'][drone]['is_cargo']
                except:
                    cargo = False

                for obj in drones:
                    if obj.obj_id == int(drone):
                        obj.rect.center = convertMeterToPix(x, y)
                        obj.typeCargo = typeCargo
                        obj.cargo = cargo
                        obj.posMetr = (x, y, h)
                        break

        screenLock.acquire()
        try:
            if showScreenSaver:
                # Держим цикл на правильной скорости
                clock.tick(FPS)

                # pepe_group.update()
                screenSaver_group.update()

                # Рендеринг
                screen.fill(WHITE)
                # pepe_group.draw(screen)
                # draw_text(screen, 'СКОРО НАЧНЕМ', 70, pepe.rect.centerx, pepe.rect.bottom + 60, BLACK)
                # zhdoon_group.draw(screen)
                # draw_text(screen, 'БОСС, СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)

                screen.blit(img_cyberdrom, (0, 0))

                screenSaver_group.draw(screen)
                # draw_text(screen, 'БОСС, СКОРО НАЧНЕМ', 70, WIDTH/2, HEIGHT - 300, BLACK)

            else:
                # Обновление координат и состояний объектов
                all_objects.update()

                # Рендеринг
                screen.fill(GRAY)

                #pygame.draw.rect(screen, BLACK, ((WIDTH-POL_WIDTH)/2, (HEIGHT-POL_HEIGHT)/2, POL_WIDTH, POL_HEIGHT))
                #screen.blit(imgOrtofotoplan, ((WIDTH - POL_WIDTH) / 2, (HEIGHT - POL_HEIGHT) / 2))
                screen.blit(imgOrtofotoplan, (0, (HEIGHT - POL_HEIGHT) / 2))

                # Результаты команд
                # draw_text(screen, 'Баллы команды', 50, int((WIDTH-POL_WIDTH)/4), 20, BLACK)
                # draw_text(screen, str(ballsPioneer), 70, int((WIDTH-POL_WIDTH)/4), 80, BLACK)

                # draw_text(screen, 'Команда РТС', 50, int((WIDTH-POL_WIDTH)/4*3) + POL_WIDTH, 20, BLACK)

                # линии сетки
                # вертикальные
                for x in range(0, POL_WIDTH+1, 100):
                    pygame.draw.line(screen, LINE_COLOR, (x, int(HEIGHT - POL_HEIGHT) / 2),
                                     (x, int(HEIGHT - POL_HEIGHT) / 2 + POL_HEIGHT), 2)
                # горизонтальные
                for y in range(int((HEIGHT - POL_HEIGHT) / 2), int((HEIGHT - POL_HEIGHT) / 2 + POL_HEIGHT), 100):
                    pygame.draw.line(screen, LINE_COLOR, (0, y),
                                     (POL_WIDTH, y), 2)

                # линии ограничения зоны полетов-заездов

                # screen.blit(background, background_rect)
                # отрисовываем все спрайты вертипортов

                if args.type == GT_LOGISTIC:
                    start_positions.draw(screen)
                    fabrics.draw(screen)
                    villages.draw(screen)
                    
                elif args.type == GT_FIREMAN:
                    fires.draw(screen)

                # отрисовка текста + графика
                for obj in all_objects:
                    # Раскрашиваем вертипорты
                    if obj.objType == ObjType.VERTIPORT:
                        if args.type == GT_LOGISTIC:
                            cargoColor = BLACK
                            if obj.typeCargo == 0:
                                cargoColor = RED
                            elif obj.typeCargo == 1:
                                cargoColor = GREEN
                            elif obj.typeCargo == 2:
                                cargoColor = BLUE
                            elif obj.typeCargo == 3:
                                cargoColor = YELLOW

                            if obj.numCargo > 0:
                                if obj.numCargo > 3:
                                    pygame.draw.circle(screen, cargoColor, obj.rect.bottomright, 20, 0)
                                if obj.numCargo > 2:
                                    pygame.draw.circle(screen, cargoColor, obj.rect.bottomleft, 20, 0)
                                if obj.numCargo > 1:
                                    pygame.draw.circle(screen, cargoColor, obj.rect.topright, 20, 0)
                                if obj.numCargo > 0:
                                    pygame.draw.circle(screen, cargoColor, obj.rect.topleft, 20, 0)

                            # pygame.draw.rect(screen, cargoColor, (obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height), 9)
                            # draw_text(screen, 'Груз: %d шт' % obj.numCargo, 15, obj.rect.centerx, obj.rect.bottom+10)

                    elif obj.objType == ObjType.FIRE:
                        if obj.detected:
                            pygame.draw.circle(screen, RED, obj.rect.center, 50, 5)

                    elif obj.objType == ObjType.VILLAGE:
                        if not obj.warehouse is None:
                            if obj.warehouse['0'] > 0:
                                pygame.draw.circle(screen, RED, obj.rect.bottomright, 20, 0)
                            if obj.warehouse['1'] > 0:
                                pygame.draw.circle(screen, GREEN, obj.rect.bottomleft, 20, 0)
                            if obj.warehouse['2'] > 0:
                                pygame.draw.circle(screen, BLUE, obj.rect.topright, 20, 0)
                            if obj.warehouse['3'] > 0:
                                pygame.draw.circle(screen, YELLOW, obj.rect.topleft, 20, 0)
                    # наименование аппарата сверху и баллы
                    elif obj.objType == ObjType.COPTER:
                        if obj.objFunc == ObjFunc.TRANSPORT:
                            if obj.cargo:
                                cargoColor = BLACK
                                if obj.typeCargo == 0:
                                    cargoColor = RED
                                elif obj.typeCargo == 1:
                                    cargoColor = GREEN
                                elif obj.typeCargo == 2:
                                    cargoColor = BLUE
                                elif obj.typeCargo == 3:
                                    cargoColor = YELLOW

                                # pygame.draw.rect(screen, cargoColor, (obj.rect.x - 5, obj.rect.y - 5, obj.rect.width + 10, obj.rect.height + 10), 3)
                                # draw_text(screen, 'Загружен', 15, obj.rect.centerx, obj.rect.bottom+10)
                                #отрисовываем груз под дроном
                                pygame.draw.circle(screen, cargoColor, (obj.rect.centerx, obj.rect.centery + 40), 20, 0)

                        draw_text(screen, 'БВС %d' % obj.number, 20, obj.rect.centerx, obj.rect.top - 20, BLACK)
                    '''    
                    if debugMode:
                        if obj.objType in (ObjType.ROBOT, ObjType.COPTER):
                            text_surface = debugFont.render('%d [%.3f %.3f %.3f]' % (obj.number, obj.posMetr[0], obj.posMetr[1], obj.posMetr[2]), True, BLACK)
                            if obj.objType == ObjType.COPTER:
                                screen.blit(text_surface, (40, (900 + obj.number*30)))
                            elif obj.objType == ObjType.ROBOT:
                                screen.blit(text_surface, (int((WIDTH-POL_WIDTH)/2) + POL_WIDTH+40, (900 + obj.number*30)))
                    '''

                drones.draw(screen)

                draw_text_left(screen, 'Кибердром 2022 1/2 финала', 50, POL_WIDTH + 20, 10, WHITE)

                if args.type == GT_LOGISTIC:
                    draw_text_left(screen, '3-я часть \"ЛОГИСТИКА\"', 50, POL_WIDTH+20, 80, WHITE)
                elif args.type == GT_FIREMAN:
                    draw_text_left(screen, '4-я часть \"АВИАПАТРУЛЬ\"', 50, POL_WIDTH+20, 80, WHITE)

                draw_text_left(screen, 'Команда', 50, POL_WIDTH+20, 280, WHITE)
                draw_text_left(screen, teamName, 50, POL_WIDTH+20, 350, WHITE)

                # статус игры 1 - ждем подключения, 2 - обратный отсчет, 3 - играем, 4 - закончили
                if statusGame == 1:
                    draw_text(screen, ' ОЖИДАЕМ СТАРТ ', 100, int(WIDTH / 2), int(HEIGHT / 2) - 50, WHITE, BLACK)
                elif statusGame == 2:
                    draw_text(screen, gameTime, 200, int(WIDTH / 2), int(HEIGHT / 2) - 100, WHITE, BLACK)
                elif statusGame == 3:
                    draw_text_left(screen, 'Баллы: %.1f' % balls, 50, POL_WIDTH + 20, 490, WHITE)
                    draw_text_left(screen, 'Время: %s' % gameTime, 50, POL_WIDTH + 20, 560, WHITE)
                elif statusGame == 4:
                    draw_text(screen, ' ИГРА ОКОНЧЕНА ', 100, int(WIDTH / 2), int(HEIGHT / 2) - 50, WHITE, BLACK)

                if oldStatusGame != statusGame:
                    oldStatusGame = statusGame
                    if statusGame == 3:
                        showTextStartTime = time.time()
                        showText = ' СТАРТ '
                        showTextDelay = 6

                if (time.time() - showTextStartTime) < showTextDelay:  # Если время на показ текста не закончилось, то показываем
                    draw_text(screen, showText, 200, int(WIDTH / 2), int(HEIGHT / 2) - 100, RED, BLACK)

            counter += 1
            if (time.time() - start_time) > 1:  # замеряем секунду
                currentFPS = (counter / (time.time() - start_time))
                # print("FPS: %.2f" % currentFPS)
                counter = 0
                start_time = time.time()

            if debugMode:
                draw_text(screen, "FPS: %.2f" % currentFPS, 50, WIDTH / 2, HEIGHT - 80, WHITE)

        finally:
            screenLock.release()

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    mainLoop.quit()  # останавливаем MainLoop
    mainLoopThread.join()  # ожидаем завершения работы потока

    pygame.quit()
