from settings import (
	REQUESTS_LIMIT,
	BAN_TIMEOUT,
	REFILL_TIME,
	NETWORK_PREFIX,
	)

def send_zen(self):
	self.send_response(200)
	self.send_header('Content-type', 'text/html;charset=utf-8')
	self.end_headers()
	with open('templates/zen.html', 'r') as html:
		template = html.read()
	self.wfile.write(bytes(template, 'utf-8'))

def send_error_400(self):
	self.send_response(400)
	self.send_header('Content-type', 'text/html;charset=utf-8')
	self.end_headers()
	with open('templates/error_400.html', 'r') as html:
		template = html.read()
	self.wfile.write(bytes(template, 'utf-8'))

def send_error_429(self, network):
	self.send_response(429)
	self.send_header('Content-type', 'text/html;charset=utf-8')
	self.send_header('Retry-After', BAN_TIMEOUT)
	self.end_headers()
	with open('templates/error_429.html', 'r') as html:
		template = html.read()
		template = template.format(
			network=network,
			requests_limit=REQUESTS_LIMIT,
			ban_timeout=BAN_TIMEOUT,
			refill_time=REFILL_TIME,
			)
	self.wfile.write(bytes(template, 'utf-8'))

def send_reset_done(self):
	self.send_response(200)
	self.send_header('Content-type', 'text/html;charset=utf-8')
	self.end_headers()
	with open('templates/reset_done.html', 'r') as html:
		template = html.read()
	self.wfile.write(bytes(template, 'utf-8'))

def send_reset_fail(self):
	self.send_response(400)
	self.send_header('Content-type', 'text/html;charset=utf-8')
	self.end_headers()
	with open('templates/reset_fail.html', 'r') as html:
		template = html.read()
	self.wfile.write(bytes(template, 'utf-8'))