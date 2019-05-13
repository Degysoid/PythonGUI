import serial
import time


address = input('Введите порт для связи с ардуино ').split()
try:
    ser = serial.Serial(address[0], int(address[1]), timeout=0)
except Exception as e:
    print(e)
    exit()


while True:
    data = str(ser.readline().strip()).strip("b'").split()
    print(data)
    time.sleep(1)
