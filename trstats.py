import subprocess
import os
import argparse
from datetime import datetime
import shutil
import time, random
import re
import json
from statistics import mean, median
import matplotlib.pyplot as plt
import matplotlib.patches as Patch
folder ='test_runs'

def trace(destination, max_hops=30):
    try:
        trace_out = subprocess.check_output(['traceroute', destination], universal_newlines = True)
        lines = trace_out.strip().split('\n')
        if not os.path.exists(folder):
            os.mkdir(folder)
        filename = str(datetime.now()) + ".out"
        file_path = os.path.join(folder, filename)

        with open(file_path, "w") as file:
            for line in lines:
                file.write(line + "\n")
    except subprocess.CalledProcessError as e:
        print("Error running traceroute:", e)

def parsing(location):
    if os.path.exists(location):
        files = os.listdir(location)
        data_vals = {}
        data_host = {}
        for file_name in files:
            file_path = os.path.join(location, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    file_content = file.read().strip().split("\n")
                    for line in file_content[1:]:
                        ele = line.split()
                        key = int(ele[0])
                        if ele[1] != '*':
                            host=ele[1]
                        t=[]
                        for i in range(2, len(ele)):
                            if ele[i] != '*':
                                t.append(float(ele[i][0:5]))
                        data_host[key] = host
                        if key in data_vals:
                            data_vals[key].extend(t)
                        else:
                            data_vals[key] = t
        data_val = {}
        for x in data_vals:
            l = []
            for y in data_vals[x]:
                l.append(float(y))
            data_val[x] = l
        return(data_host, data_val)
def parsing(location):
    if os.path.exists(location):
        files = os.listdir(location)
        data_vals = {}
        data_host = {}
        for file_name in files:
            file_path = os.path.join(location, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    file_content = file.read().strip().split("\n")
                    for line in file_content[1:]:
                        ele = line.split()
                        key = int(ele[0])
                        if ele[1] != '*':
                            host=ele[1]
                        t=[]
                        for i in range(2, len(ele)):
                            if ele[i] != '*':
                                t.append(float(ele[i][0:5]))
                        data_host[key] = host
                        if key in data_vals:
                            data_vals[key].extend(t)
                        else:
                            data_vals[key] = t
        data_val = {}
        for x in data_vals:
            l = []
            for y in data_vals[x]:
                l.append(float(y))
            data_val[x] = l
        return(data_host, data_val)
    else:
        print("The folder does not exist.")

def json_writer(d1, d2, k=" "):
    trace_data = []
    for (x,y),(a,b) in zip(d1.items(), d2.items()):
        data={
                'avg': round(mean(b),3),
                'hop': x,
                'host': y,
                'max': round(max(b), 3),
                'med': round(median(b), 3),
                'min': round(min(b), 3)
            }
        trace_data.append(data)
    file_name = " "
    if (k==" "):
        file_name = "data.json"
    elif (os.path.exists(k)):
        file_name = k+"/data.json"
    elif not os.path.exists(k):
        file_name = "data.json"
    json_data = json.dumps(trace_data, indent = 4)
    with open(file_name, "w") as json_file:
        json_file.write(json_data)
    print("The json file has been saved")

def graph_plotter(d, k=" "):
    data_lists = list(d.values())
    labels = list("hop" + str(i) for i in d.keys())
    colors = [plt.cm.jet(random.random()) for i in d.keys()]
    plt.figure(figsize=(10, 10))
    a = plt.boxplot(data_lists, labels=labels, patch_artist=True, showmeans = True, showfliers=True)
    p = [i[0:3] for i in colors]
    lamba = [Patch.Patch(color=color, label=label) for color, label in zip(p, labels)]
    plt.legend(handles = lamba)
    for box, out, m, color in zip(a['boxes'], a['fliers'], a['means'], colors):
        box.set_facecolor(color)
        out.set_markerfacecolor(color)
        out.set_markeredgecolor(color)
        out.set_markersize(5)
        m.set_markerfacecolor('black')
        m.set_markeredgecolor('black')
        m.set_marker('o')
    plt.title('Stats Graph')
    plt.xlabel('Hops')
    plt.ylabel('Latency')
    if (k==" "):
        plt.savefig('output.pdf')
    elif (os.path.exists(k)):
        plt.savefig(k+'/output.pdf')
    elif not os.path.exists(k):
        plt.savefig('output.pdf')
        print("The given location is not valid and the file is saved in current working directory")
    print("The graph has been saved")

def trstats():
    parser = argparse.ArgumentParser(description="Trace the route to a destination host or IP address.")
    parser.add_argument("-t", dest="Target", type=str, help="Host or IP address to trace to.")
    parser.add_argument("-n", dest="Num_Runs", type=int, default=5, help="Number of times traceroute will run")
    parser.add_argument("-d", dest="Run_Delay", type=int, default=2, help="Number of seconds to wait between two consecutive runs")
    parser.add_argument("-m", dest="Max_Hops", type=int, default=30, help="Maximum number of hops (default: 30).")
    parser.add_argument("-o", dest="Output", default=" ", help="Path and name of output JSON file containing the stats")
    parser.add_argument("-g", dest="Graph", default=" ", help="Path and nameof output PDF file containing stats graph")
    parser.add_argument("--test", dest="Test_Dir", type=str, help="Directory containing num_runs text files, each of whihc contains the outptu of a traceroute run. If present, this will override all other options and traceroute will not be invoked. Stats will be computed over the traceroute output stored in the text files")

    args = parser.parse_args()

    if args.Test_Dir:
        d1,d2 = parsing(args.Test_Dir)
        y1={x:y for x,y in d1.items() if y!=[]}
        y2={x:y for x,y in d2.items() if y!=[]}
        json_writer(y1,y2,args.Output)
        graph_plotter(y2,args.Graph)
    elif args.Target:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        for i in range(int(args.Num_Runs)):
            trace(args.Target,args.Max_Hops)
            time.sleep(int(args.Run_Delay))
        d1,d2 = parsing(folder)
        y1={x:y for x,y in d1.items() if y!=[]}
        y2={x:y for x,y in d2.items() if y!=[]}
        json_writer(y1,y2,args.Output)
        graph_plotter(y2,args.Graph)
    elif not args.Target:
        print("use -t to provide url")
        exit
    if not args.Output:
        print("The location of the file is /home/student/Tubati_trstats and the name is data.json")
    if not args.Graph:
        print("The location of the file is /home/student/Tubati_trstats and the name is output.pdf")

if __name__ == "__main__":
    trstats()
