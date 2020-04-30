from http.server import HTTPServer, BaseHTTPRequestHandler
from time import time
from ipaddress import ip_network
import sys

from models import DBHandler
from views import (
	send_error_400,
	send_error_429,
	send_reset_done,
	send_reset_fail,
	send_zen,
	)
if len(sys.argv)==2 and sys.argv[1]=='test':
	from tests.settings import *
else:
	from settings import (
		REQUESTS_LIMIT,
		BAN_TIMEOUT,
		REFILL_TIME,
		NETWORK_PREFIX,
		)

class NetworkManager:
	def add_new_network(self, network):
		last_request = time()
		requests = REQUESTS_LIMIT-1 #first request was already made
		banned_since = 0
		db_handler.insert_new_network(
			network,
			last_request,
			requests,
			banned_since
			)

	def ban(self, network):
		banned_since = time()
		db_handler.update_banned_since(network, banned_since)

	def is_banned(self, network):
		banned_since = db_handler.select(network, 'banned_since')
		if banned_since:
			if (time()-banned_since) < BAN_TIMEOUT:
				return True
			else:
				banned_since = 0
				db_handler.update_banned_since(network, banned_since)
				return False
		else:
			return False

	def is_rate_limit_reached(self, network):
		requests = db_handler.select(network, 'requests')
		last_request = db_handler.select(network, 'last_request')
		rate_limiter = RateLimiter()
		is_available = rate_limiter.is_available(requests, last_request)
		db_handler.update_rate_limiter_all(
			network,
			rate_limiter.last_request,
			rate_limiter.requests
			)
		return not is_available

class RateLimiter(object):
	'''
	algorithm: https://en.wikipedia.org/wiki/Token_bucket
	explanation: https://medium.com/smyte/rate-limiter-df3408325846
	'''
	def __init__(self):
		self.max_amount = REQUESTS_LIMIT
		self.refill_time = REFILL_TIME
		self.refill_amount = REQUESTS_LIMIT
		self._reset()

	def _reset(self):
		self.requests = self.max_amount
		self.last_request = time()

	def _refill_count(self, last_request):
		return int(((time() - last_request) / self.refill_time))

	def is_available(self, requests, last_request, tokens=1):
		refill_count = self._refill_count(last_request)
		self.requests = requests + refill_count * self.refill_amount
		self.last_request = last_request + refill_count * self.refill_time
		if self.requests >= self.max_amount:
			self._reset()
		if tokens > self.requests:
			return False
		self.requests -= tokens
		return True

class ServerHandler(BaseHTTPRequestHandler):
	net_manager = NetworkManager()

	def do_GET(self):
		if '/reset?net=' in self.path:
			self.reset_limit_and_response()
		else:
			self.check_limit_and_response()

	def reset_limit_and_response(self):
		network = self.path.split('=')[-1]
		network = network.replace('%2F', '/')
		if db_handler.select(network, 'network'):
			db_handler.delete(network)
			send_reset_done(self)
		else:
			send_reset_fail(self)

	def check_limit_and_response(self):
		network = self.get_network_from_header()
		if not network:
			send_error_400(self)		
		elif db_handler.select(network, 'network'):
			if self.net_manager.is_banned(network):
				send_error_429(self, network)
			elif self.net_manager.is_rate_limit_reached(network):
				self.net_manager.ban(network)
				send_error_429(self, network)
			else:
				send_zen(self)
		else:
			self.net_manager.add_new_network(network)
			send_zen(self)

	def get_network_from_header(self):
		ip = self.headers.get('X-Forwarded-For')
		if not ip:
			return None		
		network = str(ip_network(f'{ip}/{NETWORK_PREFIX}', strict=False))
		return network

if __name__ == '__main__':
	httpd = HTTPServer(("", 80), ServerHandler)
	db_handler = DBHandler()
	db_handler.connect()
	db_handler.create_table()
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		db_handler.disconnect()