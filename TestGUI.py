import serial
import pygame
from os import getcwd
from os.path import exists
import csv
from datetime import datetime
from random import random


def connect_serial_port(address):
    global error, ser
    try:
        ser = None
        ser = serial.Serial(*address, timeout=0)
        error = [False, '']
    except Exception as e:
        ser = None
        error = [True, address[0]]
        print(e)
    print(error)


def read_data():
    for i in range(4):
        x = ser.readline().strip().split()
        if not x:
            continue
        Dates[str(x[0])[1:].strip("'")]['value'] = float(str(x[1])[1:].strip("'"))
    writer.writerow([i['value'] for i in Dates.values()])
    for i in Dates.keys():
        shift = button1.frame_size[1] + images[0].get_height() + frame
        if i == 'temp_soil':
            Graphics_positions[i].append(arduino_map(Dates[i]['value'], -10, 40, shift + 89, shift + 8))
        elif i == 'temp_air':
            shift += 93
            Graphics_positions[i].append(arduino_map(Dates[i]['value'], -10, 40, shift + 88, shift + 3))
        elif i == 'wet_soil':
            shift += 93 * 2
            Graphics_positions[i].append(arduino_map(Dates[i]['value'], 0, 100, shift + 87, shift + 2))
        else:
            shift += 93 * 3
            Graphics_positions[i].append(arduino_map(Dates[i]['value'], 0, 100, shift + 88, shift + 1))

        if len(Graphics_positions[i]) > 30:
            Graphics_positions[i].pop(0)


def reset():
    global Dates
    Dates = {
        'wet_soil': {'value': 0, 'color': pygame.Color('blue')},
        'temp_soil': {'value': 0, 'color': pygame.Color('green')},
        'wet_air': {'value': 0, 'color': pygame.Color('cyan')},
        'temp_air': {'value': 0, 'color': pygame.Color('purple')}
    }


def draw_base_images():
    global font_object
    shift = 0

    for i in range(len(images)):
        screen.blit(images[i], [shift, 35])
        string = None
        shape = None
        if i == 0:
            shape = pygame.transform.rotate(wet_arrow_soil_image, (0.01 * Dates['wet_soil']['value']) * (-180))
            string = str(int(Dates['wet_soil']['value'])) + '%'
            color = Dates['wet_soil']['color']
        elif i == 1:
            string = str(Dates['temp_soil']['value'])
            color = Dates['temp_soil']['color']
        elif i == 2:
            shape = pygame.transform.rotate(wet_arrow_air_image, (0.01 * Dates['wet_air']['value']) * (-180))
            string = str(int(Dates['wet_air']['value'])) + '%'
            color = Dates['wet_air']['color']
        elif i == 3:
            string = str(Dates['temp_air']['value'])
            color = Dates['temp_air']['color']

        if string:
            if i == 1 or i == 3:
                temp_shift = 5
            else:
                temp_shift = 0
            text = font_object.render(string, True, color)
            screen.blit(text, [shift + images[i].get_width() // 2 - text.get_width() // 2,
                               images[i].get_height() * 0.85 - text.get_height() // 2 + temp_shift])
        if shape:
            screen.blit(shape, [images[0].get_width() // 2 - shape.get_width() // 2 +
                                shift, images[0].get_height() // 2 -
                                shape.get_height() // 2 + button1.frame_size[1]])
        shift += images[i].get_width()

    pygame.draw.rect(screen, pygame.Color('gray'), (frame // 2 - 1, images[0].get_height() + (frame // 2 - 1) + 35,
                                                    width - (frame - 1),
                                                    height - images[0].get_width() - (frame - 1) - 35), frame)

    whitespace = (screen.get_height() - frame * 2 - images[0].get_height() - button1.frame_size[1]) // 4
    shift = button1.frame_size[1] + images[0].get_height() + frame
    for i in range(1, 4):
        pygame.draw.line(screen, pygame.Color('gray'),
                         [frame, shift + whitespace * i],
                         [screen.get_width() - frame, shift + whitespace * i])


def arduino_map(value, range_in_min, range_in_max, range_out_min, range_out_max):
    return int(
        (value - range_in_min) * (range_out_max - range_out_min) // (range_in_max - range_in_min) + range_out_min)


def draw_graphics():
    r_dote = 2

    keys = list(Graphics_positions.keys())
    for i in range(4):
        try:
            dist = (screen.get_width() - frame * 2) // len(Graphics_positions[keys[i]])
        except:
            dist = 0
        for j in range(len(Graphics_positions[keys[i]])):
            color = Dates[keys[i]]['color']
            pygame.draw.circle(screen, color, [frame + r_dote + dist * j, Graphics_positions[keys[i]][j]], r_dote)
        for p in range(1, len(Graphics_positions[keys[i]][1:]) + 1):
            pygame.draw.line(screen, color, [frame + r_dote + dist * (p - 1), Graphics_positions[keys[i]][p - 1]],
                             [frame + r_dote + dist * p, Graphics_positions[keys[i]][p]], 1)


class Button:
    def __init__(self, __cords, __text, __status, __address):
        self.status = __status
        self.text = __text
        self.font_object = pygame.font.Font(None, 15)
        self.frame = 5
        self.frame_size = 50, 30
        self.cords = self.x, self.y = __cords
        self.size = self.width, self.height = 50 - self.frame * 2, 30 - self.frame * 2
        if self.status == 0:
            self.text_color = pygame.Color('black')
            self.text_object = self.font_object.render(self.text, True, self.text_color)
            self.color = pygame.Color('gray')
        else:
            self.text_color = pygame.Color('white')
            self.text_object = self.font_object.render(self.text, True, self.text_color)
            self.color = pygame.Color('black')
        self.text_width, self.text_height = self.font_object.size(self.text)
        self.address = __address

    def draw(self):
        pygame.draw.rect(screen, pygame.Color('green'), [self.x + self.frame // 2, self.y + self.frame // 2,
                                                         *self.frame_size], self.frame)
        pygame.draw.rect(screen, self.color, [self.x + int(self.frame * 1.5),
                                              self.y + int(self.frame * 1.5), *self.size])
        screen.blit(self.text_object, [self.x + self.width // 2 - self.text_width // 2 + int(self.frame * 1.5),
                                       self.y + self.height // 2 - self.text_height // 2 + int(self.frame * 1.5)])

    def on_click(self):
        if self.status == 0:
            for i in buttons:
                if i.status == 1:
                    i.status = 0
                    i.text_color = pygame.Color('black')
                    i.text_object = i.font_object.render(i.text, True, i.text_color)
                    i.color = pygame.Color('gray')
                    break

            self.status = 1
            self.color = pygame.Color('black')
            self.text_color = pygame.Color('white')
            self.text_object = self.font_object.render(self.text, True, self.text_color)
            reset()
        connect_serial_port(self.address)

    def clicked(self, __mouse_pos):
        return __mouse_pos[0] in range(self.cords[0] + self.frame, self.cords[0] + self.width + self.frame + 1) and \
               __mouse_pos[1] in range(self.cords[1] + self.frame, self.cords[1] + self.height + self.frame + 1)


reset()

Graphics_positions = {
    'wet_soil': [],
    'temp_soil': [],
    'wet_air': [],
    'temp_air': []
}

pygame.init()
font_object = pygame.font.Font(None, 40)

button1 = Button([0, 0], 'Поле 1', 1, ['COM4', 9600])
button2 = Button([60, 0], 'Поле 2', 0, ['COM1', 9600])
button3 = Button([120, 0], 'Поле 3', 0, ['COM2', 9600])
button4 = Button([180, 0], 'Поле 4', 0, ['COM3', 9600])
button5 = Button([240, 0], 'Поле 5', 0, ['COM5', 9600])
buttons = [button1, button2, button3, button4, button5]

connect_serial_port(button1.address)

wet_arrow_soil_image = pygame.transform.rotate(pygame.image.load('СТРЕЛКА1.png'), 90)
wet_arrow_air_image = pygame.transform.rotate(pygame.image.load('СТРЕЛКА1.png'), 90)
wet_soil_image = pygame.image.load('ВЛАЖН_почва1.png')
wet_air_image = pygame.image.load('ВЛАЖН_1.png')
temp_soil_image = pygame.image.load('градусник_почва1.png')
temp_air_image = pygame.image.load('градусник1.png')
# arrow_width = wet_arrow_image.get_width()

images = [wet_soil_image, temp_soil_image, wet_air_image, temp_air_image]

frame = 20

width = sum([i.get_width() for i in images])
height = max([i.get_height() for i in images]) + 400 + frame * 2

size = width, height  # [int(i) for i in input('Введите ширину и высоту окна через пробел ').split()]
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

now = str(datetime.now())
now = now[:10]
open(getcwd() + '\\' + now + '.csv', 'a', encoding='utf-8').close()
csvfile = open(now + '.csv', 'a', encoding='utf-8')
writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
if not exists(now + '.csv'):
    writer.writerow(['temp_soil', 'temp_air', 'wet_soil', 'wet_air'])

read_delay = 0
running = True
while running:
    screen.fill(pygame.Color('black'))

    for button in buttons:
        button.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.clicked(event.pos):
                    button.on_click()

    if not error[0]:
        if read_delay >= 1:
            read_data()
            read_delay -= 1
        '''
        for i in Dates.keys():
            # print(Dates[i])
            text = font_object.render(Dates[i]['text'] + str(Dates[i]['value']), True, pygame.Color('white'))
            screen.blit(text, Dates[i]['pos'])

        pygame.draw.rect(screen, )
        '''
        draw_base_images()
        draw_graphics()

        read_delay += clock.tick() / 1000
    else:
        string = "##### There's no Arduino on " + error[1] + " #####"
        text = font_object.render(string, True, pygame.Color('white'))
        screen.blit(text,
                    [width // 2 - font_object.size(string)[0] // 2, height // 2 - font_object.size(string)[1] // 2])

    pygame.display.flip()

pygame.quit()
csvfile.close()
