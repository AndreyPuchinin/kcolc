import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.transforms import Affine2D
from matplotlib.lines import Line2D
import sys
from datetime import datetime
from matplotlib.text import Text

# РАСКОММЕНТАРИТЬ для создания ехе (пробить в терминале pyinstaller --onefile main.py)
# sys.stdin = open('CONIN$', 'r')  # Для Windows


def hide_console():
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def input_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число")


# Ввод параметров
print("=== Настройки часов ===")
speed_c = input_float("Скорость циферблата (0=стоит, <0=обратное вращение): ")
speed_s = input_float("Скорость секундной стрелки (1=реальная скорость): ")

# Скрываем консоль после ввода
hide_console()

# Загрузка изображения циферблата
try:
    dial_img = mpimg.imread('dial_reverse.bmp' if speed_s < 0 else 'dial.bmp')
except FileNotFoundError:
    sys.exit("Ошибка: файл циферблата (dial.bmp или dial_reverse.bmp) не найден")

# Константы
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
HOURS_PER_REV = 12

# Расчёт угловых скоростей
omega_c = (abs(speed_c) * 360 / SECONDS_PER_HOUR) * (-1 if speed_c < 0 else 1)
omega_s = speed_s * 360 / SECONDS_PER_MINUTE
omega_m = omega_s / SECONDS_PER_MINUTE
omega_h = omega_m / HOURS_PER_REV

# Создание фигуры
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')
plt.title(f"Часы (скорость циферблата: {speed_c}x, скорость секундной стрелки:{speed_s}x)", pad=20)

# Отображение циферблата
dial = ax.imshow(dial_img, extent=[-1, 1, -1, 1])

# Создание укороченных стрелок
second_hand = Line2D([0, 0], [0, 0.7], color='red', linewidth=1.5)
minute_hand = Line2D([0, 0], [0, 0.6], color='green', linewidth=3)
hour_hand = Line2D([0, 0], [0, 0.4], color='blue', linewidth=4.5)

for hand in [second_hand, minute_hand, hour_hand]:
    ax.add_line(hand)

# Список для хранения объектов текста
number_texts = []


# Добавление статичных цифр (1-12) с правильным поворотом
def add_static_numbers(ax, reverse=False):
    radius = 0.85  # Радиус расположения цифр
    for hour in range(1, 13):
        angle = np.radians(90 + hour * 30) if not reverse else np.radians(90 + hour * 30)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Угол поворота текста (в градусах)
        text_angle = (hour * 30) % 360
        if reverse:
            text_angle = (-hour * 30) % 360

        color = 'red' if hour == 12 else 'black'
        # Создаем текст с поворотом и сохраняем в список
        t = ax.text(x, y, str(hour), color=color, ha='center', va='center',
                    fontsize=14, fontweight='bold', rotation=text_angle)
        number_texts.append(t)


# Добавляем цифры в зависимости от направления вращения
add_static_numbers(ax, reverse=speed_c < 0)

# Поднимаем цифры на передний план
for text in number_texts:
    text.set_zorder(10)

# Инициализация времени
now = datetime.now()
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
elapsed = (now - midnight).total_seconds()


def calculate_angles(t):
    return (
        -omega_c * t % 360,
        omega_s * t % 360,
        omega_m * t % 360,
        omega_h * t % 360
    )


def get_hand_coords(angle, dial_angle, length):
    rad = np.radians(angle - dial_angle)
    return [0, np.sin(rad) * length], [0, np.cos(rad) * length]


# Установка начального положения
angle_c, angle_s, angle_m, angle_h = calculate_angles(elapsed)
dial.set_transform(Affine2D().rotate_deg(angle_c) + ax.transData)

second_hand.set_data(*get_hand_coords(angle_s, angle_c, 0.7))
minute_hand.set_data(*get_hand_coords(angle_m, angle_c, 0.6))
hour_hand.set_data(*get_hand_coords(angle_h, angle_c, 0.4))

# Анимация
start_time = datetime.now()


def update(frame):
    current_time = elapsed + (datetime.now() - start_time).total_seconds()
    angle_c, angle_s, angle_m, angle_h = calculate_angles(current_time)

    dial.set_transform(Affine2D().rotate_deg(angle_c) + ax.transData)
    second_hand.set_data(*get_hand_coords(angle_s, angle_c, 0.7))
    minute_hand.set_data(*get_hand_coords(angle_m, angle_c, 0.6))
    hour_hand.set_data(*get_hand_coords(angle_h, angle_c, 0.4))

    return [dial, second_hand, minute_hand, hour_hand] + number_texts


# Запуск
ani = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)
plt.tight_layout()
plt.show()