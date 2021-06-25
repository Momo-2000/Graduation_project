import os
import requests
import json
import time

basedir=os.path.dirname(os.path.realpath(__file__))


def convertDict():
    with open(basedir+'/static/Json/test.json','rb') as json_file:
        json_str=json_file.read().decode("utf-8")  #读文件转str
        json_str = json_str.replace("\\", "")[1:-1]  #去反斜杠
        str_delete1=json_str.find("chinaDayList")+14
        str_delete2=json_str.find("chinaDayAddList")-2
        json_str=json_str[str_delete1:str_delete2]  #截取所需部分
        json_str = json_str.replace("date", "日期").replace("confirm", "累计确诊").replace("nowConfirm", "现有确诊（含重症）")
        json_str = json_str.replace("importedCase", "现有疑似").replace("noInfect", "现有重症").replace("deadRate","死亡率")
        json_str = json_str.replace("suspect", "累计确诊+现有疑似").replace("healRate", "治愈率")
        json_str = json_str.replace("nowSevere", "新增确诊").replace("localConfirmH5", "新增疑似").replace(
            "现有重症H5","新增(疑似+确诊)").replace("heal", "累计治愈").replace("dead", "累计死亡")
        json_file.close()
        return json_str


def read_json():
    with open(basedir+'/static/Json/test.json','rb') as json_file:
        dic_data = json.load(json_file)
        for i in range(1,len(dic_data)):
            dic_data[i]['累计确诊+现有疑似']=dic_data[i]['累计确诊']+dic_data[i]['现有疑似']
            dic_data[i]['新增确诊'] = dic_data[i]['累计确诊'] - dic_data[i-1]['累计确诊']
            dic_data[i]['新增疑似'] = dic_data[i]['现有疑似'] - dic_data[i - 1]['现有疑似']
            dic_data[i]['新增(疑似+确诊)'] = dic_data[i]['新增疑似'] + dic_data[i - 1]['新增确诊']
        dic_data[0]['累计确诊+现有疑似'] = dic_data[0]['累计确诊'] + dic_data[0]['现有疑似']
        dic_data[0]['新增确诊'] = "未知"
        dic_data[0]['新增疑似'] = "未知"
        dic_data[0]['新增(疑似+确诊)'] = "未知"
        dic_data=str(dic_data)
        dic_data=dic_data.replace("\\", "").replace("'","\"")
        return dic_data

if __name__ == "__main__":
    Download_addres = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_other"
    f = requests.get(Download_addres)
    with open(basedir + '/static/Json/test.json', "wb") as code:
        code.write(f.content)
        code.close()
    fileToWrite = convertDict()
    with open(basedir+'/static/Json/test.json', 'w',encoding="utf-8") as json_file:
        json_file.write(fileToWrite)
        json_file.close()
    fileToDic=read_json()
    date=time.strftime("%Y-%m-%d", time.localtime())
    with open(basedir+'/static/Json/'+date+'.json', 'w',encoding="utf-8") as json_file:
        json_file.write(fileToDic)
        json_file.close()


