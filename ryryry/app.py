from flask import Flask, request, render_template, url_for, send_from_directory, redirect, session, json, jsonify
import os
from datetime import timedelta
import pymysql
import sys
import requests
from bs4 import BeautifulSoup
import time
global pageSige
pageSige=8
# reload(sys)
# sys.setdefaultencoding('utf-8')


i = 0
c=requests.session()
c.keep_alive=False
basedir=os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "AASD123123"  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小



def qurry_for_result(sql):#取数据
    conn = pymysql.connect(host="47.94.202.186", user="ry", passwd="ry", db="ry", charset="utf8")
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 执行完毕返回的结果集默认以元组显示
    res = cursor.execute(sql)
    dict = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return res


def qurry_for_data(sql): #对数据库操作
    conn = pymysql.connect(host="47.94.202.186", user="ry", passwd="ry", db="ry", charset="utf8")
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 执行完毕返回的结果集默认以元组显示
    res = cursor.execute(sql)
    dict = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return dict


def convertDict():#数据处理
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


def read_json():#读数据 字典列表
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


@app.before_request#重定向，没有登录访问别的页面要先登录，才有权限访问
def print_request_info():
    # print(request.path)
    # print("请求方法：" + str(request.method))
    # print("---请求headers--start--")
    # print(str(request.headers).rstrip())
    # print("---请求headers--end----")
    # print("GET参数：" + str(request.args))
    # print("POST参数：" + str(request.form))
    if (
            request.path == '/reg' or request.path == '/login' or request.path == '/reg.html' or request.path == '/login.html' or request.path.find(
        "/static/") >= 0):
        return None
    if session.get("role") == None:
        return redirect('login.html')
    if (request.path.find('/zs') >= 0):
        if session.get("role") == 1:
            return None
        else:
            return jsonify({'status': '-1', 'msg': '权限不足'})


@app.route('/login', methods=['POST','GET'])
def login():
    userid = request.form.get('userid')
    password = request.form.get('password')
    res = qurry_for_data("select * from student where id='%s' and password='%s'" % (userid, password))
    if len(res) > 0:
        session['userid'] = userid
        session['username'] = res[0]["name"]
        session['role'] = res[0]["role"]
        session['pic_data'] = res[0]["pic_data"]
        return jsonify({'status': '0', 'msg': '登录成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '账号密码错误'})


@app.route('/reg', methods=['POST'])
def reg():
    userid=request.form['id']
    username = request.form['username']
    password = request.form['password']
    tel = request.form['tel']
    sex = request.form['sex']
    age = request.form['age']
    address = request.form['address']
    major = request.form['major']
    sclass = request.form['sclass']
    res = qurry_for_data("select * from student where id='%s'" % (userid))
    roro=1
    healths="绿"
    pic_data="2.jpg"
    if len(res) > 0:
        return jsonify({'status': '-1', 'msg': '用户已存在!'})
    else:
        res = qurry_for_result(
            "insert into student (`id`,`name`,`password`,`tel`,`sex`,`age`,`address`,`major`,`class`,`healths`,`role`,`pic_data`)"
            " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                userid,username, password, tel,sex,age,address,major,sclass,healths,roro,pic_data))
        if res == 1:
            return jsonify({ 'status': '0', 'msg': '注册成功!'})
        else:
            return jsonify({'status': '-1', 'msg': '数据库错误，请联系管理员'})

@app.route('/')
def test():#首页动图数据
    identity = session.get("role")
    username = session.get("username")
    pic_data=session.get("pic_data")
    date = time.strftime("%Y-%m-%d", time.localtime())
    dateCheck=basedir+"/static/Json/"+date+".json"
    if os.path.exists(dateCheck)==False:
        Download_addres = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_other"
        f = requests.get(Download_addres)
        with open(basedir + '/static/Json/test.json', "wb") as code:
            code.write(f.content)
            code.close()
        fileToWrite = convertDict()
        with open(basedir + '/static/Json/test.json', 'w', encoding="utf-8") as json_file:
            json_file.write(fileToWrite)
            json_file.close()
        fileToDic = read_json()
        date = time.strftime("%Y-%m-%d", time.localtime())
        with open(basedir + '/static/Json/' + date + '.json', 'w', encoding="utf-8") as json_file:
            json_file.write(fileToDic)
            json_file.close()
    if int(identity) == 0:
        identity = '管理员'
        return render_template('index_admin.html',identity=identity,username=username,pic_data=pic_data)
    elif int(identity) == 1:
        identity = '学生'
        return render_template('index_user.html',identity=identity,username=username,pic_data=pic_data)
    else:
        identity = '超管'
        return render_template('super_admin.html',identity=identity,username=username,pic_data=pic_data)
@app.route('/login.html')
def login_html():
    return render_template('login.html')

@app.route('/user_data.html')
def userdata_html():
    identity=session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    userid=session.get("userid")
    res = qurry_for_data("select * from student where id='%s'" % (userid))
    username=res[0]['name']
    healths=res[0]['healths']
    major = res[0]['major']
    grades=res[0]['class']
    address=res[0]['address']
    pic_data=res[0]['pic_data']
    return render_template('user_data.html',identity=identity,userid=userid,username=username,healths=healths,major=major,grades=grades,address=address,pic_data=pic_data)


@app.route('/reg.html')
def reg_html():
    return render_template('reg.html')


@app.route('/tongzhi.html')
def tongzhi_html():
    identity = session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    username = session.get("username")
    pic_data = session.get("pic_data")
    res = qurry_for_data("select * from notice")
    res.reverse()
    return render_template('tongzhi.html',identity=identity,username=username,pic_data=pic_data,res=res)


@app.route('/jiankang.html', methods=['POST', 'GET'])
def jiankang_html():
    identity = session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    userid = session.get("userid")
    res = qurry_for_data("select * from student where id='%s'" % (userid))
    username = res[0]['name']
    major = res[0]['major']
    grades = res[0]['class']
    address = res[0]['address']
    pic_data = res[0]['pic_data']
    tel = res[0]['tel']
    return render_template('jiankang.html',identity=identity,tel=tel,userid=userid,username=username,major=major,grades=grades,address=address,pic_data=pic_data)


@app.route('/waichu.html')
def waichu_html():
    identity = session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    userid = session.get("userid")
    username = session.get("username")
    pic_data = session.get("pic_data")
    res = qurry_for_data("select * from out_school where stu_id='%s'" % (userid))
    for i in res:
        if i['approval_status'] == 0:
            i['approval_status'] = '等待审批'
        elif i['approval_status'] == -1:
            i['approval_status'] = '已拒绝'
        else:
            i['approval_status'] = '已通过'
        if i['refuse_reason'] == '0':
            i['refuse_reason'] = '无'
    return render_template('waichu.html',identity=identity,username=username,pic_data=pic_data,userid=userid,res=res)


@app.route('/baodao.html')
def baodao_html():
    identity = session.get("role")
    if identity == '0':
        identity = '管理员'
    else:
        identity = '学生'
    userid = session.get("userid")
    username = session.get("username")
    pic_data = session.get("pic_data")
    res = c.get("http://www.gov.cn/fuwu/zt/yqfwzq/zxqk.htm#0")
    text = res.content.decode("utf8")
    html = BeautifulSoup(text, "lxml")
    res = html.find("div", {"class": "menu1 menu_tab"}).findAll("a", {"target": "_blank"})
    all = []
    for i in res:
        one = []
        one.append("http://www.gov.cn" + i["href"])
        one.append(i.string)
        all.append(one)
    # 处理完的结果在all内(二维列表)
    print(all)
    return render_template('baodao.html', identity=identity, username=username, pic_data=pic_data, userid=userid,all=all)


# 改个人资料
@app.route('/modify', methods=['POST','GET'])
def modify():
    userid=session.get("userid")
    username=request.form.get('username')
    grades=request.form.get('grades')
    address=request.form.get('address')
    portrait=request.files['portrait']
    check_portrait=portrait.filename.split('.')[-1]
    if check_portrait != 'jpg' and check_portrait != 'png' and check_portrait != 'jpeg':
        return jsonify({'status': '-1', 'msg': '请上传jpg/png/jpeg格式的图片'})
    path = basedir+"/static/portrait/"
    file_path = path+userid+'.'+check_portrait
    portrait.save(file_path)
    pic_data=userid+'.'+check_portrait
    res = qurry_for_result(
        "update student set name='%s',class='%s',address='%s',pic_data='%s' where id='%s'" % (username, grades,address,pic_data,userid))
    if res == 1 or res==0:
        return jsonify({'status': '0', 'msg': '修改成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '异常错误！请联系管理员'})

# 每日健康打卡
@app.route('/jiankang', methods=['POST', 'GET'])
def jiankang():
    userid = request.form.get('userid')
    major = request.form.get('major')
    grades = request.form.get('grades')
    nowaddress = request.form.get('nowaddress')
    tel = request.form.get('tel')
    healths=request.form.get('healths')
    potential1 = request.form.get('potential1')
    potential2 = request.form.get('potential2')
    temperature = int(request.form.get('temperature'))
    date=time.strftime("%Y-%m-%d", time.localtime())
    res = qurry_for_data("select * from signin where id='%s' and date='%s'" % (userid,date))
    if len(res)!=0:
        return jsonify({'status': '-2', 'msg': '今日已打过卡啦！'})
    if potential1== '是' or potential2=='是':
        potential=1                                                                                                                                                 
    else:
        potential=0
    res = qurry_for_result(
        "insert into signin (`id`,`major`,`class`,`nowaddress`,`tel`,`healths`,`potential`,`temperature`,`date`) values ("
        "'%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
            userid, major, grades, nowaddress, tel,healths,potential,temperature,date))
    if res == 1:
        return jsonify({'status': '0', 'msg': '打卡成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '数据库错误，请联系管理员'})


# 外出请假
@app.route('/waichu', methods=['POST', 'GET'])
def waichu():
    userid = session.get("userid")
    username=request.form.get('username')
    tel = request.form.get('tel')
    outreason = request.form.get('outreason')
    outaddress = request.form.get('outaddress')
    outtime = request.form.get('outtime')
    intime = request.form.get('intime')
    nowtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    res = qurry_for_result(
        "insert into out_school (`stu_id`,`stu_name`,`tel`,`out_reason`,`out_address`,`out_time`,`in_time`,`now_time`,`approval_status`,`refuse_reason`) values ("
        "'%s','%s','%s','%s','%s','%s','%s','%s','0','0')" % (
            userid, username,tel, outreason, outaddress, outtime, intime, nowtime))
    if res == 1:
        return jsonify({'status': '0', 'msg': '提交成功!请等待审批'})
    else:
        return jsonify({'status': '-1', 'msg': '数据库错误，请联系管理员'})


# 每日健康管理端
@app.route('/jiankang_admin.html', methods=['POST', 'GET'])
def jiankang_admin_html():
    date = time.strftime("%Y-%m-%d", time.localtime())
    identity = session.get("role")
    username = session.get("username")
    pic_data = session.get("pic_data")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    res_t = qurry_for_data("select * from signin where date='%s'" % (date))
    res_f=qurry_for_data("select id from signin where date='%s'" % (date))
    res_check = qurry_for_data("select id from student where role='1'")
    signin_c=[]
    for i in res_check:
        flag=1
        for j in res_f:
            if i==j:
                flag=0
                break
        if flag==1:
            signin_c.append(i['id'])
    return render_template('jiankang_admin.html', res=res_t,signin_c=signin_c,identity=identity,username=username,pic_data=pic_data)


@app.route('/user_data_admin.html')
def user_data_admin_html():
    identity=session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    userid=session.get("userid")
    res = qurry_for_data("select * from student where id='%s'" % (userid))
    username=res[0]['name']
    healths=res[0]['healths']
    major = res[0]['major']
    grades=res[0]['class']
    address=res[0]['address']
    pic_data=res[0]['pic_data']
    return render_template('user_data_admin.html',identity=identity,userid=userid,username=username,healths=healths,major=major,grades=grades,address=address,pic_data=pic_data)


@app.route('/tongzhi_admin.html')
def tongzhi_admin_html():
    identity = session.get("role")
    if identity == '0':
        identity= '管理员'
    else:
        identity='学生'
    username = session.get("username")
    pic_data = session.get("pic_data")
    return render_template('tongzhi_admin.html',identity=identity,username=username,pic_data=pic_data)


@app.route('/baodao_admin.html')
def baodao_admin_html():
    identity = session.get("role")
    if identity == '0':
        identity = '管理员'
    else:
        identity = '学生'
    userid = session.get("userid")
    username = session.get("username")
    pic_data = session.get("pic_data")
    res = c.get("http://www.gov.cn/fuwu/zt/yqfwzq/zxqk.htm#0")
    text = res.content.decode("utf8")
    html = BeautifulSoup(text, "lxml")
    res = html.find("div", {"class": "menu1 menu_tab"}).findAll("a", {"target": "_blank"})
    all = []
    for i in res:
        one = []
        one.append("http://www.gov.cn" + i["href"])
        one.append(i.string)
        all.append(one)
    # 处理完的结果在all内(二维列表)
    print(all)
    return render_template('baodao_admin.html', identity=identity, username=username, pic_data=pic_data, userid=userid,all=all)

# 发布通知
@app.route('/notice', methods=['POST', 'GET'])
def notice():
    userid=session.get("userid")
    notice_title = request.form.get('notice_title')
    notice_com = request.form.get('notice_com')
    username = session.get("username")
    date = time.strftime("%Y-%m-%d", time.localtime())
    res = qurry_for_result(
        "insert into notice (`release_id`,`username`,`title`,`com_ment`,`date`)"
        " values ('%s','%s','%s','%s','%s')" % (
            userid, username, notice_title, notice_com, date))
    if res==1:
        return jsonify({'status': '0', 'msg': '发布成功!'})


# 请假审批
@app.route('/waichu_admin.html', methods=['POST', 'GET'])
def waichu_admin_html():
    identity = session.get("role")
    if identity == '0':
        identity = '管理员'
    else:
        identity = '学生'
    username = session.get("username")
    pic_data = session.get("pic_data")
    res = qurry_for_data("select * from out_school where approval_status='0'")
    for i in res:
        if i['refuse_reason']=='0':
            i['refuse_reason']='无'
    return render_template('waichu_admin.html',res=res,identity=identity,username=username,pic_data=pic_data)

# 外出审批
@app.route('/approval', methods=['POST', 'GET'])
def approval():
    List=request.get_json()
    appAdmin=session.get("username")
    for i in range(0,len(List),3):
        res = qurry_for_result(
            "update out_school set approval_status='%s',refuse_reason='%s',app_name ='%s' where id='%s'" % (
                List[i+1],List[i+2], appAdmin,List[i]))
    return jsonify({'status': '0', 'msg': '审批成功!'})


# 超管接口
@app.route('/down_admin', methods=['POST', 'GET'])
def down_admin():
    down_admin = request.form.get('down_admin')
    res_check = qurry_for_data(
        "select role from student where id='%s'" % (down_admin))
    if len(res_check)==0:
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    if res_check[0]['role'] == '1' or res_check[0]['role'] == '2':
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    res = qurry_for_result(
        "update student set role='1' where id='%s'" % (down_admin))
    if res == 1:
        return jsonify({'status': '0', 'msg': '修改成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '异常错误！请联系管理员'})


@app.route('/add_admin', methods=['POST', 'GET'])
def add_admin():
    add_admin = request.form.get('add_admin')
    res_check = qurry_for_data(
        "select role from student where id='%s'" % (add_admin))
    if len(res_check)==0:
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    if res_check[0]['role'] == '0' or res_check[0]['role']=='2':
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    res = qurry_for_result(
        "update student set role='0' where id='%s'" % (add_admin))
    if res == 1:
        return jsonify({'status': '0', 'msg': '修改成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '异常错误！请联系管理员'})

@app.route('/delete_admin', methods=['POST', 'GET'])
def delete_admin():
    delete_admin = request.form.get('delete_admin')
    res_check = qurry_for_data(
        "select role from student where id='%s'" % (delete_admin))
    if len(res_check)==0:
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    if res_check[0]['role'] == '1' or res_check[0]['role'] == '2':
        return jsonify({'status': '0', 'msg': '请填写正确的管理员用户id!'})
    res = qurry_for_result(
        "delete from student where id='%s'" % (delete_admin))
    if res == 1:
        return jsonify({'status': '0', 'msg': '删除成功!'})
    else:
        return jsonify({'status': '-1', 'msg': '异常错误！请联系管理员'})
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)