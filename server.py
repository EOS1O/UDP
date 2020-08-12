#encoding-utf-8
import sys
import re
import socket
import time
import random
import threading
import io


class TempID:
    bigin = None
    end = None
    temp_id = ""

    def __init__(self, temp_id, st, et):
        self.temp_id = temp_id
        self.bigin = st
        self.end = et


class user:
    client = None
    username = None
    password = None
    status = "logout"
    wrong_times = 1
    block_time = 0
    temp_id = []

    def __init__(self,username,password):
        self.username = username
        self.password = password

    # when 3 times fail, time blocker will work
    def block_timer(self):
        self.status = "logout"
        self.wrong_times = 1

    def login(self, password, client, timeoflock):
        if self.status == "block":
            return 2
        elif self.status == "login":
            return 4
        if self.password == password:
            self.status = "login"
            self.wrong_times = 1
            self.client = client
            return 0
        else:
            if self.wrong_times >= 3:
                self.status = "block"
                threading.Timer(timeoflock,self.block_timer).start()
                return 2
            else:
                self.wrong_times += 1
                return 1

    def logout(self):
        if self.status != "login":
            return 1
        else:
            self.status = "logout"
            self.client = None
            self.wrong_times = 1
            self.temp_id = []
            return 0

    def append_id(self, temp_id):
        self.temp_id.append(temp_id)


class server:
    user_password = "credentials.txt"
    user_tid = "tempIDs.txt"
    zid_log = "z5224815_contactlog.txt"
    info_list = {}
    local_host = "127.0.0.1"
    local_port = 10000
    s_socket = None
    c_pool = []
    last_user = []
    flag_print = []
    receive_flag = 0
    num_line = 0
    timeoflock = 15;
    initial_id = 10000000000000000000;
    new_id = {}
    tpid = []

    def __init__(self,s_port,timeoflock):
        self.timeoflock = timeoflock
        self.local_port = s_port
        fp = open(self.user_password, 'r')
        for line in fp.readlines():
            result = re.match(r"(\+.*) (.*)",line)
            self.info_list[result.group(1)] = user(result.group(1),result.group(2))
        fp.close()
        fp = open(self.user_tid, 'r')
        for line in fp.readlines():
            result = re.match(r"(\+[A-Za-z0-9]+) ([0-9]+) ([0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+) (\d+/\d+/[0-9]+ \d+:\d+:\d+)",line)
            self.info_list[result.group(1)].temp_id.append(TempID(result.group(2),result.group(3),result.group(4)))
            bigin = time.mktime(time.strptime(result.group(3), "%d/%m/%Y %H:%M:%S"))
            end = time.mktime(time.strptime(result.group(4), "%d/%m/%Y %H:%M:%S"))
            self.new_id[result.group(2)]={"username":result.group(1),"bigin":bigin,"end":end}
        fp.close()
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_socket.bind((self.local_host, self.local_port))

    # the information of login to the client
    def info_login(self,client,username,password):
        msg = "login:"
        if username in self.info_list:
            rst=self.info_list[username].login(password,client,self.timeoflock)
            msg += str(rst)
        else:
            msg += "3"
        self.msgtoc(msg,client)

    # the information of logout to the client
    def info_logout(self,client,username):
        msg = "logout:"
        if username in self.info_list:
            rst = self.info_list[username].logout()
            msg += str(rst)
        else:
            msg += "3"
        self.msgtoc(msg,client)
        if rst == 0:
            print(username+" logout")

    def gettime(self,ctime):
        return time.strftime("%d/%m/%Y %H:%M:%S", ctime)

    def get_temp_id(self):
        temp_id = self.initial_id
        while True:
            temp_id = self.initial_id + random.randint(0,10000000000)
            self.initial_id = temp_id
            yield temp_id

    def tempID_recv(self,client,username):
        temp_id = next(self.get_temp_id())
        self.info_list[username].append_id(temp_id)
        bigin = time.time()
        end = bigin + 15*60
        msg = "tempID:" + str(temp_id) + ":" + str(bigin)+":"+str(end)
        self.msgtoc(msg,client)
        self.new_id[str(temp_id)]={"username":username,"bigin":bigin,"end":end}
        with open(self.user_tid,"a") as fp:
            fp.write(username+" "+str(temp_id)+" "+self.gettime(time.localtime())+" "+self.gettime(time.localtime(time.time()+900))+"\n")
        print("user:"+username+"\nTempID\n"+str(temp_id))

    # the contactlog comes from client
    def c_log(self,client,username,log_str):
        aim_flag = 0
        user_id = []
        start_time = []
        new_log = log_str.split("!")
        if new_log[0] in self.tpid:
            pass
        else:
            self.tpid.append(new_log[0])
        aimlist = []
        #for i in self.tpid:
            #print(i + "\n")
        #print("tpid:\n",self.tpid)
        line_flag = 0
        upload = open(self.zid_log, 'r')
        for line1 in upload.readlines():
            line_flag += 1
        upload.close()
        #print("num_line:",line_flag)
        #line_flag = new_log.pop()
        #num = float(line_flag)
        #num = int(line_flag)
        #print("len",len(line_flag))
        #print("line_flag: ",line_flag)
        #print("receive_flag: ",self.receive_flag)
        #receive_flag = 0
        #print(new_log+"\n")
        self.last_user.append(username)
        if(len(self.last_user) == 1):
            print("received contact log from " + username)
            for line in new_log:
                if(len(line)!=2):
                    print(line)
            print("\n")
        elif (len(self.last_user) > 1):
            if(username == self.last_user[-2]):
                for line in new_log:
                    if (len(line) != 2):
                        print(line)
                print("\n")
            else:
                for line in new_log:
                    if (len(line) != 2):
                        print(line)
                print("\n")

        if(line_flag == self.receive_flag + 1):
            print("Contact log checking\n")
            #for i in self.tpid:
                #print(i + "\n")
            self.tpid.pop(0)
            tid = open(self.user_tid, 'r')
            #length = len(self.tpid)
            #print("len_tid \n",length)
            for line1 in tid.readlines():
                for tid1 in self.tpid:
                    #print("tid1:\n", tid1)
                    #print("tid2:\n",tid1)
                    if(tid1 in line1):
                        #print("tid3:\n",tid1)
                        for word in line1:
                            aimlist.append(word)
                        len_a = len(aimlist)
                        #print("len_a:\n",len_a)
                        for i in range(len_a):
                            if(aimlist[i] == " "):
                                aim_flag += 1
                            if(aim_flag == 0):
                                user_id.append(aimlist[i])
                            if (aim_flag == 2 or aim_flag == 3):
                                start_time.append(aimlist[i])
                        aim_flag = 0
                        start_time.pop(0)
                        print("".join(user_id) + ",\n")
                        user_id = []
                        aimlist = []
                        print("".join(start_time) + ",\n")
                        start_time = []
                        print(str(tid1) + ";\n")

            tid.close()



        #result = re.match(r"([0-9]+) (\d+/\d+/[0-9]+ \d+:[0-9]+:\d+) (\d+/[0-9]+/\d+ [0-9]+:\d+:[0-9]+)",line)
        #if result:
            #line = result.group(1)+", "+result.group(2)+", "+result.group(3)+";"

        #print("\nContact log checking")
        # for line1 in new_log:
        #     result = re.match(r"(\d+) ([0-9]+/\d+/[0-9]+ [0-9]+:\d+:\d+) (\d+/[0-9]+/\d+ [0-9]+:[0-9]+:\d+)",line1)
        #     if result:
        #         username = self.new_id[result.group(1)]["username"]
        #         line1 = line1.replace(result.group(1),username, 1)
        #         line1 = username+", "+result.group(2)+", "+result.group(1)+";"
        #         print(line1)

    # def check_log(self, client, username, log_str):
    #     print("\nContact log checking")
    #     new_log = log_str.split("!")
        #for line in newlog

    # the information sending from the client
    def c_info(self,client):
        while True:
            try:
                recv = client.recv(1024)
            except ConnectionError:
                print("connect error. client close.")
                client.close()
                self.c_pool.remove(client)
                for username in self.info_list:
                    user = self.info_list[username]
                    if user.client == client and user.status == "login":
                        user.status = "logout"
                break
            recv = recv.decode(encoding="utf8")
            if re.match(r"login:(\+[A-Za-z0-9]+):(\w+)",recv):
                match = re.match(r"login:(\+[A-Za-z0-9]+):(.*)",recv)
                self.info_login(client,match.group(1),match.group(2))
            elif re.match(r"logout:(\+[A-Za-z0-9]+)",recv):
                match = re.match(r"logout:(\+.*)",recv)
                self.info_logout(client,match.group(1))
            elif re.match(r"tempID:(\+.*)",recv):
                match = re.match(r"tempID:(\+[A-Za-z0-9]+)",recv)
                self.tempID_recv(client,match.group(1))
            #elif re.match(r"uploadlog:(\+[A-Za-z0-9]+):([ /:\n[A-Za-z0-9]\+]+)",recv):
            elif re.match(r"uploadlog:(\+[A-Za-z0-9]+):(.*)", recv):
                match = re.match(r"uploadlog:(\+[A-Za-z0-9]+):(.*)",recv)
                if(match):
                    self.c_log(client,match.group(1),match.group(2))
                    self.receive_flag += 1
                    #self.check_log(client, match.group(1), match.group(2))

    def msgtoc(self,msg,client):
        client.sendall(msg.encode(encoding="utf8"))

    def start(self):
        self.s_socket.listen(10)
        while True:
            client,_ = self.s_socket.accept()
            thread = threading.Thread(target=self.c_info,args=(client,))
            thread.setDaemon(True)
            thread.start()
            self.c_pool.append(client)


if __name__ == "__main__":
    s_port = int(sys.argv[1])
    timeoflock = int(sys.argv[2])
    launch = server(s_port, timeoflock)
    launch.start()