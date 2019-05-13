import serial
import pygame
# from os import getcwd
from os.path import exists
import csv
from datetime import datetime


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

    def read_data(self):
        global pressure, pressure_g
        try:
            field = str(ser.readline().strip())[2:].strip("'")
            print(field)
            pressure = round(float(str(ser.readline().strip()).strip("b'").split()[1]) / 1000, 1)
            print(pressure)
            pressure_g.append(pressure)
            if len(pressure_g) > 20:
                pressure_g.pop()

            for _ in range(4):
                data = str(ser.readline().strip()).strip("b'").split()
                print(data)
                fields[field].write_data(data[0], data[1])
        except:
            pass

    '''
    def update_graphics(self):
        g1.dotes = fields[current_field].graphics['wet_air']
        g2.dotes = fields[current_field].graphics['temp_air']
        g3.dotes = fields[current_field].graphics['wet_soil']
        g4.dotes = fields[current_field].graphics['temp_soil']
    '''


class Label:
    def __init__(self, rect, text, text_color='black', background_color='gray', additional_symbols='', name=None):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = background_color
        self.additional_symbols = additional_symbols
        self.font_color = pygame.Color(text_color)
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.bgcolor != -1:
            surface.fill(pygame.Color(self.bgcolor), self.rect)
        self.rendered_text = self.font.render(str(self.text) + self.additional_symbols, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.centerx - self.rendered_text.get_width() // 2,
                                                         centery=self.rect.centery)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def update(self):
        if self.name:
            self.text = str(fields[current_field].dates[self.name])
        else:
            return None

    def __str__(self):
        return self.__class__.__name__


class Button(Label):
    def __init__(self, rect, text, id):
        super().__init__(rect, text)
        self.pressed = False
        self.id = id

    def render(self, surface):
        if self.bgcolor != -1:
            surface.fill(pygame.Color(self.bgcolor), self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        while self.rendered_text.get_width() > self.rect.width - 5:
            self.text = self.text[:-4] + '...'
            self.rendered_text = self.font.render(self.text, 1, self.font_color)

        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.centerx - self.rendered_text.get_width() // 2,
                                                             centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.centerx - self.rendered_text.get_width() // 2
                                                             + 2, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text,
                     self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.pos[0] in range(0, 100 * 5) and \
                event.pos[1] in range(0, 30):
            self.pressed = self.rect.collidepoint(event.pos)

    def update(self):
        global current_field
        if self.pressed:
            current_field = 'Field ' + str(self.id)


class Image:
    def __init__(self, image_name, pos, angle=None):
        self.default_image = pygame.image.load(image_name)
        self.image = self.default_image
        if angle:
            self.default_angle = angle
        self.rect = pygame.rect.Rect([*pos, self.image.get_width(), self.image.get_height()])
        self.rendered_rect = None

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.default_image, self.default_angle - angle)

    def render(self, surface):
        self.rendered_rect = self.image.get_rect(x=self.rect.x, centery=self.rect.centery)
        surface.blit(self.image, self.rendered_rect)

    def get_center(self):
        self.rendered_rect = self.image.get_rect(center=self.rect.center)
        return self.rendered_rect.center


class ArrowImage(Image):
    def __init__(self, image_name, pos, angle=None, follows=None):
        super().__init__(image_name, pos, angle)
        self.follower = follows

    def rotate(self, angle):
        super().rotate(angle)
        self.rect = pygame.rect.Rect([self.follower.rect.centerx - self.image.get_width() / 2,
                                      self.follower.rect.centery - self.image.get_height() / 2,
                                      self.image.get_width(), self.image.get_height()])


class Graphic:
    def __init__(self, rect, name, color='white', min_in=0, max_in=100, add=None):
        self.add = add
        self.r_dote = 2
        self.dotes = []
        self.rect = pygame.rect.Rect(rect)
        self.name = name
        self.color = color
        self.min_in = min_in
        self.max_in = max_in
        self.min_out = self.rect.y + self.rect.height - self.r_dote
        self.max_out = self.rect.y + self.r_dote

    def render(self, surface):
        # print(self.dotes)
        pygame.draw.line(surface, pygame.Color('gray'), [self.rect.x, self.rect.y],
                         [self.rect.x + self.rect.width, self.rect.y])
        pygame.draw.line(surface, pygame.Color('gray'), [self.rect.x, self.rect.y],
                         [self.rect.x, self.rect.y + self.rect.height])
        pygame.draw.line(surface, pygame.Color('gray'), [self.rect.x, self.rect.y + self.rect.height],
                         [self.rect.x + self.rect.width, self.rect.y + self.rect.height])
        pygame.draw.line(surface, pygame.Color('gray'), [self.rect.x + self.rect.width, self.rect.y],
                         [self.rect.x + self.rect.width, self.rect.y + self.rect.height])
        for i in range(len(self.dotes)):
            pygame.draw.circle(surface, pygame.Color(self.color),
                               [i * ((self.rect.width - self.r_dote * 2) // len(self.dotes)) + self.r_dote + 1 + self.rect.x,
                                arduino_map(self.dotes[i], self.min_in, self.max_in, self.min_out, self.max_out)],
                               self.r_dote)
        for i in range(len(self.dotes) - 1):
            pygame.draw.line(surface, pygame.Color(self.color),
                             [i * ((self.rect.width - self.r_dote * 2) // len(self.dotes)) + self.r_dote + 1 + self.rect.x,
                              arduino_map(self.dotes[i], self.min_in, self.max_in, self.min_out, self.max_out)],
                             [(i + 1) * ((self.rect.width - self.r_dote * 2) // len(self.dotes)) + self.r_dote + 1 + self.rect.x,
                              arduino_map(self.dotes[i + 1], self.min_in, self.max_in, self.min_out, self.max_out)])

    def update(self):
        if not self.add:
            self.dotes = fields[current_field].graphics[self.name]
        else:
            self.dotes = pressure_g


class Field:
    def __init__(self):
        self.dates = {
            'wet_air': 0.0,
            'temp_air': 0.0,
            'wet_soil': 0.0,
            'temp_soil': 0.0
        }
        self.graphics = {
            'wet_air': [],
            'temp_air': [],
            'wet_soil': [],
            'temp_soil': []
        }

    def write_data(self, name, value):
        # print(float(value))
        # print(name)
        self.dates[name] = float(value)
        self.graphics[name].append(int(float(value)))
        if len(self.graphics[name]) > 25:
            self.graphics[name] = self.graphics[name][1:]


def update_arrows():
    wet_air_arrow.rotate(180 * (fields[current_field].dates['wet_air'] / 100))
    wet_soil_arrow.rotate(180 * (fields[current_field].dates['wet_soil'] / 100))
    '''
    t1.text = str(fields[current_field].dates['wet_air'])
    t2.text = str(fields[current_field].dates['temp_air'])
    t3.text = str(fields[current_field].dates['wet_soil'])
    t4.text = str(fields[current_field].dates['temp_soil'])

    print(t1.text)
    print(t2.text)
    print(t3.text)
    print(t4.text)
    '''


def update_pressure():
    t5.text = str(pressure)


def arduino_map(value, range_in_min, range_in_max, range_out_min, range_out_max):
    return int((value - range_in_min) * (range_out_max - range_out_min) //
               (range_in_max - range_in_min) + range_out_min)


def draw_temp(image, value):
    counted_value = arduino_map(value, -10, 40, 0, 150)
    pygame.draw.rect(screen, (227, 30, 36), [image.rendered_rect.centerx - 10, 63 + 150 - counted_value,
                                             22, counted_value + 20])


def write_csv():
    for i in range(1, 6):
        with open('logs\\' + now + '_Field' + str(i) + '.csv', 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([fields['Field ' + str(i)].dates[j] for j in dates_list] + [pressure])
    # print('write')


pygame.init()
# writer.writerow(['temp_soil', 'temp_air', 'wet_soil', 'wet_air'])

address = input('Введите порт для связи с ардуино ').split()
try:
    ser = serial.Serial(address[0], int(address[1]), timeout=0)
except Exception as e:
    print(e)
    exit()

delay = int(input('Введите задержку для считывания '))

size = width, height = 319 * 2 + 141 * 2 + 400, 850  # нижняя граница = 30 + 319 = 349
screen = pygame.display.set_mode(size)

gui = GUI()

pressure = 0
pressure_g = []

current_field = 'Field 1'
dates_list = ['wet_air', 'temp_air', 'wet_soil', 'temp_soil']

b1 = Button([0, 0, 100, 30], 'Поле 1', 1)
b2 = Button([100, 0, 100, 30], 'Поле 2', 2)
b3 = Button([200, 0, 100, 30], 'Поле 3', 3)
b4 = Button([300, 0, 100, 30], 'Поле 4', 4)
b5 = Button([400, 0, 100, 30], 'Поле 5', 5)
b1.pressed = True
gui.add_element(b1)
gui.add_element(b2)
gui.add_element(b3)
gui.add_element(b4)
gui.add_element(b5)

wet_air = Image('wet_air.png', [0, 30])
wet_soil = Image('wet_soil.png', [319 + 141, 30])
temp_air = Image('temp_air.png', [319, 30])
temp_soil = Image('temp_soil.png', [319 * 2 + 141, 30])
wet_air_arrow = ArrowImage('arrow.png', [0, 0], 90, follows=wet_air)
wet_air_arrow.rotate(0)

wet_soil_arrow = ArrowImage('arrow.png', [0, 0], 90, follows=wet_soil)
wet_soil_arrow.rotate(0)

gui.add_element(wet_air)
gui.add_element(wet_soil)
gui.add_element(temp_air)
gui.add_element(temp_soil)
gui.add_element(wet_air_arrow)
gui.add_element(wet_soil_arrow)

t1 = Label([wet_air.get_center()[0] - 30, wet_air.image.get_height() * 0.82 - 15, 60, 40], 0.0, 'blue', -1,
           additional_symbols='%', name='wet_air')
t2 = Label([temp_air.get_center()[0] - 25, temp_air.image.get_height() * 0.84 - 15, 50, 40], 0.0, 'lightblue', -1,
           name='temp_air')
t3 = Label([wet_soil.get_center()[0] - 30, wet_soil.image.get_height() * 0.82 - 15, 60, 40], 0.0, 'green', -1,
           additional_symbols='%', name='wet_soil')
t4 = Label([temp_soil.get_center()[0] - 25, temp_soil.image.get_height() * 0.84 - 15, 50, 40], 0.0, 'lightgreen', -1,
           name='temp_soil')
t5 = Label([319 * 2 + 141 * 2, 30, 400, 80], 0.0, 'white', -1, additional_symbols=' кПа')

gui.add_element(t1)
gui.add_element(t2)
gui.add_element(t3)
gui.add_element(t4)
gui.add_element(t5)

g1 = Graphic([0, 349, 319 * 2 + 141 * 2 - 1, 125], 'wet_air', 'blue', 0, 100)
g2 = Graphic([0, 349 + 125, 319 * 2 + 141 * 2 - 1, 125], 'temp_air', 'lightblue', -10, 40)
g3 = Graphic([0, 349 + 125 * 2, 319 * 2 + 141 * 2 - 1, 125], 'wet_soil', 'green', 0, 100)
g4 = Graphic([0, 349 + 125 * 3, 319 * 2 + 141 * 2 - 1, 125], 'temp_soil', 'lightgreen', -10, 40)
g5 = Graphic([319 * 2 + 141 * 2 + 1, 110, 398, 239], 'pressure', 'white', 50, 150, add=True)

gui.add_element(g1)
gui.add_element(g2)
gui.add_element(g3)
gui.add_element(g4)
gui.add_element(g5)

fields = {
    'Field 1': Field(),
    'Field 2': Field(),
    'Field 3': Field(),
    'Field 4': Field(),
    'Field 5': Field()
}

now = str(datetime.now())
now = now[:10]

for i in range(1, 6):
    if not exists('logs\\' + now + '_Field' + str(i) + '.csv'):
        with open('logs\\' + now + '_Field' + str(i) + '.csv', 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['temp_soil', 'temp_air', 'wet_soil', 'wet_air', 'pressure'])

clock = pygame.time.Clock()

read_delay = - delay - 2
running = True
while running:
    screen.fill(pygame.Color('black'))
    gui.render(screen)
    gui.update()
    update_arrows()
    update_pressure()
    draw_temp(temp_air, fields[current_field].dates['temp_air'])
    draw_temp(temp_soil, fields[current_field].dates['temp_soil'])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # передаем события пользователя GUI-элементам
        gui.get_event(event)
        # отрисовываем все GUI-элементы
    if read_delay >= delay:
        gui.read_data()
        write_csv()
        read_delay -= delay
    # обновляеем все GUI-элементы
    read_delay += clock.tick() / 1000
    pygame.display.flip()
