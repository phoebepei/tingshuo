#/usr/env/bin python
# coding:utf-8

import re
import os
import transaction


from random import randint

from whatyousay.models import DBSession
from whatyousay.models import Users
from whatyousay.models import MetaData
from whatyousay.models import PasswordResets
from whatyousay.models import ActivateAccount
from whatyousay.models import UserTitle
from whatyousay.models import UserDomain

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from sqlalchemy import and_


def get_random_string():
	'''用来生成长度为十的随机字符串'''
	
	s_list = 'abcdefghijklmnopqrstuvwxyz1234567890'
	r_str = []
	for i in xrange(10):
		r_str.append(s_list[randint(0,35)])
	return ''.join(r_str)
	
def get_default_title(email):
	'''以邮箱@前的字符作为默认的Title'''
	r = re.compile('@')
	title = r.split(email)[0]
	return title


@view_config(request_method='GET', renderer='test.jinja2', route_name='test')
def test_get(request):
	return {'title': u'选择文件'}
	
@view_config(request_method='POST', route_name='test')
def test_post(request):
	file_name = request.POST['uploaded'].filename
	upload_file = request.POST['uploaded'].file
	
	file_path = os.path.join()
	upload_file.save()
	return Response('OK')

#主页

@view_config(renderer='frontpage.jinja2', route_name='home')
def home(request):
	return {'title': u'首页'}





#处理登录

@view_config(request_method='GET', renderer='login.jinja2', route_name='login')
def login_get(request):
	if 'logged_in'in request.session :
		if request.session['logged_in']:
			return HTTPFound(location=request.route_url('home'))
	else:
		return {'title':u'登录听说'}
	
@view_config(request_method='POST',route_name='login')
def login_post(request):
	'''登录页面的表单提交时会调用此视图'''
	req_email = request.POST['user_session[login]']
	req_password = request.POST['user_session[password]']
	query_result = DBSession.query(Users).filter(and_(Users.email==req_email,
															Users.password==req_password)).first()

	if(query_result.activated==1):
		request.session['logged_in'] = True
		request.session['email'] = req_email
		title_result = DBSession.query(UserTitle).filter(UserTitle.user_email==req_email).first()
		request.session['title'] = title_result.user_title
		
		return Response('OK')
	elif(query_result.activated==0):
		request.session.flash(u'登录失败，账户尚未激活')
		request.session.flash(u'请到'+req_email+u'查阅激活邮件并激活')
		return HTTPFound(location=request.route_url('login'))
	else:
		request.session.flash(u'登陆失败，邮箱或密码错误')
		return HTTPFound(location=request.route_url('login'))




#处理注册

@view_config(request_method='GET', renderer='signup.jinja2', route_name='signup')
def signup_get(request):
	return {'title': u'加入听说'}
	
@view_config(request_method='POST', route_name='signup')
def signup_post(request):
	'''处理用户从注册表单发回的数据
	并为每个新注册的用户添加一个激活码用来激活账户
	只有在激活账户之后，用户才能正常登录网站
	'''
	req_email = request.POST['user_session[login]']
	req_password = request.POST['user_session[password]']
	
	new_user = Users(email=req_email, password=req_password)
	DBSession.add(new_user)
	
	active_code=get_random_string()
	new_activate_url = ActivateAccount(req_email, active_code)
	DBSession.add(new_activate_url)
	transaction.commit()
	
	mailer = get_mailer(request)
	message = Message(subject=u'激活您的听说账户',
						sender='no-reply@tingshuo.com',
						recipients=req_email,
						body=u'欢迎加入听说，请点击下面的链接激活您的账户'+request.route_url('activate_account',active_code=active_code)
						)
	
	
	request.session.flash(u'您的注册已经成功，一封激活账户的邮件已经发送到您的邮箱'+req_email+u'中')
	return HTTPFound(request.route_url('login'))
	
	
	


#处理激活
@view_config(request_method='GET',route_name='activate_account')
def activate_account(request):
	'''当用户访问属于他的激活链接时会调用此视图
	首先检测激活码的正确性，若激活码有效，那么就激活该账户，并为其设置默认关联信息
	如果不正确，那么就返回提示信息
	'''
	active_code = request.matchdict['active_code']
	
	query_result = DBSession.query(ActivateAccount).filter(ActivateAccount.user_active_code==active_code).first()
	
	if(query_result):
		req_email = query_result.user_email
		user_result = DBSession.query(Users).filter(Users.email==req_email).first()
		
		default_title = get_default_title(req_email)
		print default_title
		default_domain = user_result.id
		user_title = UserTitle(req_email, default_title)
		user_domain = UserDomain(req_email, default_domain)
		DBSession.add(user_title)
		DBSession.add(user_domain)
		
		user_result.activated=1
		DBSession.delete(query_result)
		transaction.commit()
		request.session.flash(u'激活账户成功')
		return HTTPFound(location=request.route_url('login'))
	else:
		return Response(u'此激活链接失效或者此激活码不存在，若实在找不到激活邮件，请与管理员联系。管理员：suxindichen@gmail.com')
		
		
		
		
		
	
#发送重置密码的邮件

@view_config(request_method='GET', renderer='password_reset_new.jinja2', route_name='password_reset_new')
def password_reset_new_get(request):
	return {'title':u'找回密码'}
	
@view_config(request_method='POST', route_name='password_reset_new')
def password_reset_new_post(request):
	req_email = request.POST['user_session[login]']
	query_result = DBSession.query(PasswordResets).filter(PasswordResets.user_email==req_email).first()
	reset_num = get_random_string()
	new_password_reset = PasswordResets(req_email, reset_num)
	if(query_result):
		DBSession.delete(query_result)
	DBSession.add(new_password_reset)
		
	transaction.commit()
	
	mailer = get_mailer(request)
	message = Message(subject=u'为您的听说账户找回密码',
						sender='no-reply@tingshuo.com',
						recipients=req_email,
						body= request.route_url('password_reset', reset_num=reset_num)
						)
	mailer.send_immediately(message, fail_silently=False)
	
	request.session.flash(u'一封关于找回您密码的邮件已经发送到您的邮箱')
	request.session.flash(u'如果您在10分钟内没有收到邮件，请重新发送')
	
	return HTTPFound(location=request.route_url('password_reset_new'))	
						
						
	
#重置密码	
@view_config(request_method='GET',route_name='password_reset',renderer='password_reset.jinja2')
def password_reset_get(request):
	reset_num = request.matchdict['reset_num']
	
	query_result = DBSession.query(PasswordResets).filter(PasswordResets.user_reset_num==reset_num).first()
	
	if(query_result):
		return {'title':u'重置密码','email': query_result.user_email}
	else:
		request.session.flash(u'此链接失效或者错误，若要重新找回密码，请输入您的注册邮箱')
		return HTTPFound(location=request.route_url('password_reset_new'))
		
@view_config(request_method='POST', route_name='password_reset')
def password_reset_post(request):
	req_email = request.POST['user_session[login]']
	req_password = request.POST['user_session[password]']
	
	query_result = DBSession.query(Users).filter(Users.email==req_email).first()
	#重置密码
	query_result.password = req_password
	transaction.commit()
	
	#把重置密码的重置码从密码重置表中删除
	reset_result = DBSession.query(PasswordResets).filter(PasswordResets.user_email==req_email).first()
	DBSession.delete(reset_result)
	transaction.commit()
	request.session.flash(u'密码重置成功，现在你可以使用您的新密码登入了')
	return HTTPFound(location=request.route_url('login'))
	
	
	
	
