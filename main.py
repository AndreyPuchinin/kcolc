import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.transforms import Affine2D
from matplotlib.lines import Line2D
import sys
from datetime import datetime

# Загрузка изображения циферблата
try:
    dial_img = mpimg.imread('dial.bmp')
except FileNotFoundError:
    sys.exit("Ошибка: файл 'dial.png' не найден в текущей директории")

# Ввод параметров
print("Введите коэффициенты скорости относительно реальных часов:")
speed_c = float(input("Скорость циферблата за 1 минуту (0 = стоит): "))
speed_s = float(input("Скорость секундной стрелки (1 = как реальные часы): "))

# Константы
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
HOURS_PER_REV = 12

# Расчет угловых скоростей (градусы/секунду)
omega_c = speed_c * 360 / SECONDS_PER_HOUR  # Циферблат
omega_s = speed_s * 360 / SECONDS_PER_MINUTE  # Секундная стрелка
omega_m = omega_s / SECONDS_PER_MINUTE  # Минутная стрелка
omega_h = omega_m / HOURS_PER_REV  # Часовая стрелка

# Создание фигуры
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')

# Отображение циферблата
dial = ax.imshow(dial_img, extent=[-1, 1, -1, 1])

# Создание стрелок
second_hand = Line2D([0, 0], [0, 0.95], color='red', linewidth=2)
minute_hand = Line2D([0, 0], [0, 0.8], color='green', linewidth=4)
hour_hand = Line2D([0, 0], [0, 0.6], color='blue', linewidth=6)

ax.add_line(second_hand)
ax.add_line(minute_hand)
ax.add_line(hour_hand)


# Функция для расчета углов на момент времени
def calculate_angles(elapsed_seconds):
    angle_c = -omega_c * elapsed_seconds % 360  # Циферблат (вращается в обратную сторону)
    angle_s = omega_s * elapsed_seconds % 360  # Секундная стрелка
    angle_m = omega_m * elapsed_seconds % 360  # Минутная стрелка
    angle_h = omega_h * elapsed_seconds % 360  # Часовая стрелка
    return angle_c, angle_s, angle_m, angle_h


# Получаем текущее время и вычисляем "эпоху" - количество секунд с начала дня
now = datetime.now()
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
elapsed_since_midnight = (now - midnight).total_seconds()

# Вычисляем начальные углы
initial_angle_c, initial_angle_s, initial_angle_m, initial_angle_h = calculate_angles(elapsed_since_midnight)

# Устанавливаем начальное положение циферблата и стрелок
dial.set_transform(Affine2D().rotate_deg(initial_angle_c) + ax.transData)


def get_hand_coords(angle, length, dial_angle):
    rad = np.radians(angle - dial_angle)
    return [0, np.sin(rad) * length], [0, np.cos(rad) * length]


second_hand.set_data(*get_hand_coords(initial_angle_s, 0.95, initial_angle_c))
minute_hand.set_data(*get_hand_coords(initial_angle_m, 0.8, initial_angle_c))
hour_hand.set_data(*get_hand_coords(initial_angle_h, 0.6, initial_angle_c))

# Запоминаем время начала анимации
start_time = datetime.now()


def update(frame):
    # Вычисляем время, прошедшее с начала анимации
    elapsed_animation = (datetime.now() - start_time).total_seconds()
    # Общее время = время с полуночи + время анимации
    total_elapsed = elapsed_since_midnight + elapsed_animation

    # Вычисляем текущие углы
    angle_c, angle_s, angle_m, angle_h = calculate_angles(total_elapsed)

    # Обновляем положение циферблата и стрелок
    dial.set_transform(Affine2D().rotate_deg(angle_c) + ax.transData)
    second_hand.set_data(*get_hand_coords(angle_s, 0.95, angle_c))
    minute_hand.set_data(*get_hand_coords(angle_m, 0.8, angle_c))
    hour_hand.set_data(*get_hand_coords(angle_h, 0.6, angle_c))

    return [dial, second_hand, minute_hand, hour_hand]


# Запуск анимации
ani = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()