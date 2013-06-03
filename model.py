# coding: utf-8
import web
import sae.const
from datetime import date,time,timedelta,datetime
import sys
import urllib2
import re
import os

#数据库配置
db = web.database(dbn='mysql', user=sae.const.MYSQL_USER, pw=sae.const.MYSQL_PASS,\
host=sae.const.MYSQL_HOST, port=int(sae.const.MYSQL_PORT), db=sae.const.MYSQL_DB)

#学期第一周的日期
firstweek=date(2012,9,3)

#上课时间
classtime=[time(8,30),time(9,20),time(10,20),time(11,10),time(14,00),time(14,50),time(15,40),time(16,30),time(19,00),time(19,50),time(20,40)]

#一节课持续时间
classdurition=40

#下课时间
def get_classover(classstart):
    overhour=classstart.hour
    overminute=classstart.minute;
    if classstart.minute+classdurition>=60:
        overhour=overhour+1
        overminute=overminute+classdurition-60
    else:
        overminute=overminute+classdurition
    return time(overhour,overminute)

#今日是学期的第几周date.today()
def get_week(input_date):
    s=input_date.split("-");
    year=int(s[0])
    month=int(s[1])
    day=int(s[2])
    return ((date(year,month,day)-firstweek).days-1)/7+1

#输入日期是周几
def get_weekday(input_date):
    s=input_date.split("-");
    year=int(s[0])
    month=int(s[1])
    day=int(s[2])
    weekdays=[u"星期一",u"星期二",u"星期三",u"星期四",u"星期五",u"星期六",u"星期日"]
    return weekdays[date.isoweekday(date(year,month,day))-1]

#今天是学期的第几周
def get_week_today():
    return ((date.today()-firstweek).days-1)/7+1

#今天的日期
def get_date_today():
	td=date.today()
	return str(td.year)+"-"+str(td.month)+"-"+str(td.day)
#当前时刻
def get_now_time():
	nowtime=datetime.now()
	h=nowtime.hour
	m=nowtime.minute
	return "%s:%s"%(h,m)
	
#下一时刻（40min后）
def get_next_time():
	nowtime=datetime.now()
	h=nowtime.hour
	m=nowtime.minute
	if m+40>=60:
		h=h+1
		m=m+40-60
	else:
		m=m+40
	return "%s:%s"%(h,m)
	
#今天是周几
def get_weekday_today():
	weekdays=[u"星期一",u"星期二",u"星期三",u"星期四",u"星期五",u"星期六",u"星期日"]
    	return weekdays[date.isoweekday(date.today())-1]
    
#校验日期和时间(0/1/2:日期/起始时间/结束时间输入错误 3:所有输入正确)
def validate_timedate(input_date,input_start_time,input_end_time):
	try:
		s=input_date.split("-");
    		year=int(s[0])
    		month=int(s[1])
    		day=int(s[2])
    		dt=date(year,month,day)
    	except:
    		return '---->日期输入错误，请检查格式后查询<----'
    	try:
    		s=input_start_time.split(":")
    		start_time=time(int(s[0]),int(s[1]))
    	except:
    		return '---->起始时间输入错误，请检查格式后查询<----'
    	try:
    		s=input_end_time.split(":")
    		end_time=time(int(s[0]),int(s[1]))
    	except:
    		return '---->结束时间输入错误，请检查格式后查询<----'
    	else:
    		return ''

#校验日期和时间(0/1/2:日期/起始时间/结束时间输入错误 3:所有输入正确)
def validate_date(input_date):
	try:
		s=input_date.split("-");
    		year=int(s[0])
    		month=int(s[1])
    		day=int(s[2])
    		dt=date(year,month,day)
    	except:
    		return '---->日期输入错误，请检查格式后查询<----'
    	else:
    		return ''
    		    			
#输入开始时间和结束时间，看跨过了哪节课
def get_classindex(input_starttime,input_endtime):
    s=input_starttime.split(":")
    start_time=time(int(s[0]),int(s[1]))
    s=input_endtime.split(":")
    end_time=time(int(s[0]),int(s[1]))
    if start_time>end_time:
    	t=time(0,0)
        end_time=t;
        end_time=start_time;
        start_time=t;
    if start_time<time(6,30):
        start_time=time(6,30)
    if end_time>time(23,30):
        end_time=time(23,30)
    if start_time>time(23,30):
    	start_time=time(23,30)
    	end_time=time(23,30)
    if end_time<time(6,30):
        start_time=time(6,30)
        end_time=time(6,30)
    start=0.0
    k=0
    while k<10:
        if start_time>=classtime[k] and start_time<get_classover(classtime[k]):
            start=k+1
            break
        elif start_time>=get_classover(classtime[k]) and start_time<classtime[k+1]:
            start=k+1.1
            break
        else:
            k=k+1
    if start_time<classtime[0]:
        start=0.0
    if start_time>=classtime[10] and start_time<get_classover(classtime[10]):
        start=11
    if start_time>=get_classover(classtime[10]):
        start=12
    end=0.0
    m=0
    while m<10:
        if end_time>=classtime[m] and end_time<get_classover(classtime[m]):
            end=m+1
            break
        elif end_time>=get_classover(classtime[m]) and end_time<classtime[m+1]:
            end=m+1.1
            break
        else:
            m=m+1
    if end_time<classtime[0]:
        end=0.0
    if end_time>=classtime[10] and end_time<get_classover(classtime[10]):
        end=11
    if end_time>=get_classover(classtime[10]):
        end=11.1
    result=[]
    for i in [1,2,3,4,5,6,7,8,9,10,11]:
        if i>=start and i<=end:
            if i==1:
                result.extend([u"第1节",u"第1,2节",u"第1,2,3节"])
            elif i==2:
                result.extend([u"第2节",u"第1,2节",u"第1,2,3节"])
            elif i==3:
                result.extend([u"第3节",u"第3,4节",u"第1,2,3节"])
            elif i==4:
                result.extend([u"第4节",u"第3,4节"])
            elif i==5:
                result.extend([u"第5节",u"第5,6节",u"第5,6,7节"])
            elif i==6:
                result.extend([u"第6节",u"第5,6节",u"第5,6,7节"])
            elif i==7:
                result.extend([u"第7节",u"第7,8节",u"第5,6,7节"])
            elif i==8:
                result.extend([u"第8节",u"第7,8节"])
            elif i==9:
                result.extend([u"第9节",u"第9,10,11节"])
            elif i==10:
                result.extend([u"第10节",u"第9,10,11节"])
            elif i==11:
                result.extend([u"第11节",u"第9,10,11节"])
    return result
    
def get_classindex_1(start,dura):
	nowtime=datetime.now()
	h=nowtime.hour
	m=nowtime.minute
	nt=time(h,m)
	start_time=str(h)+":"+str(m)
	du=int(dura)
	if du==0:
		if m+30>=60:
			h=h+1
			m=m+30-60
		else:
			m=m+30
	elif du==-1:
		if nt<time(12,0):
			h=12
			m=0
		elif nt<time(17,0):
			h=17
			m=0
		elif nt<time(23,59):
			h=23
			m=30

	else:
		h=h+du
	if h>24:
		h=23
		m=30
	end_time=str(h)+":"+str(m)
	return get_classindex(start_time,end_time)
	
def update_jwcnews():
	try:
		content = urllib2.urlopen('http://jwc.ahu.edu.cn/main/notice.asp').read()
		content=content.decode("gb2312","ignore").encode("utf-8")
		sub_content=content[content.index('通知公告'):]
		rege=r'initialize.(\d+)'
		re_url = re.findall(rege, sub_content)
		rege=r"initialize.\d+,'(.+)'"
		re_title = re.findall(rege,sub_content)
		rege=r'initialize.*?<td class="timecss".*?>(.+)</td>'
		re_time=re.findall(rege,sub_content)
		#仅显示10条教务处新闻
		if re_url and len(re_url)>=10:
			db.query("delete from jwcnews")
			for i in range(10):
				url="http://jwc.ahu.edu.cn/main/show.asp?id="+re_url[i]
				tit=re_title[i]
				pubtime=re_time[i]
				temp="insert into jwcnews(title,publishtime,linkhref) values ('%s','%s','%s')"%(tit,pubtime,url)
				db.query(temp)
	except:
		pass

def update_jobnews():
	#以下代码更新安徽大学就业信息
	content = urllib2.urlopen('http://www.job.ahu.edu.cn/detach.portal?.pen=pe18&.pmn=view&action=queryAllZphManageView').read()	
	sub_content=content[content.index("<th>参加意愿</th>"):]
	rege=rege=r"<tr>.*?专场招聘会.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?target.*?>(.*?)</a>.*?href='(.*?)'"
    	re_info = re.findall(rege,sub_content,re.S)
    	if re_info:
    		db.query("delete from jobnews where school='安徽大学'")
    		for i in range(len(re_info)):
    			loc=re_info[i][0]
    			sdate=re_info[i][1]
    			stime=re_info[i][2]
    			comp=re_info[i][3]
    			url="http://www.job.ahu.edu.cn/"+re_info[i][4]
    			temp="insert into jobnews(companyname,location,xjdate,xjtime,school,urlhref) values ('"+comp+"','"+loc+"','"+sdate+"','"+stime+"','安徽大学','"+url+"')"
    			db.query(temp)
    	#以下代码更新中科大的就业信息（仅今明两天）
	breakif=False
	today_date=date.today()
	tomorrow_date=today_date+timedelta(1)
	db.query("delete from jobnews where school='中科大'")
    	for i in range(10):
		joburl='http://job.ustc.edu.cn/list.php?page='+str(i+1)+'&trans=7&MenuID=002001'
		content = urllib2.urlopen(joburl).read()
		content=content.decode("gb2312","ignore").encode("utf-8")
		sub_content=content[content.index("招聘会名称"):]
		rege=r'a href="(.*?)".*?>\r\n\s+(\S+?)\s+?</a><span class="zhiwei">\r\n\s+(\S+)\s+(\S+)\s+</span><span class="zhuanye">\r\n\s+(\S+)\s+</span></li>'
    		re_info = re.findall(rege,sub_content,re.S)
		for j in range(len(re_info)):
			sdate=re_info[j][2]
			s=sdate.split('-')
			xjdate=date(int(s[0]),int(s[1]),int(s[2]))
			#if xjdate==today_date or xjdate==tomorrow_date:
			if xjdate>=today_date:
				url="http://job.ustc.edu.cn/"+re_info[j][0]
				comp=re_info[j][1]
				stime=re_info[j][3]
				loc=re_info[j][4]
				temp="insert into jobnews(companyname,location,xjdate,xjtime,school,urlhref) values ('%s','%s','%s','%s','中科大','%s')"%(comp,loc,sdate,stime,url)
    				db.query(temp)
			else:
				break
		if breakif:
			break
		else:
			continue
    	#以下代码更新合工大的就业信息（仅今明两天）
    	"""er=[]
    	breakif=False
    	today_date=date.today()
	tomorrow_date=today_date+timedelta(1)
    	db.query("delete from jobnews where school='hfut'")
    	for i in range(10):
		joburl='http://gdjy.hfut.edu.cn/JobIn/MeetingInS.jsp?page='+str(i+1)
		content = urllib2.urlopen(joburl).read()
		content=content.decode("gb2312","ignore").encode("utf-8")
		sub_content=content[content.index("发布日期"):]
		rege=r'<TR.*?az.*?href="(.*?)".*?>(.*?)</a>.*?az>(.*?)</td>'
    		re_info = re.findall(rege,sub_content,re.S)
		for j in range(len(re_info)):
			sdate=re_info[j][2]
			s=sdate.split('-')
			xjdate=date(int(s[0]),int(s[1]),int(s[2]))
			if xjdate==today_date or xjdate==tomorrow_date:
				comp=re_info[j][1]
    				url='http://gdjy.hfut.edu.cn/JobIn/'+re_info[j][0]
				pagecontent=urllib2.urlopen(url).read();
				pagecontent=pagecontent.decode("gb2312","ignore").encode("utf-8")
				rege=r'height="41" align="left".*?>(.*?)</td>'
    				loc = re.findall(rege,pagecontent,re.S)[0]
    				rege=r">时间.*?<td.*?&nbsp;&nbsp;(.*?)</td>"
    				stime = re.findall(rege,pagecontent,re.S)[0]
    				temp="insert into jobnews(companyname,location,xjdate,xjtime,school,urlhref) values ('%s','%s','%s','%s','hfut','%s')"%(comp,loc,sdate,stime,url)
    				db.query(temp)
			elif xjdate<today_date:
				breakif=True
				break
			else:
				continue
		if breakif:
			break
		else:
			continue"""
