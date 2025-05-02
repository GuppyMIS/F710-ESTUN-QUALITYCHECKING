from ultralytics import YOLO
import cv2
import threading
import multiprocessing
import subprocess
import pyodbc
from tkinter import *
import sys
import gc
import minimalmodbus
import serial
import datetime
import csv
import os


def task1():
    global img_array,annotated_frame, combine_all
    while (True):

        success, camera1_frame = Camera1.read()
        success2, camera2_frame = Camera2.read()
        #success3, camera3_frame = Camera3.read()
        #success4, camera4_frame = Camera4.read()

        camera1_frame = cv2.resize(camera1_frame, (0, 0), fx=float(frame_size_x), fy=float(frame_size_y))
        camera2_frame = cv2.resize(camera2_frame, (0, 0), fx=float(frame_size_x), fy=float(frame_size_y))
        #camera3_frame = cv2.resize(camera3_frame, (0, 0), fx=float(frame_size_x), fy=float(frame_size_y))
        #camera4_frame = cv2.resize(camera4_frame, (0, 0), fx=float(frame_size_x), fy=float(frame_size_y))

        #combine_camera1 = cv2.hconcat([camera1_frame, camera2_frame])
        #combine_camera2 = cv2.hconcat([camera3_frame, camera4_frame])
        combine_all = cv2.vconcat([camera1_frame, camera2_frame])

        cv2.imshow("F723-LABEL-CHECKING", combine_all)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    Camera1.release()
    Camera2.release()
    #Camera3.release()
    #Camera4.release()
    cv2.destroyAllWindows()

def task3():
    global annotated_frame, combine_all
    while(1):
        x = input()
        date_format = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S ")
        #directory_link = r'C:\Users\PC-191\PycharmProjects\F40X-QUALITY CHECKING\dataset collection\\' + date_format + ".jpg"
        directory_link = datasetcollection + date_format + ".jpg"
        cv2.imwrite(directory_link, cv2.resize(combine_all, (0, 0), fx=float(1), fy=float(1)))
        print("saved")


if __name__ == "__main__":

    try:
        gc.enable()
        global img_array, area, annotated_frame, ocr_reader,PartCheckingFinished,combine_all
        multiprocessing.freeze_support()
        annotated_frame = cv2.imread("initial_image.JPG")
        combine_all = cv2.imread("initial_image.JPG")

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
        conf_model = setting_list[3][1]
        iou_model = setting_list[4][1]
        fig_size_x = setting_list[5][1]
        fig_size_y = setting_list[6][1]
        frame_size_x = setting_list[7][1]
        frame_size_y = setting_list[8][1]
        server = setting_list[9][1]
        database = setting_list[10][1]
        table = setting_list[11][1]
        uid = setting_list[12][1]
        pwd = setting_list[13][1]
        DSN = setting_list[14][1]
        model_inference = setting_list[15][1]
        com_number = setting_list[16][1]
        com_address = setting_list[17][1]
        camera_id_1 = setting_list[18][1]
        camera_id_2 = setting_list[19][1]
        camera_id_3 = setting_list[20][1]
        camera_id_4 = setting_list[21][1]
        datasetcollection = setting_list[22][1]

        Camera1 = cv2.VideoCapture(int(camera_id_1))
        Camera2 = cv2.VideoCapture(int(camera_id_2))
        #Camera3 = cv2.VideoCapture(int(camera_id_3))
        #Camera4 = cv2.VideoCapture(int(camera_id_4))

        model = YOLO(model_inference, task='detect')

        print("I/O Module Address: " + com_number)
        print(OK_PATH)
        print(NG_PATH)

        t1 = threading.Thread(target=task1)
        t3 = threading.Thread(target=task3)


        t1.start()
        t3.start()

        t1.join()
        t3.join()

    except Exception as e:
        print(e)
        print("Something went wrong, press Enter to Exit")
        x = input()
        sys.exit(0)