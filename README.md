<h3>Rate limiter</h3>
<hr>
An HTTP service able to limit the number of requests (rate-limit) from IPv4 networks.<br>
Extracts ip from 'X-Forwarded-For' http header and rate-limit network based on configured network prefix.<br>
If rate-limit reached block network for BAN_TIMEOUT and returns 429 error (RFC 6585)<br><br>

Use-cases:
- Open any page to get static content (example: <b>http://localhost/</b>)
- Open <b>http://localhost/reset?net=x.x.x.x/mask</b>) to reset rate limits

Default config:
- REQUESTS_LIMIT: 100 per minute
- BAN_TIMEOUT: 120 sec
- NETWORK_PREFIX = /24 (255.255.255.0)

Additionally:
- Covered with tests (Require running instance of web-server: <b>python http_server.py test</b>)
- Able to work as container (<b>docker-compose up</b>)
- Utilize <b>settings.py</b> for initial configuration
- Contain reset limit handler