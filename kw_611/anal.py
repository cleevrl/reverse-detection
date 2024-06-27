import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from roi import getRoiValue ,boxinRoinew, drawpolylines,RoiStat,getPpm_ab,get_distance,getppmfromfile

# read csv file

# df = df.iloc[::3]  # Start from the first row (index 0), and get every second row
# df2 = df[df['id'] == 2][:50]
# df3 = df[df['id'] == 3][:50]
# df4 = df[df['id'] == 4][:50]
# df5 = df[df['id'] == 5][:50]
# df6 = df[df['id'] == 6][:50]
# df7 = df[df['id'] == 7][:50]
# df8 = df[df['id'] == 8][:50]
# df['area'] = df['h']*df['x']
def euclidean_distance(row):
    return np.sqrt((row['x2'] - row['x1']) ** 2 + (row['y2'] - row['y1']) ** 2)

def speed_with_previous(row, prev_row,a,b):
    d=np.sqrt((row['x'] - prev_row['x']) ** 2 + (row['y'] - prev_row['y']) ** 2) 
    y1= (row['y'] + prev_row['y'])/2
    yppm=(y1*a+b)/3.5
    dreal=d/yppm
    # print(d,yppm,dreal)
    print(f'd{d}, {y1}, {yppm}, {dreal}')

    return dreal

def distance_with_previous(row, prev_row):
    return np.sqrt((row['x'] - prev_row['x']) ** 2 + (row['y'] - prev_row['y']) ** 2) 
def calculate_distance(pts1, pts2):
    distance = math.sqrt((pts2[0] -pts1[0])**2 + (pts2[1] - pts1[1])**2)
    return distance
def get_distance(pts1,pts2,a,b):
    d=calculate_distance(pts1,pts2)
    y1= (pts1[1]+pts2[1])/2
    yppm=(y1*a+b)/3.5
    dreal=d/yppm
    print(f'd{d}, {y1}, {yppm}, {dreal}')
    return dreal

def save_fig(df,num,sr):
    a,b=getppmfromfile()
    print(f' a={a} b={b}')
# Calculate distance with previous row for each row
    distances = [np.nan]  # Distance with the first row is not defined
    speeds=[np.nan]
   
    for i in range(1, len(df)):
        prev_row = df.iloc[i - 1]
        current_row = df.iloc[i]
        distance= distance_with_previous(current_row, prev_row)

        speed= speed_with_previous(current_row, prev_row,a,b)

        # print(distance)
        speeds.append(speed)
        distances.append(distance)
    df['D'] = distances
    df['speed']=speed
    # print(df)
    # df['Dm'] = df['D'].expanding().mean()
    # df['D4'] = df['D'].rolling(window=10).mean()
    # df['A'] =df['h']*df['w']
    # df['Td']=df['time'].diff()
    # df['Yd']=df['y'].diff()
    # df['speed']=df['D']/df['Td']
    plt.figure(figsize=(10, 6))
    # plt.plot(df['frame'], df['D4']*100, marker='o', label='D4')
    # plt.plot(df['frame'], df['y'], marker='o', label='y')
    # plt.plot(df['frame'], df['Yd'], marker='o', label='YD')
    # # # plt.plot(df['frame'], df['w']*10, marker='o', label='w')
    # # # plt.plot(df['frame'], df['h']*10, marker='o', label='h')
    # # # plt.plot(df['frame'], df['A']/5, marker='o', label='A')
    plt.plot(df['frame'], df['D'], marker='o', label='D')
    plt.plot(df['frame'], df['speed'], marker='o', label='speed')
    # plt.plot(df['frame'], df['Td']*100, marker='o', label='Td')
    # # plt.plot(df['frame'], df['speed'], marker='o', label='speed')



    plt.title('Monthly Sales and Expenses')
    plt.xlabel('y')
    plt.ylabel('x')
    plt.legend()
    plt.grid(True)
    plt.show()
    # plt.save?fig("./res/"+num+"restime.png")

def run_all(file,sr):
    df = pd.read_csv(file, header = 0)
    # Car-Speed-Estimation-using-YOLOv8/res_loc_2024-05-03_10_12.csv
    mid = df['id'].max()
    for i in range(mid):
        print(f'lkw{i}')
        df1 = df[df['id'] == i+1]
        df1 = df1.iloc[::sr]  # Start from the first row (index 0), and get every second row

        save_fig(df1,str(i+1),sr)
def run_one(file,id,sr):
    df = pd.read_csv(file, header = 0)
    # print(df)
   
    df1 = df[df['id'] == id][:34]
    df1 = df1.iloc[::sr]  # Start from the first row (index 0), and get every second row

    save_fig(df1,str(id),sr)
file="resskip1/05-26_16:11:35res_org.csv"
file='live005_1/05-26_17:44:47res_cctv005.csv'
file='live005_1/05-26_17:55:21res_05-26_17:44:47res_cctv005.csv'
run_one(file,1,1)

# resskip1/05-26_16:11:35res_org.csv
# run_all("res_cctv005.csv",1)

# Car-Speed-Estimation-using-YOLOv8/res_cctv005.csv