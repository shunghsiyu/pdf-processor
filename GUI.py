# -*- coding: utf-8 -*-

import Tkinter as tk
import logging
import tkFileDialog
import tkMessageBox

log = logging.getLogger(__name__)

store = {}


def gui_setup():
    def run():
        main_config = ['-r', rotation_var.get(), '-d', '-e', '-m', '-f', str(threshold_scale.get() / 100), '-v',
                       store.get('input', '')]
        log.info('Process PDF with config %s', repr(main_config))
        Main.main(main_config)
        tkMessageBox.showinfo(message=u'分頁成功')

    def choose_input():
        input_dir = tkFileDialog.askdirectory(parent=root, mustexist=True)
        log.info('Choose %s as input directory.', input_dir)
        input_dir_label.config(text=input_dir)
        store['input'] = input_dir

    root = tk.Tk()

    frame_rotation = tk.Frame(root)
    frame_rotation.pack(side=tk.TOP)
    rotation_label = tk.Label(frame_rotation, text=u'旋轉方向')
    rotation_label.pack(side=tk.LEFT)
    rotation_var = tk.StringVar()
    rotation_var.set('cw')
    tk.Radiobutton(frame_rotation, text=u'順時針', variable=rotation_var, value='cw').pack(side=tk.LEFT)
    tk.Radiobutton(frame_rotation, text=u'逆時針', variable=rotation_var, value='ccw').pack(side=tk.LEFT)
    tk.Radiobutton(frame_rotation, text=u'不旋轉', variable=rotation_var, value='no-op').pack(side=tk.LEFT)

    frame_threshold = tk.Frame(root)
    frame_threshold.pack(side=tk.TOP)
    blank_page_threshold_label = tk.Label(frame_threshold, text=u'空白頁偵測')
    blank_page_threshold_label.pack(side=tk.LEFT)
    threshold_scale = tk.Scale(frame_threshold, orient=tk.HORIZONTAL, resolution=0.1, sliderlength=15, length=600)
    threshold_scale.set(2)
    threshold_scale.pack(side=tk.LEFT)

    frame_input = tk.Frame(root)
    frame_input.pack(side=tk.TOP)
    input_label = tk.Label(frame_input, text=u'輸入資料夾')
    input_label.pack(side=tk.LEFT)
    input_dir_label = tk.Label(frame_input, wraplength=600)
    input_dir_label.pack(side=tk.TOP)
    choose_input_button = tk.Button(frame_input, text=u'選擇輸入資料夾', command=choose_input)
    choose_input_button.pack(side=tk.TOP)

    start_button = tk.Button(root, text=u'開始', command=run)
    start_button.pack(side=tk.BOTTOM)

    return root


def gui_main():
    gui_setup().mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    gui_main()
    logging.shutdown()
