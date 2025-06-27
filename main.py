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

# Реальные скорости (градусы/секунду)
REAL_SEC_PER_HOUR = 3600
REAL_SEC_PER_MIN = 60
REAL_HOURS_PER_REV = 12

# Рассчет фактических скоростей (градусы/секунду)
omega_c = speed_c * 360 / REAL_SEC_PER_HOUR  # Циферблат
omega_s = speed_s * 360 / REAL_SEC_PER_MIN  # Секундная стрелка
omega_m = omega_s / REAL_SEC_PER_MIN  # Минутная стрелка
omega_h = omega_m / REAL_HOURS_PER_REV  # Часовая стрелка

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

# Начальное время
start_time = datetime.now()


def update(frame):
    # Реальное прошедшее время в секундах
    elapsed = (datetime.now() - start_time).total_seconds()

    # Углы поворота (в градусах)
    angle_c = -omega_c * elapsed % 360  # Циферблат
    angle_s = omega_s * elapsed % 360  # Секундная
    angle_m = omega_m * elapsed % 360  # Минутная
    angle_h = omega_h * elapsed % 360  # Часовая

    # Вращение циферблата
    dial.set_transform(Affine2D().rotate_deg(angle_c) + ax.transData)

    # Положение стрелок (учитываем вращение циферблата)
    def get_hand_coords(angle, length):
        rad = np.radians(angle - angle_c)
        return [0, np.sin(rad) * length], [0, np.cos(rad) * length]

    # Обновление стрелок
    second_hand.set_data(*get_hand_coords(angle_s, 0.95))
    minute_hand.set_data(*get_hand_coords(angle_m, 0.8))
    hour_hand.set_data(*get_hand_coords(angle_h, 0.6))

    return [dial, second_hand, minute_hand, hour_hand]


# Запуск анимации
ani = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()