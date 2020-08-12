#encoding-utf-8
import socket
import re
import sys
import threading
import time


class client:
    socket_c = None
    socket_p2p = None
    status = False
    username = ""
    temp_id = ""
    zid_log = "z5224815_contactlog.txt"
    user_tid = "tempIDs.txt"
    log_list = []
    log_file = None
    log_lock = None
    list1 = []
    list2 = []
    flag = 0

    def __init__(self, s_addr, p2p_port):
        try:
            self.socket_c = socket.socket()
            self.socket_c.connect(s_addr)
        except:
            print("服务器连接错误")
            exit()

        try:
            self.socket_p2p = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_p2p.bind(("127.0.0.1", p2p_port))
        except:
            print("p2p连接错误")
            exit()

    # Send information to the server
    def infotos(self,info):
        self.socket_c.send(info.encode(encoding="utf8"))

    # Send information to the client
    def info_c(self):
        #old_time = []
        expecttime = []
        while True:
            info, p2p_addr = self.socket_p2p.recvfrom(1024)
            info = info.decode(encoding="utf8")
            beacon_match = re.match(r"beacon:([0-9]+) ([0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+) ([0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+) ([\.\d]+)",info)
            p2p_id = str(beacon_match.group(1))
            #print("p2p_id"+beacon_match.group(1))
            #with open(self.user_tid, "r") as tid:
                #time_match = re.match(r"(\+[A-Za-z0-9]+) (p2p_id) ([0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+) (\d+/\d+/[0-9]+ \d+:\d+:\d+)",tid)
            #tid.close()

            # get the strat_time and expiry _time
            tid = open(self.user_tid, 'r')
            for line in tid.readlines():
                #time_match = re.match(r'.*p2p_id.*',line)
                #if(time_match):
                if p2p_id in line:
                    #line.split()
                    #line1 = ''.join(line)
                    for word in line:
                        expecttime.append(word)
                    len_e = len(expecttime)
                    for i in range(len_e):
                        if (expecttime[i] == " "):
                            self.flag = self.flag + 1
                        if (self.flag == 2 or self.flag == 3):
                            self.list1.append(expecttime[i])
                        if (self.flag == 4 or self.flag == 5):
                            self.list2.append(expecttime[i])
                    #for i in self.list1:
                        #print(i)
                    self.list1.pop(0)
                    self.list2.pop(0)
                    self.list2.pop()
                    new_list1 = "".join(self.list1)
                    new_list2 = "".join(self.list2)
                    self.flag = 0


                    #print("list1:\n",new_list1)
                    #print("list2:\n",new_list2)
                    #expecttime1 = "".join(expecttime)
                    #expecttime1.split()
                    #for group in expecttime1:
                        #print("group:",group)
                    #print("word: \n",word)
                    #len_e = len(expecttime)
                    #for i in range(len_e):
                        #if(expecttime[i] == " "):
                            #self.flag++
                            #if(self.flag == 2):
                               #list1.append(expecttime[i])

            tid.close()
            if beacon_match:
                print("received beacon:\n"+beacon_match.group(1)+",\n"+beacon_match.group(2)+",\n"+beacon_match.group(3)+".\n")
                print("Current time is: \n" + time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + ".")
                time_now = time.time()
                #old_time.append(time_now)
                begin = time.mktime(time.strptime("".join(self.list1),"%d/%m/%Y %H:%M:%S"))
                end = time.mktime(time.strptime(beacon_match.group(3),"%d/%m/%Y %H:%M:%S"))
                self.list1 = []
                self.list2 = []
                if begin <= time_now and time_now <= end:
                    print("\nThe beacon is valid.")
                    self.log_list.append({"temp_id":beacon_match.group(1),"begin":float(begin),"end":float(end),"str":info[7:]})
                    self.log_lock.acquire()
                    with open(self.zid_log,"a") as clog:
                        clog.write("\n"+info[7:])
                    self.log_lock.release()
            #if(time.time() - old_time[0] == 300):

                else:
                    print("The beacon is invalid.\n")

    def infotoc(self, address, info):
        self.socket_p2p.sendto(info.encode(encoding="utf8"),address)

    # login module, considering different cases
    def c_login(self):
        username = input("username:")
        password = input("password:")
        self.infotos("login:"+username+":"+password)
        recv = self.socket_c.recv(1024).decode(encoding="utf8")
        if recv == "login:0":
            self.status = True
            self.username = username
            print("Welcome to the BlueTrace Simulator!")
            self.log_lock = threading.Lock()
            release_beacon_thread = threading.Thread(target=self.release_beacon)
            release_beacon_thread.setDaemon(True)
            release_beacon_thread.start()
        elif recv == "login:1":
            print("Invalid Password. Please try again.")
        elif recv == "login:2":
            print("Invalid Password. Your account has been blocked. Please try again later.")
        elif recv == "login:3":
            print("Username does not exist.")
        elif recv == "login:4":
            print("User already login.")

    # logout module
    def c_logout(self):
        self.infotos("logout:" + self.username)
        recv = self.socket_c.recv(1024).decode(encoding="utf8")
        if recv == "logout:0":
            self.status = False
            self.username = ""
            self.temp_id = ""

    # get the tempID
    def getid(self):
        self.infotos("tempID:" + self.username)
        recv = self.socket_c.recv(1024).decode(encoding="utf8")
        match = re.match(r"tempID:([A-Za-z0-9]+):([\.\d]+):([\.\d]+)", recv)
        if match:
            self.temp_id = match.group(1)
        print("TempID:\n" + self.temp_id)

    # p2p module including send and receive msg
    def c_beacon(self, p2p_address):
        expecttime1 = []
        list3 = []
        list4 = []
        flag1 = 0
        time_now = time.time()
        begin = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time_now))
        end = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time_now + 180))
        version = 1.0
        p2p_id = self.temp_id
        tid = open(self.user_tid, 'r')
        for line in tid.readlines():
            if p2p_id in line:
                for word in line:
                    expecttime1.append(word)
                len_e = len(expecttime1)
                for i in range(len_e):
                    if (expecttime1[i] == " "):
                        flag1 = flag1 + 1
                    if (flag1 == 2 or flag1 == 3):
                        list3.append(expecttime1[i])
                    if (flag1 == 4 or flag1 == 5):
                        list4.append(expecttime1[i])
                list3.pop(0)
                list4.pop(0)
                list4.pop()
                new_list3 = "".join(list3)
                new_list4 = "".join(list4)
                flag1 = 0
        tid.close()
        info = self.temp_id + " " + "".join(list3) + " " + "".join(list4) + " " + str(version)
        print(self.temp_id + ",\n" + "".join(list3) + ",\n" + "".join(list4) + ".")
        self.infotoc(p2p_address, "beacon:" + info)
        pass

    # this function can delete those record which last for 3 mins
    def release_beacon(self):
        def beacon_filter(beacon):
            if beacon["begin"] <= time.time() and time.time() <= beacon["end"]:
                return True
            return False
        while True:
            length = len(self.log_list)
            temp_list = filter(beacon_filter,self.log_list)
            self.log_list = list(temp_list)
            if length > len(self.log_list):
                self.log_lock.acquire()
                with open(self.zid_log,"w") as clog:
                    for beacon in self.log_list:
                        clog.write("\n"+beacon["str"])
                self.log_lock.release()

    # Upload the log
    def up_log(self):
        up1 = []
        up2 = []
        up3 = []
        up_flag = 0
        line_flag = 0
        upload = open(self.zid_log, 'r')
        for line1 in upload.readlines():
            line_flag += 1
        upload.close()
        upload1 = open(self.zid_log, 'r')
        for line in upload1.readlines():
            for word in line:
                if(word == " "):
                    up_flag += 1
                if(up_flag == 0):
                    up1.append(word)
                elif(up_flag == 1 or up_flag == 2):
                    up2.append(word)
                elif(up_flag == 3 or up_flag == 4):
                    up3.append(word)
            if(len(up1)>0 and len(up2)>0 and len(up3)>0):
                up2.pop(0)
                up3.pop(0)
                print("".join(up1)+",\n")
                print("".join(up2) + ",\n")
                print("".join(up3) + ";\n")
            up_flag = 0
            self.infotos("uploadlog:" + self.username + ":" + "".join(up1) + "!" + "".join(up2) + "!" + "".join(up3))
            up1 = []
            up2 = []
            up3 = []

        upload1.close()
        # writelog = ""
        # for log in self.log_list:
        #     writelog += log["str"]
        #     writelog += "!"
        # self.log_lock.acquire()
        # with open(self.zid_log,"w+") as clog:
        #     for log in self.log_list:
        #         clog.write("\n"+log["str"])
        #         #print("\n"+log["str"])
        # self.log_lock.release()
        # writelog = writelog[:-1]
        # self.infotos("uploadlog:" + self.username + ":" + writelog)

    def start(self):
        c_thread = threading.Thread(target=self.info_c)
        c_thread.setDaemon(True)
        c_thread.start()

        while True:
            while not self.status:
                self.c_login()
            info = input()
            if info == "Download_tempID":
                self.getid()
            elif info == "Upload_contact_log":
                self.up_log()
            elif info == "logout":
                self.c_logout()
            elif re.match(r"Beacon ([0-9]+\.[0-9]+\.[0-9]+\.\d+) ([0-9]+)",info):
                match = re.match(r"Beacon ([0-9]+\.[0-9]+\.[0-9]+\.\d+) ([0-9]+)",info)
                self.c_beacon((match.group(1), int(match.group(2))))
            else:
                print("Error. Invalid command")


if __name__ == "__main__":
    s_ip = sys.argv[1]
    s_port = int(sys.argv[2])
    p2p_port = int(sys.argv[3])
    launch = client((s_ip, s_port),p2p_port)
    launch.start()
