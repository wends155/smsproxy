import gevent
try:
	import zmq.green as zmq
except ImportError:
	import gevent_zeromq as zmq
import sys
import signal
import os

class Proxy(object):
	def __init__(self):
		ctx = zmq.Context()

		#frontend sockets
		front_receive = ctx.socket(zmq.PULL)
		front_receive.bind("tcp://*:5555")	
		self.front_receive = front_receive

		front_sender = ctx.socket(zmq.PUB)
		front_sender.bind("tcp://*:5556")
		self.front_sender = front_sender

		front_outbox = ctx.socket(zmq.PULL)
		front_outbox.bind("tcp://*:5557")
		self.front_outbox = front_outbox

		#backend sockets
		back_publish = ctx.socket(zmq.PUB)
		back_publish.bind("tcp://*:5565")
		self.back_publish = back_publish

		back_sink = ctx.socket(zmq.PULL)
		back_sink.bind("tcp://*:5566")
		self.back_sink = back_sink

		back_failed = ctx.socket(zmq.PUB)
		back_failed.bind("tcp://*:5567")
		self.back_failed = back_failed

	def recv_msgs(self):
		while True:
			msg = self.front_receive.recv_string()
			self.back_publish.send_string(msg)
			gevent.sleep(0.1)

	def recv_outbox(self):
		while True:
			msg = self.front_outbox.recv_string()
			self.back_failed.send_string(msg)
			gevent.sleep(0.1)

	def send_msg(self):
		while True:
			msg = self.back_sink.recv_string()
			self.front_sender.send_string(msg)
			gevent.sleep(0.1)

	def stop(self, signum, frame=None):
		gevent.killall(self.workers)
		raise SystemExit("SIGTERM exit.")

	def run(self):
		gevent.signal(signal.SIGTERM,self.stop,None)
		try:
			self.workers = [gevent.spawn(self.recv_msgs),gevent.spawn(self.recv_outbox),gevent.spawn(self.send_msg)]
			print os.getpid()
			gevent.joinall(self.workers)
		except KeyboardInterrupt:
			self.stop(1)
			raise SystemExit("KeyboardInterrupt")
