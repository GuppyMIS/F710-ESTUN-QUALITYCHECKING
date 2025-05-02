import cv2

def masking_frame(area_variable,frame_resize,df,show_masking_number):
    get_columns_name = list(df.columns)
    get_column_number = len(get_columns_name)
    for x in range(0, get_column_number - 1,4 ):
        frame_masking = cv2.rectangle(frame_resize, (df.iloc[int(area_variable) - 1][get_columns_name[x + 1]], df.iloc[int(area_variable) - 1][get_columns_name[x + 2]]),
                                (df.iloc[int(area_variable) - 1][get_columns_name[x + 3]], df.iloc[int(area_variable) - 1][get_columns_name[x + 4]]),(0, 0, 0), -1)
        if show_masking_number == True:
            frame_masking = cv2.putText(frame_masking, str(int((x + 4)/4)), ((df.iloc[int(area_variable) - 1][get_columns_name[x + 1]],  df.iloc[int(area_variable) - 1][get_columns_name[x + 2]]+30)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                      (0, 255, 255), 2, cv2.LINE_AA)
    x=0
    """
    frame_1 = cv2.putText(frame_1, '1', (df.iloc[int(area_variable) - 1]['Startpoint1_X']-10, df.iloc[int(area_variable) - 1]['Startpoint1_Y']-10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                  (255, 255, 255), 2, cv2.LINE_AA)
                                  """


    return frame_masking