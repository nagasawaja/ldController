# -- coding: utf-8 --
import os
import subprocess
import time
import random
import string
import randName

import psutil
import requests

ldPath = "C:\ChangZhi\dnplayer2\\"
ldconsole = ldPath + "ldconsole.exe"
ld = ldPath + "ld.exe"
lastReconnectTime = time.time()
noOpenList = ["laji"]
limitMemory = 1024
limitCpu = 180
limitDuration = 3600
checkPacFlag = False
reconnectNet = False
mobileBrand = {"xiaomi":["xiaomi6", "xiaomi8", "xiaomi9", "xiaomi10","benija", "somi"],
               "google":["googlePixel2", "googlePixel3","fancy","tom", "jack", "karsa"],
               "huawei":["huaweiHonorV9", "huaweiHonorV10", "P30","timi", "jimmy", "vanilla", "knight"],
               "vivo":["vivoX9Plus", "vivoX10Plus","uzi","clear", "love777","livezzz", "saiwen"],
               "oppo":["oppoR11Plus", "oppoR10Plus", "oppoR12Plus","xiaohua","xiaoming","chov","dwgZ"],
               "meizu":["meizuPRO6Plus", "meizuM8", "meizuPRO7Plus","naguli","faker","fucker","zoom"],
               "PHILIPS":[],"MOTOROLA":[],"SIEMENS":[],"SAMSUNG":[],"Coolpad":[],"koobee":[],"SHARP":[]}


def randomPhoneNumber():

    all_phone_nums=set()
    num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187', '188',
    '147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']

    start = random.choice(num_start)
    end = ''.join(random.sample(string.digits,8))
    res = start+end+'\n'
    return res


def checkDeviceRunning(deviceAttrList, runningStatus):
    for i in range(1, 40):
        # check device alive
        procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=5)
        time.sleep(1)
        if str(procList.stdout.splitlines()[int(deviceAttrList[0])], encoding="gbk").split(",")[4] == runningStatus:
            return
    print("%s device running status %sfail!!!" % (deviceAttrList[1], runningStatus), flush=True)
    return


def restartDevice(deviceAttrList):
    # running
    subprocess.run(ldconsole + " quit  --index %s" % (deviceAttrList[0]), timeout=5)
    print("%s quit!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(3)
    if checkDeviceRunning(deviceAttrList, "0") == False:
        return

    # set the device info
    randomManuFacturer = random.choice(list(mobileBrand))
    subprocess.run(ldconsole + " modify --index %s --manufacturer %s --model %s --pnumber %s --resolution 480,320,160 --cpu 1 --memory 1024" % (deviceAttrList[0],randomManuFacturer,randName.gen_two_words("'"), randomPhoneNumber()),timeout=5)
    print("%s modify!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(3)

    # run device
    subprocess.run(ldconsole + " launchex --index %s --packagename \"com.touchsprite.android\"" % (deviceAttrList[0]), timeout=5)
    print("%s launch!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(3)
    if checkDeviceRunning(deviceAttrList, "1") == False:
        return
    print("%s run device!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
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
    # subprocess.run(ldconsole + " sortWnd", timeout=5)
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
            stdout=subprocess.PIPE, timeout=5)
        id5HookStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.example.id5hook\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
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
            stdout=subprocess.PIPE, timeout=5)
        id5HookStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.android.pacprocessor\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
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
        cpuPercent = psutil.Process(ldBoxPid).cpu_percent(interval=1)
        if cpuPercent >= limitCpu:
            print("%s cpuPercent over %d" % (deviceAttrList[1], limitCpu), flush=True)
            return False
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


def phonelist1(phone):
    # 取出中间四位
    list = phone[3:7]
    # 加密
    newphone = phone.replace(list, '****')

    return newphone


def new():
    while True:
        try:
            if reconnectNet == True:
                checkNetWork()
            # subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0  --fastplay 1 --cleanmode 1", timeout=5)
            subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0   --cleanmode 1", timeout=5)
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