#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sae
import web
import model

urls = (
	'/', 'Index',
	'/queryrooms', 'QueryRooms',
	'/queryschedule','QuerySchedule',
	'/querynotice','QueryNotice',
	'/queryjob/page=(\d+)','QueryJob',
	'/quickquery','QuickQuery',
	'/queryborrow','QueryBorrow',
	'/wap','Wap',
	'/wap/job','WapJob',
	'/updatedb','UpdateDB'
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root, base='base')
waprender=web.template.render(templates_root)

class Index:
	def GET(self):
		args=[False,True,True,False,True,True,False,False,True,True,False,False,False,True,True,False,True,True,False]
		args.append(model.get_date_today())
		args.append(model.get_now_time())
		args.append(model.get_next_time())
		return render.index({},False,args)
class QueryRooms:
	def GET(self):
		userdata=web.input(buildingname=[],floor=[],seat=[],roomtype=[],page="1")
		buildingname_list=userdata.buildingname
		floor_list=userdata.floor
		seat_list=userdata.seat
		roomtype_list=userdata.roomtype
		currentpage=int(userdata.page)
		search_date=userdata.search_date
    		search_start_time=userdata.search_start_time
		search_end_time=userdata.search_end_time
		args=[]
		get_url='?'
		buildingnames=[u'博学南楼A',u'博学南楼B',u'博学南楼C',u'博学南楼D',u'博学北楼A',u'博学北楼B',u'博学北楼C']
		floors=['1','2','3','4','5']
		seats=['1','2','3','4']
		roomtypes=[u'多媒体教室',u'普通教室',u'考研自习室']
		for bns in buildingnames:
			if bns in buildingname_list:
				args.append(True)
				get_url=get_url+'buildingname='+bns+'&'
			else:
				args.append(False)
		for fls in floors:
			if fls in floor_list:
				args.append(True)
				get_url=get_url+'floor='+fls+'&'
			else:
				args.append(False)
		for sts in seats:
			if sts in seat_list:
				args.append(True)
				get_url=get_url+'seat='+sts+'&'
			else:
				args.append(False)
		for rts in roomtypes:
			if rts in roomtype_list:
				args.append(True)
				get_url=get_url+'roomtype='+rts+'&'
			else:
				args.append(False)
		args.append(search_date)
		args.append(search_start_time)
		args.append(search_end_time)
		get_url=get_url+'search_date='+search_date+'&search_start_time='+search_start_time+'&search_end_time='+search_end_time+'&page'
		#校验输入的日期和时间
		errorflag=model.validate_timedate(search_date,search_start_time,search_end_time)
		if errorflag:
			return render.index({},False,args,errorflag)
		weekday=model.get_weekday(search_date)
		week=model.get_week(search_date)
    		classindex=model.get_classindex(search_start_time,search_end_time)
		temp="select * from classrooms where buildingname in ('"+"','".join(buildingname_list)+"') and floor in ('"+"','".join(floor_list)+"') and seatcountlevel in ('"+"','".join(seat_list)+"') and roomtype in ('"+"','".join(roomtype_list)+"') and roomid not in(select roomid from timetable where weekday='"+weekday+"' and sector in ('"+"','".join(classindex)+"') and fromweek<="+str(week)+" and toweek>="+str(week)+")"
		tempcount=model.db.query("select count(*) as rc from ("+temp+")sub")
		resultscount=tempcount[0].rc
		resultperpage=15
		if resultscount%resultperpage==0:
			pages=resultscount/resultperpage
		else:
			pages=resultscount/resultperpage+1
		os=(currentpage-1)*resultperpage
		results=model.db.query(temp+" order by roomid asc limit 15 offset "+str(os))
		pageargs=[]
		if pages==2:
			pageargs=[currentpage,1,2,1,2]
		elif pages>=3:
			if currentpage==1:
				pageargs=[currentpage,1,pages,1,2,3]
			elif currentpage==pages:
				pageargs=[currentpage,1,pages,pages-2,pages-1,pages]
			else:
				pageargs=[currentpage,1,pages,currentpage-1,currentpage,currentpage+1]
		return render.index(results,True,args,'',get_url,pageargs)

class QuerySchedule:
	def GET(self):
		userdata=web.input()
		if userdata:
			args=[]
			args.append(userdata.search_schedule_date)
			buildingnames=[u'博学南楼A',u'博学南楼B',u'博学南楼C',u'博学南楼D',u'博学北楼A',u'博学北楼B',u'博学北楼C']
			args.append(buildingnames.index(userdata.search_schedule_building))
			args.append(userdata.search_schedule_room)
			#校验输入的日期和时间
			"""errorflag=model.validate_date(userdata.search_schedule_date)
			if errorflag:
				return render.schedule(states,errorflag,args)"""
			week=model.get_week(userdata.search_schedule_date)
			roomname=userdata.search_schedule_building+userdata.search_schedule_room
			temp="select weekday,sector from timetable where roomname='%s' and fromweek<=%s and toweek>=%s"%(roomname,week,week)
			#temp="select weekday,sector from timetable where roomname='"+roomname+"' and fromweek<="+str(week)+" and toweek>="+str(week)
			results=model.db.query(temp)
			#状态：1-有课 2-空闲 3-借用
			states=[]
			ti=0
			while ti<77:
				states.append(2)
				ti=ti+1
			weekdays=[u"星期一",u"星期二",u"星期三",u"星期四",u"星期五",u"星期六",u"星期日"]
			for r in results:
				ind=weekdays.index(r.weekday)*11
				sect=r.sector[1:-1].split(',')
				for j in sect:
					states[ind+int(j)-1]=1
			return render.schedule(states,'',args)
		else:
			args=[]
			args.append(model.get_date_today())
			args.append(0)
			args.append("101")
			week=model.get_week(model.get_date_today())
			temp="select weekday,sector from timetable where roomname='博学南楼A101' and fromweek<=%s and toweek>=%s"%(week,week)
			#temp="select weekday,sector from timetable where roomname='"+roomname+"' and fromweek<="+str(week)+" and toweek>="+str(week)
			results=model.db.query(temp)
			#状态：1-有课 2-空闲 3-借用
			states=[]
			ti=0
			while ti<77:
				states.append(2)
				ti=ti+1
			weekdays=[u"星期一",u"星期二",u"星期三",u"星期四",u"星期五",u"星期六",u"星期日"]
			for r in results:
				ind=weekdays.index(r.weekday)*11
				sect=r.sector[1:-1].split(',')
				for j in sect:
					states[ind+int(j)-1]=1
			return render.schedule(states,'',args)

class QueryNotice:
	def GET(self):
		temp="select * from webnews limit 8"
		webresults=model.db.query(temp)
		temp="select * from jwcnews limit 8"
		jwcresults=model.db.query(temp)
		temp="select * from jobnews order by xjdate,xjtime,school asc limit 10"
		jobresults=model.db.query(temp)
		return render.notice(webresults,jwcresults,jobresults)

class QueryJob:
	def GET(self,page):
		currentpage=int(page)
		temp="select * from jobnews order by xjdate,xjtime,school asc"
		tempcount=model.db.query("select count(*) as rc from ("+temp+")sub")
		resultscount=tempcount[0].rc
		resultperpage=20
		if resultscount%resultperpage==0:
			pages=resultscount/resultperpage
		else:
			pages=resultscount/resultperpage+1
		os=(currentpage-1)*resultperpage
		results=model.db.query(temp+" limit 20 offset "+str(os))
		pageargs=[]
		if pages==2:
			pageargs=[currentpage,1,2,1,2]
		elif pages>=3:
			if currentpage==1:
				pageargs=[currentpage,1,pages,1,2,3]
			elif currentpage==pages:
				pageargs=[currentpage,1,pages,pages-2,pages-1,pages]
			else:
				pageargs=[currentpage,1,pages,currentpage-1,currentpage,currentpage+1]
		return render.queryjob(results,pageargs)
class QueryBorrow:
	def GET(self):
		return render.queryborrow()
class UpdateDB:
	def GET(self):
		model.update_jwcnews()
		model.update_jobnews()
		return "ok"
class Wap:
	def GET(self):
		userdata=web.input()
		if userdata:
			buildingname=userdata.building
			start=userdata.start
			dura=userdata.dura
			weekday=model.get_weekday_today()
			week=model.get_week_today()
			classindex=model.get_classindex_1(start,dura)
			temp="select * from classrooms where buildingname='%s' and roomid not in(select roomid from timetable where weekday='%s' and sector in ('%s') and fromweek<=%s and toweek>=%s) order by roomid asc"%(buildingname,weekday,"','".join(classindex),week,week)
			#temp="select * from classrooms where roomid in(select roomid from timetable where buildingname='"+buildingname+"' and (case when weekday='"+weekday+"' then 1 else 0 end + case when duration in ('"+"','".join(classindex)+"') then 1 else 0 end + case when fromweek<="+str(week)+" and toweek>="+str(week)+" then 1 else 0 end)<>3)"
			results=model.db.query(temp)
			return waprender.wap(results,True)
		else:
			return waprender.wap()
class WapJob:
	def GET(self):
		temp="select * from jobnews where xjdate='%s' order by xjdate,xjtime,school asc"%model.get_date_today()
		results=model.db.query(temp)
		return waprender.wapjob(results)
class QuickQuery:
	def GET(self):
		userdata=web.input(page="1")
		buildingname=userdata.building
		start=userdata.start
		dura=userdata.dura
		currentpage=int(userdata.page)
		weekday=model.get_weekday_today()
		week=model.get_week_today()
		classindex=model.get_classindex_1(start,dura)
		temp="select * from classrooms where buildingname='%s' and roomid not in(select roomid from timetable where weekday='%s' and sector in ('%s') and fromweek<=%s and toweek>=%s) order by roomid asc"%(buildingname,weekday,"','".join(classindex),week,week)
		tempcount=model.db.query("select count(*) as rc from ("+temp+")sub")
		resultscount=tempcount[0].rc
		resultperpage=20
		if resultscount%resultperpage==0:
			pages=resultscount/resultperpage
		else:
			pages=resultscount/resultperpage+1
		os=(currentpage-1)*resultperpage
		results=model.db.query(temp+" limit 20 offset "+str(os))
		#args=[]
		"""buildingnames=[u'博学南楼A',u'博学南楼B',u'博学南楼C',u'博学南楼D',u'博学北楼A',u'博学北楼B',u'博学北楼C']
		starts=[u'现在',u'5分钟后',u'10分钟后',u'20分钟后',u'30分钟后',u'1小时后']
		duras=[u'半小时',u'1小时',u'2小时',u'3小时',u'4小时',u'整个时间段']
		args.append(buildingnames.index(buildingname))
		args.append(starts.index(start))
		args.append(duras.index(dura))"""
		get_url='?building='+buildingname+'&start='+start+'&dura='+dura+'&page'
		pageargs=[]
		if pages==2:
			pageargs=[currentpage,1,2,1,2]
		elif pages>=3:
			if currentpage==1:
				pageargs=[currentpage,1,pages,1,2,3]
			elif currentpage==pages:
				pageargs=[currentpage,1,pages,pages-2,pages-1,pages]
			else:
				pageargs=[currentpage,1,pages,currentpage-1,currentpage,currentpage+1]
		return render.quickquery(results,get_url,pageargs)
		
app = web.application(urls, globals()).wsgifunc()
application = sae.create_wsgi_app(app)
