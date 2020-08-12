# UDP

### 已实现功能：
+ Server与多个Client间通信
+ 登录登出功能
+ 3次登陆错误锁定10s
+ client向server申请虚拟临时ID
+ 上传日志
+ 日志检查
+ 过期日志（3mins）自动删除
+ p2p连接通信
+ p2p连接有效性检测

**Important notes：My programs and download files are located in G:\UNSWIT\9331\ASS, so my local tests are based on this route. If you are needing to test it and something goes wrong occasionally , please open server.py and client.py to change  the route to a right one which includes the server.py (line 74,75,76), client.py (line 15,16), credentials.txt, tempIDs.txt, z5224815_contactlog.txt. Thank you.**


#### Part 1: Launch server

 The first step is running the server by using this command

```
python G:\UNSWIT\9331\ASS\server.py 10000 10
```

10000  -  server_port			10  -  block_duration

![微信图片_20200807002924](C:\Users\24593\Desktop\微信图片_20200807002924.png)



#### Part 2: Client login

The user needs to use client.py to login by typing this command

```
python G:\UNSWIT\9331\ASS\client.py 127.0.0.1 10000 10
```

 127.0.0.1  -  local_host        10000  -  server_port      10  -  client_udp_port (random)

![微信图片_20200807004328](C:\Users\24593\Desktop\微信图片_20200807004328.png)



##### Case 1 - Login successfully

![微信图片_20200807004625](C:\Users\24593\Desktop\微信图片_20200807004625.png)



##### Case 2 - Wrong password

![微信图片_20200807005030](C:\Users\24593\Desktop\微信图片_20200807005030.png)



##### Case 3 - Wrong account

![微信图片_20200807005201](C:\Users\24593\Desktop\微信图片_20200807005201.png)



##### Case 4 - Already login

![微信图片_20200807011407](C:\Users\24593\Desktop\微信图片_20200807011407.png)



##### Case 5 - Log in wrongly three times

After 3 consecutive failed attempts,  user is blocked for a duration of block_duration seconds (in this program is 10 second)

![微信图片_20200807005539](C:\Users\24593\Desktop\微信图片_20200807005539.png)



#### Part 3: Client logout

When user want to logout, he can type this command in the client

```
logout
```

![微信图片_20200807010258](C:\Users\24593\Desktop\微信图片_20200807010258.png)

 In the server window, it will show which user logs out



#### Part 4: Download_tempID

After logging in, user need to apply for a distinct tempID

![微信图片_20200807010641](C:\Users\24593\Desktop\微信图片_20200807010641.png)

 In the server window, it will also show the TempID. In addition, a new record about this information will be added to the file tempIDs.txt 

![微信图片_20200807011016](C:\Users\24593\Desktop\微信图片_20200807011016.png)



#### Part 5: P2P

Use this command to connect with another client

```
Beacon 127.0.0.1 10
```

10   -   UDP_port

![微信图片_20200807011611](C:\Users\24593\Desktop\微信图片_20200807011611.png)

When current_time > expiry_time, peer-2 will display The beacon is invalid

![微信图片_20200807012104](C:\Users\24593\Desktop\微信图片_20200807012104.png)



#### Part 6: Uploadlog

In order to upload the log to the server, user can use this command

```
Upload_contact_log
```

![微信图片_20200807012748](C:\Users\24593\Desktop\微信图片_20200807012748.png)

In the server window, it shows all tempIDs, start_time and expiry_time. Meanwhile, it also shows contact log checking.

Because using of time locker,after 3 mins if there is no upload,the record will be deleted.

