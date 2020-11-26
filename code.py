import time
import os
import board
import displayio
import random
from digitalio import DigitalInOut, Pull, Direction
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer
from secrets import secrets
import openweather_graphics  # pylint: disable=wrong-import-position

# --- Constants ---
UNITS = "imperial"
LOCATION = "Saint Louis, US"
WEATHER_SOURCE = ("http://api.openweathermap.org/data/2.5/weather?q="
                  + LOCATION + "&units=" + UNITS)
WEATHER_SOURCE += "&appid=" + secrets["openweather_token"]
DATA_LOCATION = []
SCROLL_HOLD_TIME = 0
SPRITESHEET_FOLDER = "/bmps"
DEFAULT_FRAME_DURATION = 1  # 100ms
AUTO_ADVANCE_LOOPS = 3
TIMEZONE = secrets['timezone']
TWELVE_HOUR = True

# --- Display setup ---
matrix = Matrix(width=32, height=16, bit_depth=4)
sprite_group = displayio.Group(max_size=1)
network = Network(status_neopixel=board.NEOPIXEL, debug=False)
gfx = openweather_graphics.OpenWeather_Graphics(matrix.display,
                                                am_pm=True, units=UNITS)
matrix.display.show(sprite_group)

# --- Button setup ---
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

localtime_refresh = None
weather_refresh = None
auto_advance = True

file_list = sorted(
    [
        f
        for f in os.listdir(SPRITESHEET_FOLDER)
        if (f.endswith(".bmp") and not f.startswith("."))
    ]
)

current_image = None
current_frame = 0
current_loop = 1
frame_count = 0
frame_duration = DEFAULT_FRAME_DURATION

def load_image():
    """
    Load an image as a sprite
    """
    # pylint: disable=global-statement
    global current_frame, current_loop, frame_count, frame_duration
    while sprite_group:
        sprite_group.pop()

    bitmap = displayio.OnDiskBitmap(
        open(SPRITESHEET_FOLDER + "/" + file_list[current_image], "rb")
    )
    frame_count = int(bitmap.height / matrix.display.height)
    frame_duration = DEFAULT_FRAME_DURATION

    sprite = displayio.TileGrid(
        bitmap,
        pixel_shader=displayio.ColorConverter(),
        width=1,
        height=1,
        tile_width=bitmap.width,
        tile_height=matrix.display.height,
    )

    sprite_group.append(sprite)
    current_frame = 0
    current_loop = 0

def advance_image(which_image):
    """
    Advance to the next image in the list and loop back at the end
    """
    # pylint: disable=global-statement
    global current_image
    current_image = which_image
    load_image()

def advance_frame():
    """
    Advance to the next frame and loop back at the end
    """
    # pylint: disable=global-statement
    global current_frame, current_loop
    current_frame = current_frame + 1
    if current_frame >= frame_count:
        current_frame = 0
        current_loop = 1
    sprite_group[0][0] = current_frame

def hh_mm(time_struct):
    """ Given a time.struct_time, return a string as H:MM or HH:MM, either
        12- or 24-hour style depending on global TWELVE_HOUR setting.
        This is ONLY for 'clock time,' NOT for countdown time, which is
        handled separately in the one spot where it's needed.
    """
    if TWELVE_HOUR:
        if time_struct.tm_hour > 12:
            hour_string = str(time_struct.tm_hour - 12) # 13-23 -> 1-11 (pm)
        elif time_struct.tm_hour > 0:
            hour_string = str(time_struct.tm_hour) # 1-12
        else:
            hour_string = '12' # 0 -> 12 (am)
    else:
        hour_string = '{0:0>2}'.format(time_struct.tm_hour)
    return hour_string + ':' + '{0:0>2}'.format(time_struct.tm_min)

while True:
    if (not localtime_refresh) or (time.monotonic() -
                                   localtime_refresh) > 3600:
        try:
            network.get_local_time()
            localtime_refresh = time.monotonic()
            value = network.fetch_data(WEATHER_SOURCE,
                                       json_path=(DATA_LOCATION,))
            weather_refresh = time.monotonic()
        except RuntimeError as e:
            print(e)
            continue

    if (current_loop == 1):
        NOW = time.localtime()
        gfx.display_weather(value)
        time.sleep(10)
        gfx.display_time(hh_mm(NOW))
        time.sleep(10)
        gfx.display_date(str(NOW.tm_mon) + '/' + str(NOW.tm_mday))
        time.sleep(10)
        gfx.display_weather(value)
        time.sleep(10)
        gfx.display_time(hh_mm(NOW))
        time.sleep(10)
        gfx.display_date(str(NOW.tm_mon) + '/' + str(NOW.tm_mday))
        time.sleep(10)
        if (NOW.tm_mon == 1):  # Month Pictures
            which_pic = 4
        if (NOW.tm_mon == 2):
            which_pic = 3
        if (NOW.tm_mon == 3):
            which_pic = 10
        if (NOW.tm_mon == 4):
            which_pic = 0
        if (NOW.tm_mon == 5):
            which_pic = 11
        if (NOW.tm_mon == 6):
            which_pic = 6
        if (NOW.tm_mon == 7):
            which_pic = 5
        if (NOW.tm_mon == 8):
            which_pic = 1
        if (NOW.tm_mon == 9):
            which_pic = 21
        if (NOW.tm_mon == 10):
            which_pic = 15
        if (NOW.tm_mon == 11):
            which_pic = 13
        if (NOW.tm_mon == 12):
            which_pic = 2
        current_loop = 0
        random_image_control = random.randint(1,22)
        if (random_image_control == 2):
            which_pic = 7  #Kirby
        if (random_image_control == 4):
            which_pic = 8  #Koopas
        if (random_image_control == 6):
            which_pic = 9  #Link
        if (random_image_control == 8):
            which_pic = 12  #Mermaid
        if (random_image_control == 10):
            which_pic = 14  #Nyan
        if (random_image_control == 12):
            which_pic = 16  #Pac1
        if (random_image_control == 14):
            which_pic = 17  #Pac2
        if (random_image_control == 16):
            which_pic = 18  #Pac3
        if (random_image_control == 18):
            which_pic = 19  #Pac4
        if (random_image_control == 20):
            which_pic = 20  #Penny
        if (random_image_control == 22):
            which_pic = 22  #ThisIsFine
        advance_image(which_pic)
        #advance_image(15)
        matrix.display.show(sprite_group)
    if (current_loop == 0):
        advance_frame()
        time.sleep(frame_duration)