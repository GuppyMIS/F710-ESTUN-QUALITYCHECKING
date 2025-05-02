import time
import csv
from ultralytics import YOLO
import cv2
import threading
from pymodbus.client import ModbusTcpClient
import matplotlib
import matplotlib.pyplot as plt
import datetime
import warnings
import multiprocessing
import subprocess
import os
import pyodbc
from tkinter import *
import sys
import gc
import pandas as pd

matplotlib.use('Agg')
warnings.filterwarnings("ignore")


def process_frame(check1, check2, check3, count1, count2, count3):
    global annotated_frame, cls_detected, dict, cls_conf, cls_list, ng_string_total
    ng_string_1 = ""
    ng_string_2 = ""
    ng_string_3 = ""
    ng_string_total = []
    cls_list = []
    results = model(frame, conf=float(conf_model), iou=float(iou_model), show_conf=False, verbose=False, task='detect')
    annotated_frame = results[0].plot(conf=False)
    for r in results:
        dict = r.names
        cls_detected = r.boxes.cls.tolist()
        cls_conf = r.boxes.conf.tolist()
    for xy in range(len(cls_detected)):
        cls_list.append(dict.get(cls_detected[xy]))
    # print(check1 + " = ", str(cls_list.count(check1)) + " | " + check2 + " = " , str(cls_list.count(check2)) + " | "  + check3 + " = " , str(cls_list.count(check3)))
    results.clear()
    if (cls_list.count(check1) == count1 and cls_list.count(check2) == count2 and cls_list.count(check3) == count3):
        return True
    else:
        if (cls_list.count(check1) - count1) != 0:
            ng_string_total.append(check1 + ": " + str(cls_list.count(check1) - count1))
        if (cls_list.count(check2) - count2) != 0:
            ng_string_total.append(check2 + ": " + str(cls_list.count(check2) - count2))
        if (cls_list.count(check3) - count3) != 0:
            ng_string_total.append(check3 + ": " + str(cls_list.count(check3) - count3))
        # print(ng_string_total)
        return False


def part_configuration_selector(unit_type):
    global df, model
    part_configuration_list_buffer = []
    part_configuration_list_buffer.clear()
    row_count = 0

    match unit_type:
        case "AA2JF":
            client.write_register(address=4000, value=10, slave=1)
            df = pd.read_csv('masking_coordinate_AA2JF.csv')
            model = YOLO(model_EagleL, task='detect')
            with open('Part Cheking Configuration AA2JF.csv', 'r') as file:
                reader = csv.reader(file, skipinitialspace=True, quoting=csv.QUOTE_NONE)
                for row in reader:
                    row_count = row_count + 1
                    part_configuration_list_buffer.append(row)
                return part_configuration_list_buffer
        case "ADXJF":
            client.write_register(address=4000, value=20, slave=1)
            df = pd.read_csv('masking_coordinate_ADXJF.csv')
            model = YOLO(model_EagleH, task='detect')
            with open('Part Cheking Configuration ADXJF.csv', 'r') as file:
                reader = csv.reader(file, skipinitialspace=True, quoting=csv.QUOTE_NONE)
                for row in reader:
                    row_count = row_count + 1
                    part_configuration_list_buffer.append(row)
                return part_configuration_list_buffer
        case "ADXDE_ADXFE":
            client.write_register(address=4000, value=20, slave=1)
            df = pd.read_csv('masking_coordinate_ADXDE_ADXFE.csv')
            model = YOLO(model_EagleH, task='detect')
            with open('Part Cheking Configuration ADXDE.csv', 'r') as file:
                reader = csv.reader(file, skipinitialspace=True, quoting=csv.QUOTE_NONE)
                for row in reader:
                    row_count = row_count + 1
                    part_configuration_list_buffer.append(row)
                return part_configuration_list_buffer


def save_record_directory(master_path, new_now):
    month = new_now.strftime("%m")
    year = new_now.strftime("%Y")
    month_year = year + "_" + month
    path = master_path + month_year + "\\"

    if not os.path.exists(path):
        os.mkdir(path)
        return path
        print("Folder %s created!" % path)
    else:
        return path


def save_record_picture(image_list, path, barcode_number_590, subplotx, subploty, new_now):
    fig = plt.figure(figsize=(int(fig_size_x), int(fig_size_y)))
    date_format = new_now.strftime(" %Y_%m_%d %H_%M_%S ")
    for count in range(len(image_list)):
        fig.add_subplot(subplotx, subploty, count + 1)
        plt.axis('off')
        plt.imshow(image_list[count])
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.tight_layout(pad=0)
    plt.savefig(save_record_directory(path, new_now=new_now) + date_format + barcode_number_590 + ".jpg",
                bbox_inches='tight', pad_inches=0)
    plt.clf()
    plt.close("all")


def save_ng_temporary(image_list, subplotx, subploty):
    # fig = plt.figure(figsize=(int(fig_size_x) * 2.5, int(fig_size_y) * 2.5))
    fig = plt.figure(figsize=(int(fig_size_x) * 2.5, int(fig_size_y) * 2.5))
    for count in range(len(image_list)):
        fig.add_subplot(subplotx, subploty, count + 1)
        plt.axis('off')
        plt.imshow(image_list[count])
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.tight_layout(pad=0)
    plt.savefig("temporary_show.jpg", bbox_inches='tight', pad_inches=0)
    plt.clf()
    plt.close("all")


def save_record_csv(barcode_number_590, barcode_number_710, NG_OK, Remark, PartDirectory, note, model_detection,
                    model_remark):
    global annotated_frame
    Now = datetime.datetime.now()
    cursor = cnxn.cursor()
    cursor.execute("INSERT INTO [" + table + "](DateTime,UnitNumber,Remark,Status,PartDirectory,Note) values ('" + str(
        Now) + "','" + str(barcode_number_590) + "','" + str(Remark) + "','" + str(NG_OK) + "','" + str(
        PartDirectory) + "','" + str(note) + str(model_detection) + "','" + str(model_remark) + "')")

    # cursor.execute("INSERT INTO [" + table + "](DateTime, UnitNumber,Remark,PartDirectory,Status) values ('" + str(
    #    Now) + "','" + str(barcode_number) + "','"
    #              + str(Remark) + "','" + str(PartDirectory) + "','" + str(NG_OK) + "')")
    cnxn.commit()


def read_table():
    cursor = cnxn.cursor()
    cursor.execute(
        "SELECT SerielNumber FROM F710SerielNumber where Id=(Select MAX(Id) from F710SerielNumber) order by id desc")
    for row in cursor.fetchall():
        return (row)


def save_in_server(barcode_number_590, barcode_number_710, NG_OK, part_ng_count, ScratchesMoistureTotal, path,
                   note, new_now, image_list_part):
    global annotated_frame
    try:
        if checkbox_status == 0:
            save_record_csv(barcode_number_590=barcode_number_590,
                            barcode_number_710=barcode_number_710, NG_OK=NG_OK, model_detection=model_EagleL,
                            model_remark=model_remark,
                            Remark="Found:" + str(part_ng_count) + " PartNG || " + str(
                                sum(ScratchesMoistureTotal)) + " AppNG",
                            PartDirectory=save_record_directory(path,
                                                                new_now=new_now) + new_now.strftime(
                                " %Y_%m_%d %H_%M_%S ") + str(barcode_number_590) + ".jpg",
                            note=note)
        else:
            save_record_csv(barcode_number_590=barcode_number_590,
                            barcode_number_710="", NG_OK=NG_OK, model_detection=model_EagleL, model_remark=model_remark,
                            Remark="Found:" + str(part_ng_count) + " PartNG || " + str(
                                sum(ScratchesMoistureTotal)) + " AppNG",
                            PartDirectory=save_record_directory(path,
                                                                new_now=new_now) + new_now.strftime(
                                " %Y_%m_%d %H_%M_%S ") + str(barcode_number_590) + ".jpg",
                            note=note)

    except Exception as e:
        print(e)
        print("Server Down!")
        annotated_frame = cv2.imread('SERVER_DOWN.JPG')

    try:
        save_record_picture(image_list_part, path, barcode_number_590, subplotx=int(subplotx),
                            subploty=int(subploty), new_now=new_now)
    except Exception as e:
        print(e)
        print("Server Down!")
        annotated_frame = cv2.imread('SERVER_DOWN.JPG')


def task1():  # get_frame
    global img_array, annotated_frame, frame_copy, frame, CheckBox_ID, area_variable, df
    while cap.isOpened():
        success, frame_get_temp = cap.read()
        # frame_resize = cv2.resize(frame_get_temp, (0, 0), fx=float(frame_size_x), fy=float(frame_size_y))
        frame_resize = frame_get_temp

        if imgmasking == '1':
            frame_1 = cv2.rectangle(frame_resize, (
            df.iloc[int(area_variable) - 1]['Startpoint1_X'], df.iloc[int(area_variable) - 1]['Startpoint1_Y']),
                                    (df.iloc[int(area_variable) - 1]['Endpoint1_X'],
                                     df.iloc[int(area_variable) - 1]['Endpoint1_Y']), (0, 0, 0), -1)
            frame_2 = cv2.rectangle(frame_1, (
            df.iloc[int(area_variable) - 1]['Startpoint2_X'], df.iloc[int(area_variable) - 1]['Startpoint2_Y']),
                                    (df.iloc[int(area_variable) - 1]['Endpoint2_X'],
                                     df.iloc[int(area_variable) - 1]['Endpoint2_Y']), (0, 0, 0), -1)
            frame = cv2.rectangle(frame_2, (
            df.iloc[int(area_variable) - 1]['Startpoint3_X'], df.iloc[int(area_variable) - 1]['Startpoint3_Y']),
                                  (df.iloc[int(area_variable) - 1]['Endpoint3_X'],
                                   df.iloc[int(area_variable) - 1]['Endpoint3_Y']), (0, 0, 0), -1)
        else:
            frame = frame_resize
        frame_copy = frame.copy()

        # cv2.namedWindow("F710 QUALITY CHECKING", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("F710 QUALITY CHECKING", int(windowsizex), int(windowsizey))
        cv2.imshow("F710 QUALITY CHECKING", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


def task2():
    global area, annotated_frame, cls_list, PartCheckingFinished, frame_copy, CheckBox_ID, checkbox_status, button_status, barcode_number_590, barcode_number_710, NG_OK, part_ng_count, ScratchesMoistureTotal, path, note, new_now, image_list_part, area_variable, ng_string_total, dataset_colection

    ScratchesMoistureTotal = []
    image_list_part = []
    image_list_app = []
    image_list_temp_show = []
    cls_list = []
    result_list = []

    step = 0
    step_app = 0
    part_ng_count = 0
    show_ng = 0
    show_ng_judgement = 0
    flag = 0
    checkbox_status = 1
    button_status = ""
    while (1):
        while (button_status == ""):
            print("PLEASE SELECT PART CONFIGURATION!!!")
            time.sleep(0.5)
        while (step < len(PartChecking1)):
            rr = client.read_coils(address=3200, count=1, slave=1)
            if (rr.bits[0] == 1):
                if flag == 0:
                    current_time = datetime.datetime.now()
                    flag = 1
                time.sleep(float(delay_variable))
                if process_frame(PartChecking1[step], PartChecking2[step], PartChecking3[step],
                                 int(PartQuantity1[step]), int(PartQuantity2[step]), int(PartQuantity3[step])) == True:
                    result_list.append(True)
                    annotated_frame = cv2.rectangle(annotated_frame, (0, 0), (85, 60), (0, 255, 0), -1)
                    annotated_frame = cv2.putText(annotated_frame, 'OK', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                                  (0, 0, 0), 3, cv2.LINE_AA)
                    annotated_frame = cv2.putText(annotated_frame, str(step + 1), (100, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                                  2,
                                                  (0, 255, 255), 2, cv2.LINE_AA)
                    if (dataset_colection == 1):
                        date_format = datetime.datetime.now().strftime(" %Y_%m_%d %H_%M_%S ")
                        cv2.imwrite(DATASET_PATH + date_format + ".jpg", frame_copy)

                else:
                    y_position = 0
                    result_list.append(False)
                    annotated_frame = cv2.rectangle(annotated_frame, (0, 0), (85, 60), (0, 0, 255), -1)
                    annotated_frame = cv2.putText(annotated_frame, 'NG', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                                  (0, 0, 0), 3, cv2.LINE_AA)
                    annotated_frame = cv2.putText(annotated_frame, str(step + 1), (100, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                                  2,
                                                  (0, 0, 255), 2, cv2.LINE_AA)
                    for x in range(len(ng_string_total)):
                        y_position = y_position + 50
                        annotated_frame = cv2.putText(annotated_frame, ng_string_total[x], (180, y_position),
                                                      cv2.FONT_HERSHEY_SIMPLEX, 2,
                                                      (0, 255, 255), 3, cv2.LINE_AA)
                        # b   g    r
                    part_ng_count = part_ng_count + 1
                    image_list_temp_show.append(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
                    ng_string_total.clear()

                    if (dataset_colection == 1):
                        date_format = datetime.datetime.now().strftime(" %Y_%m_%d %H_%M_%S ")
                        cv2.imwrite(DATASET_PATH + date_format + ".jpg", frame_copy)

                client.write_coil(address=3200, value=0, slave=1)
                time.sleep(float(delay_variable))
                cls_list = []
                step = step + 1
                area_variable = area_variable + 1
                image_list_part.append(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))

            while (step >= int(subplotx) * int(subploty)):
                annotated_frame = cv2.imread('SCANNING_DISPLAY.JPG')
                step = len(PartChecking1) + 1
                TextBox_ID.focus_set()
                note = TextBox_Note.get(1.0, "end-1c")
                rr = client.read_coils(address=3200, count=1, slave=1)
                if (rr.bits[0] == 1):
                    new_now = datetime.datetime.now()
                    if "\n" in TextBox_ID.get("1.0", "end-1c"):
                        barcode_number_590 = TextBox_ID.get("1.0", "end-2c")
                        client.write_coil(address=3200, value=0, slave=1)
                        cycle_time = (datetime.datetime.now() - current_time)

                        NG_OK = all(result_list)
                        if NG_OK == True:
                            path = OK_PATH
                            NG_OK = "OK"
                            client.write_coil(address=3400, value=1, slave=1)  # green lamp

                            annotated_frame = cv2.imread('OK_DISPLAY.JPG')
                            save_in_server(barcode_number_590=barcode_number_590, barcode_number_710="",
                                           part_ng_count=part_ng_count,
                                           ScratchesMoistureTotal=ScratchesMoistureTotal,
                                           path=path, note=note, new_now=new_now, NG_OK=NG_OK,
                                           image_list_part=image_list_part)

                        else:
                            path = NG_PATH
                            NG_OK = "NG"
                            client.write_coil(address=3402, value=1, slave=1)  # red lamp
                            annotated_frame = cv2.imread('NG_DISPLAY.JPG')

                            client.write_coil(address=3411, value=0, slave=1)  # CLEAR BUTTON
                            client.write_coil(address=3412, value=0, slave=1)  # CLEAR BUTTON

                            if (len(image_list_temp_show) != 0):
                                while (show_ng == 0):
                                    rx = client.read_coils(address=3410, count=1, slave=1)
                                    if (rx.bits[0] == 1):
                                        show_ng = 1
                                        time.sleep(0.1)
                                        client.write_coil(address=3402, value=0, slave=1)
                                        if (len(image_list_temp_show) < 10):
                                            save_ng_temporary(image_list_temp_show, subplotx=3, subploty=3)
                                            annotated_frame = cv2.imread('temporary_show.jpg')
                                            while (show_ng_judgement == 0):
                                                rx2 = client.read_coils(address=3411, count=1, slave=1)
                                                rx3 = client.read_coils(address=3412, count=1, slave=1)
                                                if (rx2.bits[0] == 1):
                                                    time.sleep(0.1)
                                                    show_ng_judgement = 1
                                                    annotated_frame = cv2.imread('PENDING VERIFICATION.jpg')
                                                    NG_OK = "PENDING VERIFICATION"
                                                    save_in_server(barcode_number_590=barcode_number_590,
                                                                   barcode_number_710="",
                                                                   part_ng_count=part_ng_count,
                                                                   ScratchesMoistureTotal=ScratchesMoistureTotal,
                                                                   path=path, note=note, new_now=new_now, NG_OK=NG_OK,
                                                                   image_list_part=image_list_part)

                                                elif (rx3.bits[0] == 1):
                                                    time.sleep(0.1)
                                                    show_ng_judgement = 1
                                                    annotated_frame = cv2.imread('NG_DISPLAY.jpg')
                                                    NG_OK = "NG"
                                                    save_in_server(barcode_number_590=barcode_number_590,
                                                                   barcode_number_710="",
                                                                   part_ng_count=part_ng_count,
                                                                   ScratchesMoistureTotal=ScratchesMoistureTotal,
                                                                   path=path, note=note, new_now=new_now, NG_OK=NG_OK,
                                                                   image_list_part=image_list_part)

                                        else:
                                            annotated_frame = cv2.imread('MANY_NG_DISPLAY.JPG')
                                            NG_OK = "NG"
                                            save_in_server(barcode_number_590=barcode_number_590,
                                                           barcode_number_710="",
                                                           part_ng_count=part_ng_count,
                                                           ScratchesMoistureTotal=ScratchesMoistureTotal,
                                                           path=path, note=note, new_now=new_now, NG_OK=NG_OK,
                                                           image_list_part=image_list_part)

                        step_app = 0
                        step = 0
                        area_variable = 1

                        ScratchesMoistureTotal = []
                        image_list_app = []
                        image_list_part = []
                        result_list.clear()
                        part_ng_count = 0
                        TextBox_ID.delete('1.0', END)
                        show_ng_judgement = 0
                        image_list_temp_show.clear()
                        image_list_part.clear()
                        image_list_app.clear()
                        print(barcode_number_590 + " " + NG_OK + " Time Elapsed: " + str(
                            cycle_time.seconds) + "s" + " " + note)
                        show_ng = 0
                        flag = 0
                        cycle_time = 0
                        current_time = 0
                        gc.collect()


# SELECT F590SerielNumber FROM F810SerielNumber where Id=(Select MAX(Id) from F810SerielNumber) order by id desc
def task3():
    global TextBox_ID, CheckBox_ID, TextBox_Note, dataset_colection
    global win

    win = Tk()
    # Set the geometry of Tkinter frame
    win.title("Barcode Scanner")
    win.geometry("800x200")

    # Define Function to print the input value
    def display_input():
        global checkbox_status, button_status, PartChecking1, PartChecking2, PartChecking3, PartQuantity1, PartQuantity2, PartQuantity3, df, model
        PartChecking1 = []
        PartChecking2 = []
        PartChecking3 = []
        PartQuantity1 = []
        PartQuantity2 = []
        PartQuantity3 = []
        checkbox_status = var1.get()
        button_status = var2.get()

        print("Part Configuration: " + button_status)

        match button_status:
            case ("AA2JF"):
                print("Model:" + model_EagleL)
            case ("ADXGF"):
                print("Model:" + model_EagleH)


        part_configuration_list = part_configuration_selector(button_status)
        row_count = len(part_configuration_list)
        for n in range(row_count - 1):
            # print(part_configuration_list[1:17][n])
            PartChecking1.append(part_configuration_list[1:row_count][n][1])
            PartChecking2.append(part_configuration_list[1:row_count][n][3])
            PartChecking3.append(part_configuration_list[1:row_count][n][5])

            PartQuantity1.append(part_configuration_list[1:row_count][n][2])
            PartQuantity2.append(part_configuration_list[1:row_count][n][4])
            PartQuantity3.append(part_configuration_list[1:row_count][n][6])

    def dataset_collection():
        global dataset_colection
        dataset_colection = var3.get()
        print("Dataset Collection: " + str(dataset_colection))

    var1 = IntVar()
    var3 = IntVar()
    var2 = StringVar()
    Check1 = Checkbutton(win, text="SCAN BARCODE?", variable=var1, onvalue=1, offvalue=0, command=display_input,
                         justify=LEFT, bd=5, font='Helvetica 12 bold')
    Check2 = Checkbutton(win, text="DATASET COLLECTION?", variable=var3, onvalue=1, offvalue=0,
                         command=dataset_collection,
                         justify=LEFT, bd=5, font='Helvetica 12 bold')
    Label1 = Label(win, text="Barcode Scanner: ", font='Helvetica 12 bold')
    Label2 = Label(win, text="Note: ", font='Helvetica 12 bold')

    TextBox_ID = Text(win, height=2, width=40, bg="light yellow")
    TextBox_Note = Text(win, height=1, width=10, bg="light yellow")

    radio_button1 = Radiobutton(win, text="AA2JF", variable=var2, value="AA2JF", indicator=2, background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    radio_button2 = Radiobutton(win, text="ADXJF", variable=var2, value="ADXJF", indicator=2,
                                background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    radio_button3 = Radiobutton(win, text="ADXDE_ADXFE", variable=var2, value="ADXDE_ADXFE", indicator=2,
                                background="light blue",
                                command=display_input, font='Helvetica 12 bold')
    Label1.grid(row=1, column=1, sticky=W, pady=2)
    Label2.grid(row=2, column=1, sticky=W, pady=2)
    TextBox_ID.grid(row=1, column=2, sticky=W, pady=2)
    TextBox_Note.grid(row=2, column=2, sticky=W, pady=2)

    radio_button1.grid(row=1, column=3, sticky=W, pady=2)
    radio_button2.grid(row=2, column=3, sticky=W, pady=2)
    radio_button3.grid(row=3, column=3, sticky=W, pady=2)

    Check1.grid(row=1, column=4, sticky=W, pady=2)
    Check2.grid(row=2, column=4, sticky=W, pady=2)

    Check1.select()
    Check2.deselect()
    # radio_button1.select()
    # TextBox_ID.pack()
    # t1.pack()

    win.mainloop()


if __name__ == "__main__":
    try:
        gc.enable()
        global img_array, area, annotated_frame, ocr_reader, PartCheckingFinished
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
        model_EagleH = setting_list[18][1]
        model_remark = setting_list[19][1]
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
        model_EagleL = setting_list[31][1]

        df = pd.read_csv('masking_coordinate_AA2JF.csv')
        cnxn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + uid + ';PWD=' + pwd + '')
        cnxn = pyodbc.connect('DSN=' + DSN + ';UID=' + uid + ';PWD=' + pwd + '')
        print("Server: " + server + " Database: " + database + " DSN: " + DSN + " TABLE: " + table)
        print("TcpClient: " + tcp_client + " Tcpport: " + tcp_port)
        print("Model Eagle High: " + model_EagleH + " Model2: " + model_remark)
        print("Model Eagle Low: " + model_EagleL + " Model2: " + model_remark)
        print("conf: " + conf_model + " conf2: " + conf_model2)
        print("CameraID: " + camera_id)
        print("Dataset_Collection: " + str(dataset_colection))
        print("Scan Barcode: " + scan_barcode)
        print("Resolution: " + frame_size_x + "x" + frame_size_y)

        client = ModbusTcpClient(host=tcp_client, port=int(tcp_port))
        client.connect()
        client.write_coil(address=320, value=0, slave=1)
        client.write_coil(address=340, value=0, slave=1)
        client.write_coil(address=341, value=0, slave=1)
        client.write_coil(address=342, value=0, slave=1)

        img_array = []
        area = 0
        PartCheckingFinished = 0
        area_variable = 1
        annotated_frame = cv2.resize(cv2.imread('initial_image.jpg'), (0, 0), fx=0.5, fy=0.5)
        model = YOLO(model_EagleH, task='detect')
        results = model(annotated_frame, conf=float(conf_model), iou=float(iou_model), show_conf=False, verbose=False,
                        task='detect')
        # results = model2(annotated_frame, conf=float(conf_model), iou=float(iou_model),show_conf=False, verbose=False, task='detect')
        print("Camera API: " + camera_API)
        if camera_API == "":
            cap = cv2.VideoCapture(int(camera_id))
        else:
            cap = cv2.VideoCapture(int(camera_id), int(camera_API))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(frame_size_x))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(frame_size_y))

        t1 = threading.Thread(target=task1)
        t2 = threading.Thread(target=task2)
        t3 = threading.Thread(target=task3)

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
