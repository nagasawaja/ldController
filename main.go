package main

import (
	"github.com/sirupsen/logrus"
	"os/exec"
)

var ldPath = "C:\\ChangZhi\\dnplayer2\\"
var ldConsole = ldPath + "ldconsole.exe"
var ld = ldPath + "ld.exe"

func main() {
	cmd := exec.Command(ldConsole, "globalsetting","--fps 20","--audio 0","--fastplay 1", "--cleanmode 1")
	logrus.Info(cmd.)
	out, err := cmd.CombinedOutput()
	if err != nil {
		logrus.Errorf("globalsettingFail;err:%s", err.Error())
		return
	}
	logrus.Infof("asd:%+v", string(out))
}