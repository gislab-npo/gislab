# BSD Licensed, Copyright (c) 2006-2008 MetaCarta, Inc.
import time

class Cache (object):
	def __init__ (self, timeout = 30.0, stale_interval = 300.0, readonly = False, sendfile = False, **kwargs):
		self.stale	  = float(stale_interval)
		self.timeout = float(timeout)
		self.readonly = readonly
		self.sendfile = sendfile

	def lock (self, tile, blocking = True):
		start_time = time.time()
		result = self.attempt_lock(tile)
		if result:
			return True
		elif not blocking:
			return False
		while result is not True:
			if time.time() - start_time > self.timeout:
				raise Exception("You appear to have a stuck lock. You may wish to remove the lock named:\n%s" % self.get_lock_name(tile))
			time.sleep(0.25)
			result = self.attempt_lock(tile)
		return True

	def get_lock_name (self, tile):
		return self.get_key(tile) + ".lck"

	def get_key (self, tile):
		raise NotImplementedError()

	def attempt_lock (self, tile):
		raise NotImplementedError()

	def unlock (self, tile):
		raise NotImplementedError()

	def get (self, tile):
		raise NotImplementedError()

	def set (self, tile, data):
		raise NotImplementedError()

	def delete(self, tile):
		raise NotImplementedError()

	def delete_layer_cache (self, layer):
		raise NotImplementedError()

# vim: set ts=4 sts=4 sw=4 noet:
