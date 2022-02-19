import colorsys
import json
from statistics import mode
import threading
import time

import dearpygui.dearpygui as dpg
import easygui
from vector3d.vector import Vector

# Possibly worst code ever sorry :(


leds = []
led_start1 = Vector()
led_end1 = Vector()
led_start2 = Vector()
led_end2 = Vector()
use_hsv = False
led_count = 30

led_count_id = 0
color_1_start_id = 0
color_2_start_id = 0

color_1_end_id = 0
color_2_end_id = 0
mode_id = 0

frame = 0


def rgb_to_hsv(v):
    color_tuple = (v.x, v.y, v.z)
    hsv = colorsys.rgb_to_hsv(*color_tuple)
    return Vector(hsv[0], hsv[1], hsv[2])


def hsv_to_rgb(v):
    color_tuple = (v.x, v.y, v.z)
    hsv = colorsys.hsv_to_rgb(*color_tuple)
    return Vector(hsv[0], hsv[1], hsv[2])


def get_led_color(index, count, frm):
    l_start1 = rgb_to_hsv(led_start1) if use_hsv else led_start1
    l_end1 = rgb_to_hsv(led_end1) if use_hsv else led_end1

    l_start2 = rgb_to_hsv(led_start2) if use_hsv else led_start2
    l_end2 = rgb_to_hsv(led_end2) if use_hsv else led_end2

    color1 = ((l_end1 - l_start1) * (1/count)) * index + l_start1
    color2 = ((l_end2 - l_start2) * (1/count)) * index + l_start2

    if frame < 16:
        color = ((color2 - color1) * (1/16)) * frm + color1
    else:
        color = ((color1 - color2) * (1/16)) * ((frm - 16)) + color2

    return hsv_to_rgb(color) if use_hsv else color


def set_leds():
    for i, led in enumerate(leds):
        color = get_led_color(i, len(leds), frame)
        dpg.set_value(led, [color.x*255, color.y*255, color.z*255])


def set_start_led1(id, value):
    global led_start1
    led_start1 = Vector(value[0], value[1], value[2])


def set_end_led1(id, value):
    global led_end1
    led_end1 = Vector(value[0], value[1], value[2])


def set_start_led2(id, value):
    global led_start2
    led_start2 = Vector(value[0], value[1], value[2])


def set_end_led2(id, value):
    global led_end2
    led_end2 = Vector(value[0], value[1], value[2])


def set_led_mode(id, value):
    global use_hsv
    use_hsv = value == 'HSV'


def set_led_count(id, value):
    global led_count
    led_count = value


def save_animation():
    out_file = easygui.filesavebox(
        default='animations/*.json', filetypes=['*.json', '*.*'])

    out_frames = []
    for j in range(32):
        out_colors = []
        for i in range(led_count):
            color = get_led_color(i, led_count, j)
            out_colors.append([color.x, color.y, color.z])
        out_frames.append(out_colors)

    colors = {
        'start1': [led_start1.x, led_start1.y, led_start1.z],
        'end1': [led_end1.x, led_end1.y, led_end1.z],
        'start2': [led_start2.x, led_start2.y, led_start2.z],
        'end2': [led_end2.x, led_end2.y, led_end2.z],
    }
    out_dict = {'frames': out_frames, 'hsv': use_hsv,
                'leds': led_count, 'colors': colors}

    if out_file is not None:
        with open(out_file, 'w') as fp:
            fp.write(json.dumps(out_dict, indent=2))


def mul_list(l, amount):
    return [l[0]*amount, l[1]*amount, l[2]*amount]


def load_animation():
    global led_count, led_start1, led_start2, led_end1, led_end2, use_hsv
    in_file = easygui.fileopenbox(
        default='animations/*.json', filetypes=['*.json', '*.*'])
    if in_file is not None:
        with open(in_file, 'r') as fp:
            in_dict = json.loads(fp.read())

        led_count = in_dict['leds']
        led_start1 = Vector(in_dict['colors']['start1'][0],
                            in_dict['colors']['start1'][1], in_dict['colors']['start1'][2])
        led_start2 = Vector(in_dict['colors']['start2'][0],
                            in_dict['colors']['start2'][1], in_dict['colors']['start2'][2])
        led_end1 = Vector(in_dict['colors']['end1'][0],
                          in_dict['colors']['end1'][1], in_dict['colors']['end1'][2])
        led_end2 = Vector(in_dict['colors']['end2'][0],
                          in_dict['colors']['end2'][1], in_dict['colors']['end2'][2])
        use_hsv = in_dict['hsv']

        dpg.set_value(led_count_id, led_count)
        dpg.set_value(color_1_start_id, mul_list(
            in_dict['colors']['start1'], 255))
        dpg.set_value(color_2_start_id, mul_list(
            in_dict['colors']['start2'], 255))
        dpg.set_value(color_1_end_id, mul_list(
            in_dict['colors']['end1'], 255))
        dpg.set_value(color_2_end_id, mul_list(
            in_dict['colors']['end2'], 255))
        dpg.set_value(mode_id, 'HSV' if use_hsv else 'RGB')


def animate():
    global frame
    while True:
        set_leds()
        frame = (frame + 1) % 32
        time.sleep(0.05)


anim_thread = threading.Thread(target=animate)
anim_thread.start()


def main():
    global led_count_id, color_1_end_id, color_1_start_id, color_2_end_id, color_2_start_id, mode_id
    dpg.create_context()
    dpg.create_viewport(title='LED Animation Tool')
    dpg.setup_dearpygui()

    with dpg.font_registry():
        default_font = dpg.add_font("open-sans.ttf", 16)
        dpg.bind_font(default_font)

    with dpg.window(label="Animation", width=300):
        led_count_id = dpg.add_input_int(label="LED Count", min_value=0,
                                         max_value=255, default_value=30, callback=set_led_count)
        color_1_start_id = dpg.add_color_edit(label="Start LED 1", no_alpha=True,
                                              callback=set_start_led1)
        color_1_end_id = dpg.add_color_edit(label="End LED 1", no_alpha=True,
                                            callback=set_end_led1)

        color_2_start_id = dpg.add_color_edit(label="Start LED 2", no_alpha=True,
                                              callback=set_start_led2)
        color_2_end_id = dpg.add_color_edit(label="End LED 2", no_alpha=True,
                                            callback=set_end_led2)
        mode_id = dpg.add_listbox(label="Mode", items=[
            "RGB", "HSV"], callback=set_led_mode)

    with dpg.window(label="Preview", pos=(400, 0)):
        for i in range(16):
            leds.append(dpg.add_color_button())

    with dpg.window(label="File", pos=(0, 300)):
        dpg.add_button(label="Save", callback=save_animation)
        dpg.add_button(label="Load", callback=load_animation)

    with dpg.theme() as global_theme:

        with dpg.theme_component(dpg.mvAll):

            # Text Color
            dpg.add_theme_color(dpg.mvThemeCol_Text,
                                (0xe4, 0xe6, 0xeb), category=dpg.mvThemeCat_Core)

            # Title Background
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,
                                (0x04, 0x2b, 0x8e), category=dpg.mvThemeCat_Core)
            # Title Active
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,
                                (0x1a, 0x46, 0xe4), category=dpg.mvThemeCat_Core)

            # Frame Color
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,
                                (0x0a, 0x0a, 0x10), category=dpg.mvThemeCat_Core)
            # Window Background
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,
                                (0x24, 0x25, 0x26), category=dpg.mvThemeCat_Core)

            # Rounding
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,
                                2, category=dpg.mvThemeCat_Core)

    dpg.bind_theme(global_theme)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()
