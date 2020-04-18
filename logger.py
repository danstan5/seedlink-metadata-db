import logging
import time

STARTTIME = time.time()

def since_starttime():
    since = time.time() - STARTTIME
    return '%.2f' % since

# updating log records 
factory = logging.getLogRecordFactory()
def set_record(*args, **kwargs):
    record = factory(*args, **kwargs)
    record._time = since_starttime()
    return record
logging.setLogRecordFactory(set_record)

# filehander
filehandle = logging.FileHandler('runtime.log')
formatter = logging.Formatter(
    '%(asctime)-12s %(levelname)-7s: Runtime %(_time)s s: %(name)s <%(funcName)s>: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S')
filehandle.setFormatter(formatter)

# streamhandler (console)
console = logging.StreamHandler()
formatter = logging.Formatter(
    'Runtime %(_time)s s: %(levelname)s: %(message)s')
console.setFormatter(formatter)

# logger instance
log = logging.getLogger()
log.addHandler(console)
log.addHandler(filehandle)
log.setLevel(logging.INFO)

log.debug('Logger started')
