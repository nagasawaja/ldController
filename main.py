# -- coding: utf-8 --
import os
import subprocess
import time
import psutil
import requests

ldPath = "C:\ChangZhi\dnplayer2\\"
ldconsole = ldPath + "ldconsole.exe"
ld = ldPath + "ld.exe"
lastReconnectTime = time.time()
noOpenList = ["laji"]
limitMemory = 750
limitCpu = 20
limitDuration = 3600
checkPacFlag = False
reconnectNet = True


def restartDevice(deviceAttrList):
    # running
    print("%s restart!!!" % (deviceAttrList[1]), flush=True)
    subprocess.run(ldconsole + " launch --index %s" % (deviceAttrList[0]))
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.reboot --value com.touchsprite.android" % (deviceAttrList[0]), timeout=5)
    deviceAliveFlag = False
    for i in range(1, 40):
        # check device alive
        procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=5)
        time.sleep(1)
        if str(procList.stdout.splitlines()[int(deviceAttrList[0])], encoding="gbk").split(",")[4] == "1":
            deviceAliveFlag = True
            break
    if deviceAliveFlag == False:
        print("%s cannot run device!!!" % (deviceAttrList[1]), flush=True)
        return
    print("%s run device!!!" % (deviceAttrList[1]), flush=True)
    touchSpriteFlag = False
    for i in range(1, 20):
        touchSpriteRunStatus = subprocess.run(
            ld + " -s %s adb shell \" dumpsys activity activities | grep mFocusedActivity\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
        touchSpriteRunStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell dumpsys activity activities | grep mFocusedActivity\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
        touchSpritePsList = touchSpriteRunStatus.stdout.splitlines()
        touchSpritePsList2 = touchSpriteRunStatus2.stdout.splitlines()
        tpInFlag = False
        for tp in touchSpritePsList:
            if "com.touchsprite.android/.activity.MainActivity" in str(tp, encoding="gbk"):
                tpInFlag = True
                break
        if tpInFlag == True:
            touchSpriteFlag = True
            break
        for tp in touchSpritePsList2:
            if "com.touchsprite.android/.activity.MainActivity" in str(tp, encoding="gbk"):
                tpInFlag = True
                break
        if tpInFlag == True:
            touchSpriteFlag = True
            break
        time.sleep(1)
    if touchSpriteFlag == False:
        print("%s cannot run touchSprite!!!" % (deviceAttrList[1]))
        return
    print("%s run touchSprite!!!" % (deviceAttrList[1]))
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value home" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=5)
    print("%s run home!!!" % (deviceAttrList[1]))
    time.sleep(4)
    subprocess.run(ldconsole + " sortWnd", timeout=5)
    print("%s run sortWnd!!!" % (deviceAttrList[1]))
    time.sleep(2)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=5)
    print("%s run script!!!" % (deviceAttrList[1]))
    print("%s run end!!!" % (deviceAttrList[1]))


def checkNetWork():
    try:
        r = requests.get("https://mgbsdk.matrix.netease.com/h55/sdk/query_product?platform=ios&ff_channel=app_store",
                         timeout=(1, 1))
        if r.status_code != 200 or lastReconnectTime + 60 * 10 <= time.time():
            # ping fail or time to reconnect
            reconnectNetwork()
        else:
            print("networkSuc", flush=True)
    except Exception as e:
        print("checkNetWorkFail", flush=True)
        print(e, flush=True)
        reconnectNetwork()


def reconnectNetwork():
    try:
        print("reconnectNetwork", flush=True)
        global lastReconnectTime
        lastReconnectTime = time.time()
        os.system('@Rasdial 宽带连接 /DISCONNECT')  # disconnect
        os.system('@Rasdial 宽带连接 hhad157 878053')  # reconnect
        time.sleep(3)
    except Exception as e:
        print("reconnectNetworkFail", flush=True)
        print(e, flush=True)


def checkHookApp(deviceAttrList):
    try:
        id5HookStatus = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.example.id5hook\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE)
        id5HookStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.example.id5hook\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE)
        id5HookPsList = id5HookStatus.stdout.splitlines()
        id5HookPsList2 = id5HookStatus2.stdout.splitlines()
        for l in id5HookPsList:
            if "com.example.id5hook" in str(l, encoding="gbk"):
                # print("%s hookAppSuc" % (deviceAttrList[1]), flush=True)
                return True
        for l in id5HookPsList2:
            if "com.example.id5hook" in str(l, encoding="gbk"):
                # print("%s hookAppSuc" % (deviceAttrList[1]), flush=True)
                return True

        return False
    except Exception as e:
        print("checkHookAppFail", flush=True)
        print(e, flush=True)
        return False


def checkPac(deviceAttrList):
    if "NewAccount" not in deviceAttrList[1]:
        return True
    try:
        id5HookStatus = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.android.pacprocessor\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE)
        id5HookStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.android.pacprocessor\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE)
        id5HookPsList = id5HookStatus.stdout.splitlines()
        id5HookPsList2 = id5HookStatus2.stdout.splitlines()
        for l in id5HookPsList:
            if "com.android.pacprocessor" in str(l, encoding="gbk"):
                print("%s pacprocessorSuc" % (deviceAttrList[1]), flush=True)
                return True
        for l in id5HookPsList2:
            if "com.android.pacprocessor" in str(l, encoding="gbk"):
                print("%s pacprocessorSuc" % (deviceAttrList[1]), flush=True)
                return True

        print("%s pacprocessorFail" % (deviceAttrList[1]), flush=True)
        return False
    except Exception as e:
        print("pacprocessorFail", flush=True)
        print(e, flush=True)
        return False


def checkExistNoOpenList(deviceInfoStr):
    for s in noOpenList:
        if s in deviceInfoStr:
            return True
    return False

def checkDeviceRunningHealth(deviceAttrList):
    dnplayerPid = int(deviceAttrList[5])
    ldBoxPid = int(deviceAttrList[6])
    runningStatus = deviceAttrList[4]
    try:
        if runningStatus != "1":
            return False
        # check pid exists
        if psutil.pid_exists(dnplayerPid) == False:
            print("%s dnplayerPid not exist" % (deviceAttrList[1]), flush=True)
            return False
        if psutil.pid_exists(ldBoxPid) == False:
            print("%s ldboxPid not exist"%(deviceAttrList[1]), flush=True)
            return False
        # check memory
        if (psutil.Process(dnplayerPid).memory_info().rss +psutil.Process(ldBoxPid).memory_info().rss) / 1024 / 1024 > limitMemory:
            print("%s memory:%dMB;limitMemory:%dMB"%(deviceAttrList[1], (psutil.Process(dnplayerPid).memory_info().rss +psutil.Process(ldBoxPid).memory_info().rss) / 1024 / 1024, limitMemory), flush=True)
            return False
        # check cpu...
        # psutil.Process(9304).cpu_percent(0)
        # check alive duration
        if int(psutil.Process(dnplayerPid).create_time()) + limitDuration <= int(time.time()):
            print("%s createTime:%s;maxAliveTime:%s;nowTime:%s"%(deviceAttrList[1], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.Process(dnplayerPid).create_time())), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.Process(dnplayerPid).create_time() + limitDuration)), time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), flush=True)
            return False
        if int(psutil.Process(ldBoxPid).create_time()) + limitDuration <= int(time.time()):
            print("%s createTime:%s;maxAliveTime:%s;nowTime:%s"%(deviceAttrList[1], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.Process(ldBoxPid).create_time())), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.Process(ldBoxPid).create_time() + limitDuration)), time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), flush=True)
            return False
        # check hook app
        if checkHookApp(deviceAttrList) == False:
            print("%s checkHookApp Fail"%(deviceAttrList[1]), flush=True)
            return False
        # check Pac
        if checkPacFlag == True and checkPac(deviceAttrList) == False:
            print("%s checkPacFlag Fail" % (deviceAttrList[1]), flush=True)
            return False
        return True
    except Exception as e:
        print(e, flush=True)
        print("%s fuckCheckDeviceRunningHealth"%(deviceAttrList[1]), flush=True)
        return False

def old():
    while True:
        # set global device env
        subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0  --fastplay 1 --cleanmode 1")
        # check network
        # checkNetWork()
        # check many exception
        for proc in psutil.process_iter():
            try:
                # LdBoxSVC.exe || dnplayer.exe
                if "LdBoxHeadless.exe" == proc.name():
                    ldBoxProc = psutil.Process(proc.pid)
                    # find ldbox map controller
                    procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE)
                    objectDeviceAttrList = ""
                    for byteDevice in procList.stdout.splitlines():
                        stringDevice = str(byteDevice, encoding="gbk")
                        deviceAttrList = stringDevice.split(",")
                        if deviceAttrList[6] == str(ldBoxProc.pid):
                            objectDeviceAttrList = deviceAttrList
                            break
                    # check ldbox memory and running time and hook app run status
                    memoryOver = ldBoxProc.memory_info().rss / 1024 / 1024
                    if memoryOver >= 750 or int(ldBoxProc.create_time()) + 3600 <= int(
                            time.time()) or checkHookApp(objectDeviceAttrList) == False or checkPac(
                        objectDeviceAttrList) == False:
                        print("deviceStatus;memory:%dMB;createTime:%s;checkHookApp:%r;checkPac:%r" % (
                            memoryOver, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ldBoxProc.create_time())),
                            checkHookApp(objectDeviceAttrList), checkPac(
                                objectDeviceAttrList)),
                              flush=True)
                        restartDevice(objectDeviceAttrList)
            except Exception as e:
                if "AccessDenied" not in str(e):
                    print(e, flush=True)

        print("sleepAt:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), flush=True)

        time.sleep(60)


def new():
    while True:
        try:
            if reconnectNet == True:
                checkNetWork()
            subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0  --fastplay 1 --cleanmode 1", timeout=5)
            procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=5)
            for byteDevice in procList.stdout.splitlines():
                stringDevice = str(byteDevice, encoding="gbk")
                if checkExistNoOpenList(stringDevice) == True:
                    # no handle this device that name exist in noOpenList
                    continue
                deviceAttrList = stringDevice.split(",")
                # check device hardware
                if checkDeviceRunningHealth(deviceAttrList) == False:
                    restartDevice(deviceAttrList)
            print("sleepAt:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), flush=True)
            time.sleep(60)
        except Exception as e:
            print(e)





new()
