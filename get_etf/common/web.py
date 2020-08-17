from __future__ import unicode_literals
import os
import re
import urllib
import urllib3
import requests
import log
import chardet #http://pypi.python.org/pypi/chardet
import func

#----------------------
http_prefix = 'http://'

http_headers = {
	'Accept':'*/*',
	'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding':'gzip,deflate,sdch',
	'Accept-Language':'en-US,en;q=0.8,zh;q=0.6',
	'Cache-Control':'no-cache',
	'Connection':'keep-alive',
	'Pragma':'no-cache',
	'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
}

#---------------------------------------------------------------
class browser_tab(object):
	proxy_loaded = False
	proxy_str = None
	http = None
	session = None
	headers = {}
	site_base = ''
	
	#----------------------
	def Connect(this, website):
		this.set_base(website)

		#this.http = urllib3.HTTPConnectionPool(website, timeout=120)
		#this.http = urllib3.PoolManager()

		#this.session = requests.session(headers=http_headers)
		this.session = requests.session()

	#----------------------
	def get_web_contents(this, url):
		url = this._get_full_url(url, this.set_base)
		if not isinstance(url, unicode):
			log.WriteError('连接不是纯字符串形式：%s' % url)
			return ''

		this.headers['Referer'] = this._get_full_url(this.get_base())
		strg = this._request(url)
		return this._decode(str(strg))

	#----------------------
	def get_picture(this, url_from, url_pic, file_save_to):
		if os.path.isfile(file_save_to) : 
			log.WriteDetail("已有:%s" % file_save_to)
			return True
		
		url_pic = this._get_full_url(url_pic, this.set_base)
		this.headers['Referer'] = this._get_full_url(url_from)
		
		raw = this._request(url_pic)

		if not raw :
			log.WriteError("失败无法下载:%s" % url_pic)
			return False

		fout = open(file_save_to, 'wb')
		fout.write(raw)
		fout.close()

		if not os.path.isfile(file_save_to) :
			log.WriteDetail("失败无法保存:%s <- %s" % (file_save_to, url_pic))
			return False

		log.WriteDetail('保存:%s' % file_save_to)
		return True

	#----------------------
	def get_base(this) : return this.site_base
	def set_base(this, host):
		this.headers['Host'] = host
		this.site_base = host

	#----------------------
	def _request(this, url):
		try_time = 2

		for i in xrange(0, try_time):
			try:
				raw_str = this._request_requests(url)
				if not raw_str : raise Exception('空内容')
				return raw_str

			except Exception as e:
				desc = '%s' % e
				if i < try_time - 1: desc = desc + '.重试'
				log.WriteError(desc)

		log.WriteError('空内容')
		return ''

	#----------------------
	def _request_requests(this, url):
		#r = this.session.get(url, headers=this.headers,
		#proxies=this._get_proxy(), timeout=30)
		r = this.session.get(url, headers=this.headers, proxies=None, timeout=30)
		if r.status_code != requests.codes.ok : return ''
		return r.content
		#r.content is raw #text is unicode.

	#----------------------
	def _request_v1(this, url):
		r = urllib.urlopen(url, proxies=this._get_proxy())
		return r.read()

	#----------------------
	def _request_v3(this,url):
		r = this.http.request('GET', url)
		return r.data

	#----------------------
	def _decode(this, c):
		if not c : return c

		cs = ''
		m = re.search(r'(?uims)<meta.+?charset=[ \'\"]*(.+?)[ \'\"\/>]', c)
		if m : cs = m.group(1)

		if len(cs) < 3 :
			cs = chardet.detect(c)
			cs = cs['encoding']
			if not cs:
				raise Exception('编码不可读')

		if cs.lower() == 'unicode' : return c

		return c.decode(cs, 'ignore')

	#----------------------
	#url如果是 '/abc/cc' 的形式，将自动添加 http://site_base/abc/cc
	#如果 url 包含 http://abc, abc 将成为 site_base
	def _get_full_url(this, url, func_set_host=None):
		url_info = urllib3.util.parse_url(url)
		host = this.get_base()

		# have a specified host
		if url_info.host :
			host = url_info.host

		# make full url
		url = http_prefix + host
		if url_info.path : url = url + url_info.path
		if url_info.query : url = url + '?' + url_info.query

		# set host if needed:
		if func_set_host : func_set_host(host)

		return url

	#----------------------
	def _get_proxy(this):
		if this.proxy_loaded : return this.proxy_str

		this.proxy_loaded = True
		empty_str = "代理文件(_proxy.txt)为空，不使用代理. 格式：{'http': 'http://127.0.0.1:8080'}"

		try:
			f = open('_proxy.txt')
			strg = f.read()
			if strg :
				this.proxy_str = eval(strg)
				log.WriteEntry('全部使用代理 : %s' % strg)
			else:
				log.WriteEntry(empty_str)
		except:
			this.proxy_str = None
			log.WriteEntry(empty_str)
		
		return this.proxy_str


		
