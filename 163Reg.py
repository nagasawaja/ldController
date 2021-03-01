# -*- coding:utf-8 -*-
import urllib.request as urllib2, time, http.cookiejar, random, urllib;

cookiedict = {};


def encode(a):
    q = 10;
    w = a;
    m = len(w);
    b = int(time.time() * 1000)
    #    b = 1406081721783
    c = b % q;
    h = (b - c) / q;
    if c < 1:
        c = 1;
    c = b % q;
    d = b % (q * q);
    h = (b - d) / q;
    h = h / q;
    d = (d - c) / q;
    z = str(b) + "";
    p = z[q];
    g = str(c) + "" + str(d) + "" + str(p);
    l = int(g);
    e = l * int(w);
    x = str(e) + "";
    k = "";
    for n in range(len(str(e)) - 1, -1, -1):
        o = x[n];
        k = k + o;
    i = p + k + str(d) + str(c);
    u = i;
    return u;


def getjstime():
    return str(int(time.time() * 1000));


def getrandom():
    a = int(random.random() * 26);
    return a;


def getrandomalpha():
    return chr(random.randint(97, 122));


def getwords():
    words = "";
    for i in range(6):
        words = words + getrandomalpha();
    return words


def getCookieByNameNoCache(cj, name):
    global cookiedict;
    cookiedict = {};
    getCookieByName(cj, name);


def getCookieByName(cj, name):
    if not cookiedict.has_key(name):
        for index, cookie in enumerate(cj):
            print
            cookie.name, '-------------->', cookie.value
            if cookie.name == name:
                cookiedict[name] = cookie.value;
                return cookie.value;
    else:
        return cookiedict[name];



# 中文注释
if __name__ == '__main__':
    print("url connect start");
    # url = "https://login.vancl.com/Controls/CalculateValidateCode.ashx?key=15140570217&t="+str(int(time.time()*1000));
    url = "http://reg.email.163.com/unireg/call.do?cmd=register.entrance&from=126mail";
    #cj = cookielib.CookieJar();
    cj = http.cookiejar.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj));
    headers = [{'User-Agent',
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'},
               {'Accept', 'text/html;q=0.9,*/*;q=0.8'},
               {'Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'},
               {'Accept-Encoding', 'gzip,deflate,sdch'},
               {'Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,ms;q=0.2,zh-TW;q=0.2'},
               {'Connection', 'keep-alive'},
               {'Cache-Control', 'max-age=0'},
               {'Referer', 'http://reg.email.163.com/unireg/call.do?cmd=register.entrance&from=126mail'}
               ]
    opener.addheaders = headers
    urllib2.install_opener(opener)
    f = urllib2.urlopen(url)
    # print(f.read())
    print(cj)