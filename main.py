import subprocess
import time
import psutil

ldPath = "C:\ChangZhi\dnplayer2\\"
ldconsole = ldPath + "ldconsole.exe"
ld = ldPath + "ld.exe"


def handleRunningDevice(deviceAttrList):
    # running
    print("%s run begin!!!" % (deviceAttrList[1]))
    subprocess.run(
        ldconsole + " action --index %s --key call.reboot --value com.touchsprite.android" % (deviceAttrList[0]))
    time.sleep(18)
    deviceAliveFlag = False
    for i in range(1, 10):
        # check device alive
        procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE)
        # print("%s wake up retryTime:%d" % (deviceAttrList[1], i))
        time.sleep(1)

        if str(procList.stdout.splitlines()[int(deviceAttrList[0])], encoding="gbk").split(",")[4] == "1":
            deviceAliveFlag = True
            break
    if deviceAliveFlag == False:
        print("%s cannot run device!!!" % (deviceAttrList[1]))
        return
    print("%s run device!!!" % (deviceAttrList[1]))
    touchSpriteFlag = False
    for i in range(1, 10):
        touchSpriteRunStatus = subprocess.run(
            ld + " -s %s adb shell \" dumpsys activity activities | grep mFocusedActivity\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE)
        touchSpriteRunStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command \"shell dumpsys activity activities | grep mFocusedActivity\"" % (
            deviceAttrList[0]),
            stdout=subprocess.PIPE)
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
                   stdout=subprocess.PIPE)
    print("%s run home!!!" % (deviceAttrList[1]))
    time.sleep(4)
    subprocess.run(ldconsole + " sortWnd")
    print("%s run sortWnd!!!" % (deviceAttrList[1]))
    time.sleep(2)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE)
    print("%s run script!!!" % (deviceAttrList[1]))
    print("%s run end!!!" % (deviceAttrList[1]))


def restartDevice():
    subprocess.run(ldconsole + " globalsetting --fps 20 --audio 0  --fastplay 1 --cleanmode 1")
    aa = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE)

    for byteDevice in aa.stdout.splitlines():
        stringDevice = str(byteDevice, encoding="gbk")
        deviceAttrList = stringDevice.split(",")
        if deviceAttrList[1] in "naga":
            continue
        if deviceAttrList[2] == "0":
            # not running
            subprocess.run(ldconsole + " launch --index %s" % (deviceAttrList[0]))
            subprocess.run(ldconsole + " runapp --index %s com.touchsprite.android" % (deviceAttrList[0]))
            subprocess.run(
                ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]))
        else:
            handleRunningDevice(deviceAttrList)


while True:
    for proc in psutil.process_iter():
        try:
            # LdBoxSVC.exe || dnplayer.exe
            if "LdBoxHeadless.exe" == proc.name():
                ldBoxProc = psutil.Process(proc.pid)
                if ldBoxProc.memory_info().rss / 1024 / 1024 >= 600 or int(proc.create_time()) + 1800 <= int(time.time()):
                    procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE)
                    for byteDevice in procList.stdout.splitlines():
                        stringDevice = str(byteDevice, encoding="gbk")
                        deviceAttrList = stringDevice.split(",")
                        if deviceAttrList[6] == str(ldBoxProc.pid):
                            handleRunningDevice(deviceAttrList)
        except Exception as e:
            if "AccessDenied" not in str(e):
                print(e)


    print("sleepAt:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    time.sleep(60)
