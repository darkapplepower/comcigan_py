import requests
from bs4 import BeautifulSoup
import re
from urllib import parse
import json
import base64
import math;
def _getHtml():
    result=requests.get("http://comci.kr:4082/st")
    result.encoding="euc-kr"
    result=BeautifulSoup(result.text, "html.parser")
    result=result.select("script")[1]
    return str(result)
def _scData():
    result = _getHtml()
    result=result[result.find("sc_data('") + 8:]
    return re.search("'[^']+", result).group(0)[1:]
def _searchVariableName():
    ret = []
    result = _getHtml()
    count=None
    while (True):
        count = result.find("자료.자료")
        if count == -1:
            break
        ret.append(result[count + 3: count + 8])
        result = result[count + 8:]
    return ret
def _getUrl():
    result = _getHtml()
    result = result[result.find("url"):]
    return re.search("/[^']+", result).group(0)
def getSchoolNumber(schoolName):
    url = _getUrl()
    schoolName = parse.quote(schoolName, encoding="euc-kr")
    data = requests.get("http://comci.kr:4082"+url+schoolName)
    data.encoding="utf-8"
    data=str(data.text)
    data = json.loads(data.replace("\0", ""))
    result=[]
    for i in data["학교검색"]:
        dic={}
        dic["name"]=i[2]+"("+i[1]+")"
        dic["number"]=i[3]
        result.append(dic)
    return result
def getTimeTable(schoolId, grade, cl, nextweek=False):
    grade=int(grade)
    cl=int(cl)
    nextweek=1+ +bool(nextweek)
    scdata = _scData()
    _base64 = (str(scdata) + str(schoolId) + "_0_"+str(nextweek)).encode("utf-8")
    _base64=base64.b64encode(_base64)
    url = _getUrl()
    data = requests.get("http://comci.kr:4082" + url.split("?")[0] + "?" + _base64.decode("utf-8"))
    data.encoding="utf-8"
    data = json.loads(str(data.text).replace("\0", ""))
    zaryo = _searchVariableName()
    result = {}
    result["수업시간"] = data["일과시간"].copy()
    result["시간표"] = [[], [], [], [], [], []]
    ordd, dad, th, sb, na=None, None, None, None, None
    for t in range(1,9):
        for we in range(1,7):
            ordd = data[zaryo[0]][grade][cl][we][t]
            dad = data[zaryo[1]][grade][cl][we][t]
            th = math.floor(dad / 100)
            sb = dad - th * 100
            if dad > 100:
                if th < len(data[zaryo[3]]):
                    na = data[zaryo[4]][th][0:2]
                else:
                    na = ""
                result["시간표"][we - 1].append(None)
                result["시간표"][we - 1][t - 1] = data[zaryo[5]][sb] + "(" + na + ")"
    return result
_date="월화수목금토일"
def sortTable(timeTable):
    result=["" for i in range(6)]
    for i in range(6):
        result[i]+=_date[i]+"\n";
        for ii in timeTable["시간표"][i]:
            result[i]+=ii+"\n"
    return "\n\n".join(result)