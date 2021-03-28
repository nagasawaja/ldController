# -- coding: utf-8 --
import os
import subprocess
import time
import datetime
import random
import string
import win32con
import win32gui
import randName
import psutil
import requests
import configparser
import json

cconfig = configparser.ConfigParser()


def initConfig():
    global cconfig
    cconfig.read("config.ini", encoding='UTF-8')


initConfig()
ldPath = cconfig["cc"]["ldpath"]
ldconsole = ldPath + cconfig["cc"]["ldconsole"]
ld = ldPath + cconfig["cc"]['ld']
backupAndRestorePath = ldPath + cconfig["cc"]['backupAndRestorePath']
lastReconnectTime = time.time()
noOpenList = json.loads(cconfig["cc"]['noOpenList'])
checkPacFlag = cconfig.getboolean("cc", "checkPacFlag")
reconnectNet = cconfig.getboolean("cc", "reconnectNet")
showWindowFlag = cconfig.getboolean("cc", "showWindowFlag")
sortWndFlag = cconfig.getboolean("cc", "sortWndFlag")
limitMemory = cconfig.getint("cc", "limitMemory")
limitCpu = cconfig.getint("cc", "limitCpu")
limitDuration = cconfig.getint("cc", "limitDuration")
deviceCpuNum = cconfig.getint("cc", "deviceCpuNum")
deviceMemoryNum = cconfig.getint("cc", "deviceMemoryNum")
resolutionModelList = json.loads(cconfig["cc"]['resolutionModelList'])
resolutionModel = cconfig.getint("cc", "resolutionModel")
backupAndRestoreDateMap = json.loads(cconfig["cc"]['backupAndRestoreDateMap'])
backupAndRestoreDateRecordMap = json.loads(cconfig["cc"]['backupAndRestoreDateRecordMap'])
deviceMaxFps = cconfig.getint("cc", "deviceMaxFps")
deviceAudio = cconfig.getint("cc", "deviceAudio")
deviceFastplay = cconfig.getint("cc", "deviceFastplay")
deviceCleanmode = cconfig.getint("cc", "deviceCleanmode")
checkCurrentFocusList = json.loads(cconfig["cc"]["checkCurrentFocusList"])
checkAppRunningList = json.loads(cconfig["cc"]["checkAppRunningList"])

mobileBrand = {"xiaomi": ["xiaomi6", "xiaomi8", "xiaomi9", "xiaomi10", "benija", "somi"],
               "google": ["googlePixel2", "googlePixel3", "fancy", "tom", "jack", "karsa"],
               "huawei": ["huaweiHonorV9", "huaweiHonorV10", "P30", "timi", "jimmy", "vanilla", "knight"],
               "vivo": ["vivoX9Plus", "vivoX10Plus", "uzi", "clear", "love777", "livezzz", "saiwen"],
               "oppo": ["oppoR11Plus", "oppoR10Plus", "oppoR12Plus", "xiaohua", "xiaoming", "chov", "dwgZ"],
               "meizu": ["meizuPRO6Plus", "meizuM8", "meizuPRO7Plus", "naguli", "faker", "fucker", "zoom"],
               "PHILIPS": [], "MOTOROLA": [], "SIEMENS": [], "SAMSUNG": [], "Coolpad": [], "koobee": [], "SHARP": [],
               "LG": [], "ZTE": [], "Oukitel": [], "Micromax": [], "LeEco": [], "Lumia": []}


def randomPhoneNumber():
    num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187',
                 '188',
                 '147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']
    start = random.choice(num_start)
    end = ''.join(random.sample(string.digits, 8))
    res = start + end
    return res


def checkDeviceRunning(deviceAttrList, runningStatus):
    try:
        for i in range(1, 40):
            # check device alive
            procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=10)
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
    subprocess.run(ldconsole + " quit --index %s" % (deviceAttrList[0]), timeout=10)
    print("%s deviceQuit!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    if killAllRelativeProcess(int(deviceAttrList[6]), int(deviceAttrList[5])) is False:
        return
    time.sleep(1)
    if checkDeviceRunning(deviceAttrList, "0") is False:
        return
    # set the device info
    randomManuFacturer = random.choice(list(mobileBrand))
    modifyParamsStr = ldconsole + " modify --index %s --manufacturer %s --model %s --pnumber %s --resolution %s,%s,%s --cpu %s --memory %s" % (
        deviceAttrList[0], randomManuFacturer, randName.gen_two_words("'"), randomPhoneNumber(),
        resolutionModelList[resolutionModel]["x"],
        resolutionModelList[resolutionModel]["y"], resolutionModelList[resolutionModel]["dpi"], deviceCpuNum,
        deviceMemoryNum)
    subprocess.run(modifyParamsStr, timeout=10)
    print("%s modifyDeviceParams!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    subprocess.run(ldconsole + " globalsetting --fps %s --audio %s --fastplay %s --cleanmode %s" % (
        deviceMaxFps, deviceAudio, deviceFastplay, deviceCleanmode), timeout=10)
    print("%s globalSetting!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(1)
    # run device
    # subprocess.run(ldconsole + " launchex --index %s --packagename \"com.touchsprite.android\"" % (deviceAttrList[0]),
    #                timeout=10)
    subprocess.run(ldconsole + " launch --index %s" % (deviceAttrList[0]), timeout=10)
    print("%s runDeviceBegin!!!" % (deviceAttrList[1]), flush=True)
    time.sleep(5)
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
    if checkCurrentActive(deviceAttrList, 30, "com.android.launcher3/.Launcher") is False:
        print("%s cannotRunMainActive!!!" % (deviceAttrList[1]))
        return
    print("%s runMainActive!!!" % (deviceAttrList[1]))
    time.sleep(3)
    # run touchSprite
    subprocess.run(ldconsole + " runapp --index %s --packagename com.touchsprite.android" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=10)
    if checkCurrentActive(deviceAttrList, 35, "com.touchsprite.android/.activity.MainActivity") is False:
        print("%s cannotRunTouchSprite!!!" % (deviceAttrList[1]))
        return
    print("%s runTouchSprite!!!" % (deviceAttrList[1]))
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value home" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=10)
    print("%s runHome!!!" % (deviceAttrList[1]))
    if checkCurrentActive(deviceAttrList, 15, "com.android.launcher3/.Launcher") is False:
        print("%s cannotRunMainActive2!!!" % (deviceAttrList[1]))
        return
    print("%s runMainActive2!!!" % (deviceAttrList[1]))
    time.sleep(5)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE, timeout=10)
    print("%s runScript!!!" % (deviceAttrList[1]))
    time.sleep(5)
    if sortWndFlag is True:
        subprocess.run(ldconsole + " sortWnd", timeout=10)
        print("%s runSortWnd!!!" % (deviceAttrList[1]))
        time.sleep(5)


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
            activeNameInFlag = False
            for tp in mResumeList:
                if activeName in str(tp, encoding="gbk"):
                    activeNameInFlag = True
                    break
            if activeNameInFlag is True:
                currentActiveFlag = True
                break
            for tp in mResumeList2:
                if activeName in str(tp, encoding="gbk"):
                    activeNameInFlag = True
                    break
            if activeNameInFlag is True:
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


def checkAppRunning(deviceAttrList):
    for appName in checkAppRunningList:
        try:
            appRunningCmd = subprocess.run(
                ld + " -s %s adb shell \" ps | grep %s\"" % (deviceAttrList[0], appName),
                stdout=subprocess.PIPE, timeout=10)
            appRunningCmd2 = subprocess.run(
                ldconsole + " adb --index %s --command \"shell ps | grep %s\"" % (
                    deviceAttrList[0], appName),
                stdout=subprocess.PIPE, timeout=10)
            appRunningPsList = appRunningCmd.stdout.splitlines()
            appRunningPsList2 = appRunningCmd2.stdout.splitlines()
            for l in appRunningPsList:
                if appName in str(l, encoding="gbk"):
                    return True
            for l in appRunningPsList2:
                if appName in str(l, encoding="gbk"):
                    return True
            print("%s %s not running" % (deviceAttrList[1], appName), flush=True)
            return False
        except Exception as e:
            print("checkAppRunning except exception", flush=True)
            print(e, flush=True)
            return False


def checkCurrentFocus(deviceAttrList):
    for checkCurrentFocusName in checkCurrentFocusList:
        try:
            for retryTimes in range(checkCurrentFocusList[checkCurrentFocusName]['retryTimes']):
                currentFocusCmd = subprocess.run(
                    ld + " -s %s adb shell \" dumpsys window windows | grep 'mCurrentFocus'\"",
                    stdout=subprocess.PIPE, timeout=10)
                currentFocusCmd2 = subprocess.run(
                    ldconsole + " adb --index %s --command \"shell dumpsys window windows | grep 'mCurrentFocus'\"",
                    stdout=subprocess.PIPE, timeout=10)
                currentFocusPsList = currentFocusCmd.stdout.splitlines()
                currentFocusPsList2 = currentFocusCmd2.stdout.splitlines()
                for l in currentFocusPsList:
                    if checkCurrentFocusName in str(l, encoding="gbk"):
                        return True
                for l in currentFocusPsList2:
                    if checkCurrentFocusName in str(l, encoding="gbk"):
                        return True
                print("%s %s is not focus, retryTimes:%s" % (deviceAttrList[1], checkCurrentFocusName, retryTimes),
                      flush=True)
                time.sleep(1)
            return False
        except Exception as e:
            print("checkCurrentFocus except exception", flush=True)
            print(e, flush=True)
            return False


def killLeiDianGameCenter(deviceAttrList):
    try:
        leiDianGameCenterCmd = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.android.flysilkworm\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
        leiDianGameCenterCmd2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.android.flysilkworm\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
        leiDianGameCenterPsList = leiDianGameCenterCmd.stdout.splitlines()
        leiDianGameCenterPsList2 = leiDianGameCenterCmd2.stdout.splitlines()
        for l in leiDianGameCenterPsList:
            if "com.android.flysilkworm" in str(l, encoding="gbk"):
                print("%s killLeiDianGameCenter" % (deviceAttrList[1]), flush=True)
                subprocess.run(
                    ld + " -s %s adb shell \" kill -9 %s\"" % (deviceAttrList[0], l.split()[1].decode('utf-8')),
                    stdout=subprocess.PIPE, timeout=10)
                return True
        for l in leiDianGameCenterPsList2:
            if "com.android.flysilkworm" in str(l, encoding="gbk"):
                print("%s killLeiDianGameCenter2" % (deviceAttrList[1]), flush=True)
                subprocess.run(
                    ldconsole + " adb --index %s --command \"shell kill -9 %s\"" % (
                        deviceAttrList[0], l.split()[1].decode('utf-8')),
                    stdout=subprocess.PIPE, timeout=10)
                return True

    except Exception as e:
        print("killLeiDianGameCenterFail", flush=True)
        print(e, flush=True)
        return False


def checkPac(deviceAttrList):
    if "NewAccount" not in deviceAttrList[1]:
        return True
    try:
        id5HookStatus = subprocess.run(
            ld + " -s %s adb shell \" ps | grep com.android.pacprocessor\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
        id5HookStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell ps | grep com.android.pacprocessor\"" % (
                deviceAttrList[0]),
            stdout=subprocess.PIPE, timeout=10)
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
        # check device running status
        if runningStatus != "1":
            return False
        # check device pid exists...device display
        if psutil.pid_exists(dnplayerPid) is False:
            print("%s dnplayerPid device display not exist" % (deviceAttrList[1]), flush=True)
            return False
        # check divce pid exists...device service
        if psutil.pid_exists(ldBoxPid) is False:
            print("%s ldboxPid device service not exist" % (deviceAttrList[1]), flush=True)
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
        # check app running
        if checkAppRunning(deviceAttrList) is False:
            print("%s check app running Fail" % (deviceAttrList[1]), flush=True)
            return False
        # check current focus
        if checkCurrentFocus(deviceAttrList) is False:
            print("%s check current focus Fail" % (deviceAttrList[1]), flush=True)
            return False
        # check Pac
        if checkPacFlag == True and checkPac(deviceAttrList) == False:
            print("%s checkPacFlag Fail" % (deviceAttrList[1]), flush=True)
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
    newPhone = phone.replace(list, '****')

    return newPhone


def killAllRelativeProcess(ldBoxPid, dnPlayerPid):
    try:
        if psutil.pid_exists(ldBoxPid) is True:
            p = psutil.Process(ldBoxPid)
            for child in p.children():
                child.kill()
            p.kill()

        if psutil.pid_exists(dnPlayerPid) is True:
            psutil.Process(dnPlayerPid).kill()
        return True
    except Exception as e:
        print(e, flush=True)
        print("killAllRelativeProcessFail", flush=True)
        return False


def getDeviceAttrList(deviceIndex):
    try:
        procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=10)
        for byteDevice in procList.stdout.splitlines():
            stringDevice = str(byteDevice, encoding="gbk")
            deviceAttrList = stringDevice.split(",")
            if deviceAttrList[0] == deviceIndex:
                return deviceAttrList
    except Exception as e:
        print(e, flush=True)
        print("getDeviceAttrListFail", flush=True)
        return False


def backupDevice(deviceAttrList):
    if deviceAttrList[0] not in backupAndRestoreDateRecordMap["backup"]:
        backupAndRestoreDateRecordMap['backup'][deviceAttrList[0]] = {}
    # assert weekday
    nowWeekday = datetime.date.today().isoweekday()
    if nowWeekday != backupAndRestoreDateMap["backup"]["week"]:
        return
    # assert hour
    nowHour = datetime.datetime.now().hour
    if nowHour < backupAndRestoreDateMap["backup"]["hour"]:
        return
    # assert backup yet
    if datetime.date.today().strftime("%Y-%m-%d") in backupAndRestoreDateRecordMap["backup"][deviceAttrList[0]]:
        print("%s in %s backupYet!!!" % (deviceAttrList[1], datetime.date.today().strftime("%Y-%m-%d")), flush=True)
        return
    # quit all device
    print("restore quit all device and sleep 20s!!!", flush=True)
    subprocess.run(ldconsole + " quitall", timeout=10)
    # wait device actually exit
    time.sleep(20)
    procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=10)
    for byteDevice in procList.stdout.splitlines():
        stringDevice = str(byteDevice, encoding="gbk")
        if checkExistNoOpenList(stringDevice) is True:
            # no handle this device that name exist in noOpenList
            continue
        deviceAttrList = stringDevice.split(",")
        try:
            # begin backup
            newBackupFile = "%s/%s.backup.ldbk" % (backupAndRestorePath, deviceAttrList[0])
            print(newBackupFile + " beginBackup", flush=True)
            subprocess.run(ldconsole + " backup --index %s --file %s" % (
                deviceAttrList[0], newBackupFile), timeout=100)
            # backup suc, remove old backup file
            oldBackupFile = "%s/%s.ldbk" % (backupAndRestorePath, deviceAttrList[0])
            if os.path.exists(oldBackupFile) == True:
                # exist
                os.remove(oldBackupFile)
            os.rename(newBackupFile, oldBackupFile)
            # write backup record to file cache
            fWrite = open("backupRecord.txt", "w")
            fWrite.write(str(backupAndRestoreDateRecordMap))
            fWrite.close()
            # suc and return true
            backupAndRestoreDateRecordMap["backup"][deviceAttrList[0]][
                datetime.date.today().strftime("%Y-%m-%d")] = True
            print("%s backupSuc!!!" % (deviceAttrList[1]), flush=True)
        except Exception as e:
            print("backupFail", flush=True)
            print(e, flush=True)
            time.sleep(120)
            return False
    return "restart"


def restoreDevice(deviceAttrList):
    if deviceAttrList[0] not in backupAndRestoreDateRecordMap["restore"]:
        backupAndRestoreDateRecordMap['restore'][deviceAttrList[0]] = {}
    # assert weekday
    nowWeekday = datetime.date.today().isoweekday()
    if nowWeekday != backupAndRestoreDateMap["restore"]["week"]:
        return
    # assert hour
    nowHour = datetime.datetime.now().hour
    if nowHour < backupAndRestoreDateMap["restore"]["hour"]:
        return
    # assert backup yet
    if datetime.date.today().strftime("%Y-%m-%d") in backupAndRestoreDateRecordMap["restore"][deviceAttrList[0]]:
        print("%s in %s restoreYet!!!" % (deviceAttrList[1], datetime.date.today().strftime("%Y-%m-%d")), flush=True)
        return
    # quit all device
    print("restore quit all device and sleep 20s!!!", flush=True)
    subprocess.run(ldconsole + " quitall", timeout=10)
    # wait device actually exit
    time.sleep(20)
    procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=10)
    for byteDevice in procList.stdout.splitlines():
        stringDevice = str(byteDevice, encoding="gbk")
        if checkExistNoOpenList(stringDevice) is True:
            # no handle this device that name exist in noOpenList
            continue
        deviceAttrList = stringDevice.split(",")
        try:
            # begin restore
            # check restore file exist
            restoreFile = "%s/%s.ldbk" % (backupAndRestorePath, deviceAttrList[0])
            print(restoreFile + " begin restore")
            if os.path.exists(restoreFile) == False:
                print("%s restoreFailNotExist!!!" % (restoreFile), flush=True)
                continue
            subprocess.run(ldconsole + " restore --index %s --file %s" % (deviceAttrList[0], restoreFile), timeout=100)
            backupAndRestoreDateRecordMap["restore"][deviceAttrList[0]][
                datetime.date.today().strftime("%Y-%m-%d")] = True
            print("%s restoreSuc!!!" % (deviceAttrList[1]), flush=True)
        except Exception as e:
            print("restoreFail", flush=True)
            print(e, flush=True)
            time.sleep(120)
            return False
    return "restart"


def loadBackupAndRestoreDateRecordMapFileCache():
    if os.path.exists("backupRecord.txt") == False:
        return
    fRead = open("backupRecord.txt", "r")
    body = fRead.read(-1)
    global backupAndRestoreDateRecordMap
    backupAndRestoreDateRecordMap = eval(body)
    fRead.close()
    return


def new():
    # load backup cache
    loadBackupAndRestoreDateRecordMapFileCache()
    while True:
        try:
            if reconnectNet is True:
                checkNetWork()
            procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE, timeout=10)
            for byteDevice in procList.stdout.splitlines():
                stringDevice = str(byteDevice, encoding="gbk")
                if checkExistNoOpenList(stringDevice) is True:
                    # no handle this device that name exist in noOpenList
                    continue
                deviceAttrList = stringDevice.split(",")
                # backup device
                if backupDevice(deviceAttrList) == "restart":
                    break
                # restore device
                if restoreDevice(deviceAttrList) == "restart":
                    break
                # check device hardware
                # eample:['0', '雷电模拟器', '2364406', '790452', '1', '24916', '17032']
                if checkDeviceRunningHealth(deviceAttrList) is False:
                    restartDevice(deviceAttrList)
            print("sleepAt:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), flush=True)
            time.sleep(60)
        except Exception as e:
            print(e)


new()
