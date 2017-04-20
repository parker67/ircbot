import logging

class customlog(object):
	#def __init__(self):
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	logger.info('Starting IRCBOT')

	def cust_log(self, entry):
		self.logger.info(entry)