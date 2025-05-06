from ultralytics import YOLO
import cv2
import threading
import csv
import sys
import gc
import multiprocessing
import subprocess
import os
import pandas as pd
from tkinter import *

def part_configuration_selector(unit_type):
    global df
    part_configuration_list_buffer = []
    part_configuration_list_buffer.clear()
    row_count = 0

    match unit_type:
        case "AA2JF":
            df = pd.read_csv('masking_coordinate_AA2JF.csv')
            print("masking_coordinate_AA2JF")
        case "ADXJF":
            df = pd.read_csv('masking_coordinate_ADXJF.csv')
            print("masking_coordinate_ADXJF")
        case "CUSTOM":
            df = pd.read_csv('masking_coordinate_CUSTOM.csv')
            print("masking_coordinate_CUSTOM")



def click_event(event, x, y, flags, params):
    global annotated_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'({x},{y})')
        cv2.putText(annotated_frame, f'({x},{y})', (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.circle(annotated_frame, (x, y), 3, (0, 255, 255), -1)

def task1():
    global img_array,annotated_frame, cls_detected,dict,cls_conf,for_barcode,area_variable,df
    while (1):
        success, frame_get_temp = cap.read()
        annotated_frame = frame_get_temp
        frame_resize = frame_get_temp
        frame_1 = cv2.rectangle(frame_resize, (df.iloc[int(area_variable)-1]['Startpoint1_X'], df.iloc[int(area_variable)-1]['Startpoint1_Y']),
                                (df.iloc[int(area_variable)-1]['Endpoint1_X'], df.iloc[int(area_variable)-1]['Endpoint1_Y']), (0, 0, 0), -1)
        frame_2 = cv2.rectangle(frame_1, (df.iloc[int(area_variable)-1]['Startpoint2_X'], df.iloc[int(area_variable)-1]['Startpoint2_Y']),
                                (df.iloc[int(area_variable)-1]['Endpoint2_X'], df.iloc[int(area_variable)-1]['Endpoint2_Y']), (0, 0, 0), -1)
        frame = cv2.rectangle(frame_2, (df.iloc[int(area_variable)-1]['Startpoint3_X'], df.iloc[int(area_variable)-1]['Startpoint3_Y']),
                                (df.iloc[int(area_variable)-1]['Endpoint3_X'], df.iloc[int(area_variable)-1]['Endpoint3_Y']), (0, 0, 0), -1)
        frame_copy = frame.copy()
        results = model(frame, conf=float(conf_model), iou=float(iou_model), show_conf=False, verbose=False,task='detect')
        annotated_frame = results[0].plot()
        for r in results:
             dict = r.names
             cls_detected = r.boxes.cls.tolist()
             cls_conf = r.boxes.conf.tolist()
        cv2.imshow("Point Coordinates", annotated_frame)
        cv2.setMouseCallback('Point Coordinates', click_event)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    #cap.release()
    #cv2.destroyAllWindows()

def task2():
    global area_variable
    while(1):
        input_keyin = input()
        if (input_keyin.isnumeric() and int(input_keyin)<=40):
            area_variable = input_keyin
        else:
            print("Something Wrong!")

def task3():
    global TextBox_ID, CheckBox_ID, TextBox_Note
    global win

    win = Tk()
    # Set the geometry of Tkinter frame
    win.title("Barcode Scanner")
    win.geometry("760x200")

    # Define Function to print the input value
    def display_input():
        global checkbox_status, button_status, PartChecking1, PartChecking2, PartChecking3, PartQuantity1, PartQuantity2, PartQuantity3
        PartChecking1 = []
        PartChecking2 = []
        PartChecking3 = []
        PartQuantity1 = []
        PartQuantity2 = []
        PartQuantity3 = []
        checkbox_status = var1.get()
        button_status = var2.get()
        print("Part Configuration: " + button_status)
        dataframe = part_configuration_selector(button_status)


    var1 = IntVar()
    var2 = StringVar()
    Check1 = Checkbutton(win, text="SCAN BARCODE?", variable=var1, onvalue=1, offvalue=0, command=display_input,
                         justify=LEFT, bd=5, font='Helvetica 12 bold')
    Label1 = Label(win, text="Barcode Scanner: ", font='Helvetica 12 bold')
    Label2 = Label(win, text="Note: ", font='Helvetica 12 bold')

    TextBox_ID = Text(win, height=2, width=40, bg="light yellow")
    TextBox_Note = Text(win, height=1, width=10, bg="light yellow")

    radio_button1 = Radiobutton(win, text="AA2JF", variable=var2, value="AA2JF", indicator=2, background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    radio_button2 = Radiobutton(win, text="ADXJF", variable=var2, value="ADXJF", indicator=2, background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    radio_button3 = Radiobutton(win, text="CUSTOM", variable=var2, value="CUSTOM", indicator=2, background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    Label1.grid(row=1, column=1, sticky=W, pady=2)
    Label2.grid(row=2, column=1, sticky=W, pady=2)
    TextBox_ID.grid(row=1, column=2, sticky=W, pady=2)
    TextBox_Note.grid(row=2, column=2, sticky=W, pady=2)

    radio_button1.grid(row=1, column=3, sticky=W, pady=2)
    radio_button2.grid(row=2, column=3, sticky=W, pady=2)
    radio_button3.grid(row=3, column=3, sticky=W, pady=2)


    Check1.grid(row=1, column=4, sticky=W, pady=2)

    Check1.select()
    # radio_button1.select()
    # TextBox_ID.pack()
    # t1.pack()

    win.mainloop()

if __name__ == "__main__":

    try:
        gc.enable()
        global img_array, area, annotated_frame, ocr_reader,PartCheckingFinished
        multiprocessing.freeze_support()

        proc = subprocess.Popen(os.getcwd() + r'\runInf.bat',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.PIPE,
                                cwd=os.getcwd(),
                                env=os.environ)
        proc.stdin.close()

        setting_list = []
        with open('setting.csv', 'r') as file:
            reader = csv.reader(file, skipinitialspace=True, quoting=csv.QUOTE_NONE)
            for row in reader:
                setting_list.append(row)

        OK_PATH = setting_list[1][1]
        NG_PATH = setting_list[2][1]
        APP_PATH = setting_list[3][1]
        conf_model = setting_list[4][1]
        conf_model2 = setting_list[5][1]
        iou_model = setting_list[6][1]
        iou_model2 = setting_list[7][1]
        fig_size_x = setting_list[8][1]
        fig_size_y = setting_list[9][1]
        frame_size_x = setting_list[10][1]
        frame_size_y = setting_list[11][1]
        server = setting_list[12][1]
        database = setting_list[13][1]
        table = setting_list[14][1]
        uid = setting_list[15][1]
        pwd = setting_list[16][1]
        DSN = setting_list[17][1]
        model_inference = setting_list[18][1]
        model2_inference = setting_list[19][1]
        tcp_client = setting_list[20][1]
        tcp_port = setting_list[21][1]
        camera_id = setting_list[22][1]
        DATASET_PATH = setting_list[23][1]
        dataset_colection = 0
        scan_barcode = setting_list[25][1]
        subplotx = setting_list[26][1]
        subploty = setting_list[27][1]
        imgmasking = setting_list[28][1]
        delay_variable = setting_list[29][1]
        camera_API = setting_list[30][1]
        area_variable = setting_list[31][1]
        station = "Estun robot"

        model = YOLO(model_inference,task = 'detect')
        cap = cv2.VideoCapture(int(camera_id))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(frame_size_x))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(frame_size_y))

        t1 = threading.Thread(target=task1)
        t2 = threading.Thread(target=task2)
        t3 = threading.Thread(target=task3)

        df = pd.read_csv('masking_coordinate_AA2JF.csv')
        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()


    except Exception as e:
        print(e)
        print("Something went wrong, press Enter to Exit")
        x = input()
        sys.exit(0)
