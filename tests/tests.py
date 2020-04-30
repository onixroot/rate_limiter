import unittest
import requests
import time

class RateLimitTest(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print('\nRun new local instance of web-server: python http_server.py test')
		print('\nPress ANY key when ready')
		input()

	def test_1get_below_limit(self):
		response = requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.1'},)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'The Zen of Python', response.content)

	def test_2get_above_limit(self):
		response = requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.2'},)
		self.assertEqual(response.status_code, 429)
		self.assertIn(b'Error code: 429', response.content)

	def test_3reset_rate_limit(self):
		response = requests.get('http://localhost/reset?net=1.1.1.0/24')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Reset done', response.content)
		response = requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.3'},)
		self.assertEqual(response.status_code, 200)

	def test_4reset_wrong_net(self):
		response = requests.get('http://localhost/reset?net=6.6.6.0/24')
		self.assertEqual(response.status_code, 400)
		self.assertIn(b'Reset fail', response.content)

	def test_5check_ratelimit_timeout(self):
		time.sleep(2.1)
		response = requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.5'},)
		self.assertEqual(response.status_code, 200)

	def test_6check_ban_timeout(self):
		requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.6'},)
		time.sleep(3.1)
		response = requests.get('http://localhost', headers={'X-Forwarded-For': '1.1.1.6'},)
		self.assertEqual(response.status_code, 200)

	def test_7no_http_header(self):
		response = requests.get('http://localhost')
		self.assertEqual(response.status_code, 400)

	@classmethod
	def tearDownClass(self):
		print('\nNow you can turn off web-server')

if __name__ == '__main__' :
	unittest.main()