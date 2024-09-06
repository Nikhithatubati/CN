import subprocess
import os
import argparse
import random
import shutil
import json
import matplotlib.pyplot as plt
import matplotlib.patches as Patch
folder = 'ping_test'

def ping(destination, count, delay):
    try:
        ping_out = subprocess.check_output(['ping', '-c', str(count), '-i', str(delay), destination], universal_newlines = True)
        lines = ping_out.strip().split('\n')
        if not os.path.exists(folder):
            os.mkdir(folder)
        filename = "ping.out"
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
                    key = 1
                    for line in file_content[1:]:
                        #print(line)
                        ele = line.split()
                        if key <= 10:
                            host = ele[4][1:-2:]
                            time = float(ele[len(ele)-2][5::])
                            data_host[key] = host
                            data_vals[key] = [time]
                            key = key + 1
                        if len(ele) != 0 and ele[0]=='rtt':
                            t = ele[3].split("/")
                            print(t)
        return (data_host, data_vals)
    else:
        print("The folder does not exist")

def json_writer(d1, d2, k=" "):
    trace_data = []
    for (x,y),(a,b) in zip(d1.items(), d2.items()):
        data={
                'packet': x,
                'host': y,
                'time': b
            }
        trace_data.append(data)
    file_name = " "
    if (k==" "):
        file_name = "ping_data.json"
    elif (os.path.exists(k)):
        file_name = k+"/ping_data.json"
    elif not os.path.exists(k):
        file_name = "ping_data.json"
    json_data = json.dumps(trace_data, indent = 4)
    with open(file_name, "w") as json_file:
        json_file.write(json_data)
    print("The json file has been saved")

def graph_plotter(d, k=" "):
    data_lists = list(d.values())
    labels = list("packet" + str(i) for i in d.keys())
    colors = [plt.cm.jet(random.random()) for i in d.keys()]
    plt.figure(figsize=(10, 10))
    a = plt.boxplot(data_lists, labels=labels, patch_artist=True, showmeans = True)
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
        plt.savefig('ping_output.pdf')
    elif (os.path.exists(k)):
        plt.savefig(k+'/ping_output.pdf')
    elif not os.path.exists(k):
        plt.savefig('ping_output.pdf')
        print("The given location is not valid and the file is saved in current working directory")
    print("The graph has been saved")

def pingstats():
    parser = argparse.ArgumentParser(description="Trace the route to a destination host or IP address.")
    parser.add_argument("-t", dest="Target", type=str, help="Host or IP address to trace to.")
    parser.add_argument("-d", dest="delay", type=int, default=2, help="Number of seconds to wait between two consecutive ping packets")
    parser.add_argument("-m", dest="Max_pings", type=int, default=10, help="Maximum number of ping packets (default: 30).")
    parser.add_argument("-o", dest="Output", default=" ", help="Path and name of output JSON file containing the stats")
    parser.add_argument("-g", dest="Graph", default=" ", help="Path and nameof output PDF file containing stats graph")
    parser.add_argument("--test", dest="Test_Dir", type=str, help="Directory containing num_runs text files, each of whihc contains the outptu of a traceroute run. If present, this will override all other options and traceroute will not be invoked. Stats will be computed over the traceroute output stored in the text files")

    args = parser.parse_args()

    if args.Test_Dir:
        #parsing(folder)
        d1,d2 = parsing(args.Test_Dir)
        #y1={x:y for x,y in d1.items() if y!=[]}
        #y2={x:y for x,y in d2.items() if y!=[]}
        json_writer(d1,d2,args.Output)
        graph_plotter(d2,args.Graph)
    elif args.Target:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        ping(args.Target,args.Max_pings, args.delay)
        #parsing(folder)
        d1,d2 = parsing(folder)
        #y1={x:y for x,y in d1.items() if y!=[]}
        #y2={x:y for x,y in d2.items() if y!=[]}
        json_writer(d1,d2,args.Output)
        graph_plotter(d2,args.Graph)
    elif not args.Target:
        print("use -t to provide url")
        exit
    if not args.Output:
        print("The location of the file is /home/student/Tubati_trstats and the name is data.json")
    if not args.Graph:
        print("The location of the file is /home/student/Tubati_trstats and the name is output.pdf")

if __name__ == "__main__":
    pingstats()
