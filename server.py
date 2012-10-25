#!/usr/bin/python
from lib.geventdaemon import GeventDaemon
import os
home = os.environ["HOME"]
pidfile = '/var/run/smsd/proxy.pid'
class ProxyDaemon(GeventDaemon):
	def run(self):
		from proxy import Proxy
		proxy = Proxy()
		proxy.run()

if __name__ == "__main__":
	proxd = ProxyDaemon(pidfile)
	proxd.start()
