import logging

def customlog():
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	logger.info('Starting IRCBOT')

def log(entry):
	logger.info(entry)
