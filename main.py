# -- coding: utf-8 --
import os
import subprocess
import time
import random
import string

import win32con
import win32gui

import randName
import psutil
import requests

ldPath = "C:\ChangZhi\dnplayer2\\"
ldconsole = ldPath + "ldconsole.exe "
ld = ldPath + "ld.exe"
lastReconnectTime = time.time()
noOpenList = ["laji"]
limitMemory = 2048
limitCpu = 250
limitDuration = 5000
checkPacFlag = False
reconnectNet = False
showWindowFlag = True
sortWndFlag = False
deviceCpuNum = 2
deviceMemoryNum = 2048
mobileBrand = {"xiaomi": ["xiaomi6", "xiaomi8", "xiaomi9", "xiaomi10", "benija", "somi"],
               "google": ["googlePixel2", "googlePixel3", "fancy", "tom", "jack", "karsa"],
               "huawei": ["huaweiHonorV9", "huaweiHonorV10", "P30", "timi", "jimmy", "vanilla", "knight"],
               "vivo": ["vivoX9Plus", "vivoX10Plus", "uzi", "clear", "love777", "livezzz", "saiwen"],
               "oppo": ["oppoR11Plus", "oppoR10Plus", "oppoR12Plus", "xiaohua", "xiaoming", "chov", "dwgZ"],
               "meizu": ["meizuPRO6Plus", "meizuM8", "meizuPRO7Plus", "naguli", "faker", "fucker", "zoom"],
               "PHILIPS": [], "MOTOROLA": [], "SIEMENS": [], "SAMSUNG": [], "Coolpad": [], "koobee": [], "SHARP": []}


def randomPhoneNumber():
    all_phone_nums = set()
    num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187',
                 '188',
                 '147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']

    start = random.choice(num_start)
    end = ''.join(random.sample(string.digits, 8))
    res = start + end + '\n'
    return res


def checkDeviceRunning(deviceAttrList, runningStatus):
    try:
        for i in range(1, 40):
            # check device alive
            procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=5)
            time.sleep(1)
            if str(procList.stdout.splitlines()[int(deviceAttrList[0])], encoding="gbk").split(",")[4] == runningStatus:
                return True
        print("%s device running status %sfail!!!" % (deviceAttrList[1], runningStatus), flush=True)
        return False
    except Exception as e:
        print("checkDeviceRunningFail", flush=True)
        print(e, flush=True)
        return False


def hideDeviceWindow(deviceAttrList):
    try:
        win32gui.ShowWindow(int(deviceAttrList[2]), win32con.SW_MINIMIZE)
        return True
    except Exception as e:
        print("showDeviceWindowFail", flush=True)
        print(e, flush=True)
        return False


def restartDevice(deviceAttrList):
    # running
    subprocess.run(ldconsole + " quit --index %s" % (deviceAttrList[0]), timeout=5)
    print("%s deviceQuit!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    if killAllRelativeProcess(int(deviceAttrList[6]), int(deviceAttrList[5])) is False:
        return
    time.sleep(1)
    if checkDeviceRunning(deviceAttrList, "0") is False:
        return
    # set the device info
    randomManuFacturer = random.choice(list(mobileBrand))
    modifyParamsStr = ldconsole + " modify --index %s --manufacturer %s --model %s --pnumber %s --resolution 480,320,160 --cpu %s --memory %s" % (
        deviceAttrList[0], randomManuFacturer, randName.gen_two_words("'"), randomPhoneNumber(), deviceCpuNum,
        deviceMemoryNum)
    subprocess.run(modifyParamsStr, timeout=5)
    print("%s modifyDeviceParams!!!" % (deviceAttrList[1], modifyParamsStr), flush=True)
    time.sleep(1)
    # subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0  --fastplay 1 --cleanmode 1", timeout=5)
    subprocess.run(ldconsole + " globalsetting --fps 10 --audio 0   --cleanmode 1", timeout=5)
    print("%s globalSetting!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    # run device
    # subprocess.run(ldconsole + " launchex --index %s --packagename \"com.touchsprite.android\"" % (deviceAttrList[0]),
    #                timeout=5)
    subprocess.run(ldconsole + "launch --index %s" % (deviceAttrList[0]), timeout=5)
    print("%s runDeviceBegin!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    deviceAttrList = getDeviceAttrList(deviceAttrList[0])
    if deviceAttrList is False:
        return
    if int(deviceAttrList[2]) == 0:
        print("%s devicePidIsZero!!!" % (deviceAttrList[1]), flush=True)
        return
    if showWindowFlag is False:
        print("%s hideDevice!!!" % (deviceAttrList[1]), flush=True)
        hideDeviceWindow(deviceAttrList)

    if checkDeviceRunning(deviceAttrList, "1") is False:
        return
    print("%s runDeviceSuc!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(3)
    # mFocusedActivity => mResume，maybe different android version ，mResume is current mainActive
    if checkCurrentActive(deviceAttrList, 20, "com.android.launcher3/.Launcher") is False:
        print("%s cannotRunMainActive!!!" % (deviceAttrList[1]))
        return
    print("%s runMainActive!!!" % (deviceAttrList[1]))
    time.sleep(3)
    # run touchSprite
    subprocess.run(ldconsole + " runapp --index %s --packagename com.touchsprite.android" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=5)
    if checkCurrentActive(deviceAttrList, 10, "com.touchsprite.android/.activity.MainActivity") is False:
        print("%s cannotRunTouchSprite!!!" % (deviceAttrList[1]))
        return
    print("%s runTouchSprite!!!" % (deviceAttrList[1]))
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value home" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=5)
    print("%s runHome!!!" % (deviceAttrList[1]))
    if checkCurrentActive(deviceAttrList, 10, "com.android.launcher3/.Launcher") is False:
        print("%s cannotRunMainActive2!!!" % (deviceAttrList[1]))
        return
    print("%s runMainActive2!!!" % (deviceAttrList[1]))
    time.sleep(3)
    if sortWndFlag is True:
        subprocess.run(ldconsole + " sortWnd", timeout=5)
        print("%s runSortWnd!!!" % (deviceAttrList[1]))
        time.sleep(5)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=5)
    print("%s runScript!!!" % (deviceAttrList[1]))
    time.sleep(2)


def checkCurrentActive(deviceAttrList, retryTimes, activeName):
    try:
        currentActiveFlag = False
        for i in range(1, retryTimes):
            runStatus = subprocess.run(
                ld + " -s %s adb shell \" dumpsys activity activities | grep mResume\"" % (deviceAttrList[0]),
                stdout=subprocess.PIPE, timeout=10)
            runStatus2 = subprocess.run(
                ldconsole + " adb --index %s --command \"shell dumpsys activity activities | grep mResume\"" % (
                    deviceAttrList[0]),
                stdout=subprocess.PIPE, timeout=10)
            mResumeList = runStatus.stdout.splitlines()
            mResumeList2 = runStatus2.stdout.splitlines()
            tpInFlag = False
            for tp in mResumeList:
                if activeName in str(tp, encoding="gbk"):
                    tpInFlag = True
                    break
            if tpInFlag == True:
                currentActiveFlag = True
                break
            for tp in mResumeList2:
                if activeName in str(tp, encoding="gbk"):
                    tpInFlag = True
                    break
            if tpInFlag == True:
                currentActiveFlag = True
                break
            time.sleep(1)
        return currentActiveFlag
    except Exception as e:
        print("checkCurrentActiveFail", flush=True)
        print(e, flush=True)
        return False


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


def killLeiDianGameCenter(deviceAttrList):
    try:
        leiDianGameCenterCmd = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.android.flysilkworm\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
        leiDianGameCenterCmd2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.android.flysilkworm\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
        leiDianGameCenterPsList = leiDianGameCenterCmd.stdout.splitlines()
        leiDianGameCenterPsList2 = leiDianGameCenterCmd2.stdout.splitlines()
        for l in leiDianGameCenterPsList:
            if "com.android.flysilkworm" in str(l, encoding="gbk"):
                print("%s killLeiDianGameCenter" % (deviceAttrList[1]), flush=True)
                subprocess.run(
                    ld + " -s %s adb shell \" kill -9 %s\"" % (deviceAttrList[0], l.split()[1].decode('utf-8')),
                    stdout=subprocess.PIPE, timeout=5)
                return True
        for l in leiDianGameCenterPsList2:
            if "com.android.flysilkworm" in str(l, encoding="gbk"):
                print("%s killLeiDianGameCenter2" % (deviceAttrList[1]), flush=True)
                subprocess.run(
                    ldconsole + " adb --index %s --command \"shell kill -9 %s\"" % (
                        deviceAttrList[0], l.split()[1].decode('utf-8')),
                    stdout=subprocess.PIPE, timeout=5)
                return True

    except Exception as e:
        print("killLeiDianGameCenterFail", flush=True)
        print(e, flush=True)
        return False


def checkTouchSprite(deviceAttrList):
    try:
        touchspriteCmd = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.touchsprite.android\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
        touchspriteCmd2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.touchsprite.android\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=5)
        touchspritePsList = touchspriteCmd.stdout.splitlines()
        touchspritePsList2 = touchspriteCmd2.stdout.splitlines()
        for l in touchspritePsList:
            if "com.touchsprite.android" in str(l, encoding="gbk"):
                # print("%s touchspriteSuc" % (deviceAttrList[1]), flush=True)
                return True
        for l in touchspritePsList2:
            if "com.touchsprite.android" in str(l, encoding="gbk"):
                # print("%s touchspriteSuc2" % (deviceAttrList[1]), flush=True)
                return True

        print("%s touchspriteFail" % (deviceAttrList[1]), flush=True)
        return False
    except Exception as e:
        print("touchspriteFail2", flush=True)
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
            print("%s ldboxPid not exist" % (deviceAttrList[1]), flush=True)
            return False
        # check memory
        if (psutil.Process(dnplayerPid).memory_info().rss + psutil.Process(
                ldBoxPid).memory_info().rss) / 1024 / 1024 > limitMemory:
            print("%s memory:%dMB;limitMemory:%dMB" % (deviceAttrList[1], (
                    psutil.Process(dnplayerPid).memory_info().rss + psutil.Process(
                ldBoxPid).memory_info().rss) / 1024 / 1024, limitMemory), flush=True)
            return False
        # check cpu...
        cpuPercent = psutil.Process(ldBoxPid).cpu_percent(interval=1)
        if cpuPercent >= limitCpu:
            print("%s cpuPercent over %d" % (deviceAttrList[1], limitCpu), flush=True)
            return False
        # check alive duration
        if int(psutil.Process(dnplayerPid).create_time()) + limitDuration <= int(time.time()):
            print("%s createTime:%s;maxAliveTime:%s;nowTime:%s" % (deviceAttrList[1], time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                                    time.localtime(
                                                                                                        psutil.Process(
                                                                                                            dnplayerPid).create_time())),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                                                                       psutil.Process(
                                                                           dnplayerPid).create_time() + limitDuration)),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                 time.localtime())), flush=True)
            return False
        if int(psutil.Process(ldBoxPid).create_time()) + limitDuration <= int(time.time()):
            print("%s createTime:%s;maxAliveTime:%s;nowTime:%s" % (deviceAttrList[1], time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                                    time.localtime(
                                                                                                        psutil.Process(
                                                                                                            ldBoxPid).create_time())),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                                                                       psutil.Process(
                                                                           ldBoxPid).create_time() + limitDuration)),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                 time.localtime())), flush=True)
            return False
        # check hook app
        if checkHookApp(deviceAttrList) == False:
            print("%s checkHookApp Fail" % (deviceAttrList[1]), flush=True)
            return False
        # check Pac
        if checkPacFlag == True and checkPac(deviceAttrList) == False:
            print("%s checkPacFlag Fail" % (deviceAttrList[1]), flush=True)
            return False
        # check touchSprite
        if checkTouchSprite(deviceAttrList) == False:
            print("%s checkTouchSprite Fail" % (deviceAttrList[1]), flush=True)
            return False
        return True
    except Exception as e:
        print(e, flush=True)
        print("%s fuckCheckDeviceRunningHealth" % (deviceAttrList[1]), flush=True)
        return False


def phonelist1(phone):
    # 取出中间四位
    list = phone[3:7]
    # 加密
    newphone = phone.replace(list, '****')

    return newphone


def killAllRelativeProcess(ldBoxPid, dnPlayerPid):
    try:
        if psutil.pid_exists(ldBoxPid) == True:
            p = psutil.Process(ldBoxPid)
            for child in p.children():
                child.kill()
            p.kill()

        if psutil.pid_exists(dnPlayerPid) == True:
            psutil.Process(dnPlayerPid).kill()
        return True
    except Exception as e:
        print(e, flush=True)
        print("killAllRelativeProcessFail", flush=True)
        return False


def getDeviceAttrList(deviceIndex):
    try:
        procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=5)
        for byteDevice in procList.stdout.splitlines():
            stringDevice = str(byteDevice, encoding="gbk")
            deviceAttrList = stringDevice.split(",")
            if deviceAttrList[0] == deviceIndex:
                return deviceAttrList
    except Exception as e:
        print(e, flush=True)
        print("getDeviceAttrListFail", flush=True)
        return False


def new():
    while True:
        try:
            if reconnectNet == True:
                checkNetWork()
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