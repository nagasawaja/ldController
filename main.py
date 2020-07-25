import subprocess
import time
import psutil


ldPath = "C:\ChangZhi\dnplayer2\\"
ldconsole = ldPath + "ldconsole.exe"
ld = ldPath + "ld.exe"

def handleRunningDevice(deviceAttrList):
    # running
    subprocess.run(
        ldconsole + " action --index %s --key call.reboot --value com.touchsprite.android" % (deviceAttrList[0]))
    time.sleep(5)
    deviceAliveFlag = False
    for i in range(1, 60):
        # check device alive
        bbb = subprocess.run(ld + " -s %s adb get-state" % (deviceAttrList[0]), stdout=subprocess.PIPE)
        bbb2 = subprocess.run(ldconsole + " adb --index %s --command \"get-state\"" % (deviceAttrList[0]),
                              stdout=subprocess.PIPE)
        print("%s wake up retryTime:%d" % (deviceAttrList[1], i))
        time.sleep(1)
        if str(bbb.stdout.lower().splitlines()[0], encoding="gbk") == "device" or str(
                bbb2.stdout.lower().splitlines()[0], encoding="gbk") == "device":
            deviceAliveFlag = True
            break
    if deviceAliveFlag == False:
        print("%s cannot run device!!!" % (deviceAttrList[1]))
        return
    print("%s run device!!!" % (deviceAttrList[1]))
    touchSpriteFlag = False
    for i in range(1, 60):
        touchSpriteRunStatus = subprocess.run(
            ld + " -s %s adb shell \"ps | grep com.touchsprite.android\"" % (deviceAttrList[0]), stdout=subprocess.PIPE)
        touchSpriteRunStatus2 = subprocess.run(
            ldconsole + " adb --index %s --command  \"shell ps | grep com.touchsprite.android\"" % (deviceAttrList[0]),
            stdout=subprocess.PIPE)
        touchSpritePsList = touchSpriteRunStatus.stdout.splitlines()
        touchSpritePsList2 = touchSpriteRunStatus2.stdout.splitlines()
        tpInFlag = False
        for tp in touchSpritePsList:
            if str(tp, encoding="gbk") in "touchsprite":
                tpInFlag = True
                break
        if tpInFlag == True:
            touchSpriteFlag = True
            break
        for tp in touchSpritePsList2:
            if str(tp, encoding="gbk") in "touchsprite":
                tpInFlag = True
                break
        if tpInFlag == True:
            touchSpriteFlag = True
            break
    if touchSpriteFlag == False:
        print("%s cannot run touchSprite!!!" % (deviceAttrList[1]))
        return
    print(print("%s run touchSprite!!!" % (deviceAttrList[1])))
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value home" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE)
    time.sleep(3)
    subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown" % (deviceAttrList[0]),
                   stdout=subprocess.PIPE)
    time.sleep(2)

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
            subprocess.run(ldconsole + " launch --index %s"%(deviceAttrList[0]))
            subprocess.run(ldconsole + " runapp --index %s com.touchsprite.android"%(deviceAttrList[0]))
            subprocess.run(ldconsole + " action --index %s --key call.keyboard --value volumedown"%(deviceAttrList[0]))
        else:
            handleRunningDevice(deviceAttrList)


# while True:
#     restartDevice()
#     time.sleep(3600)

while True:
    for proc in psutil.process_iter():
        try:
            # LdBoxSVC.exe || dnplayer.exe
            if "LdBoxHeadless.exe" == proc.name():
                ldBoxProc = psutil.Process(proc.pid)
                if ldBoxProc.memory_info().rss / 1024/1024 >= 800:
                    procList = subprocess.run(ldconsole + " list2", stdout=subprocess.PIPE)
                    for byteDevice in procList.stdout.splitlines():
                        stringDevice = str(byteDevice, encoding="gbk")
                        deviceAttrList = stringDevice.split(",")
                        if deviceAttrList[6] == str(ldBoxProc.pid):
                            handleRunningDevice(deviceAttrList)
                            subprocess.run(ldconsole + " sortWnd")
        except Exception:
            print("fuckProcException")

    print("sleepAt:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    time.sleep(60)