import mysql.connector
import logging
import subprocess
import time
import os

WATCHER_SLEEP_TIME = 0.2

# logfile
logfile = None
logger = None

# db
db_host = '167.88.34.62'
db_user = 'Brun0'
db_pwd = '65UB3b3$'
db_name = 'vidblit'
cnx = None

def get_logger(logfile):
    # setup log file
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    if logfile is not None:
        logdir = os.path.dirname(logfile)
        if not os.path.exists(logdir):
            os.makedirs(logdir)        
        handler = logging.FileHandler(logfile)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
def GetNewRequests():
    sql = 'SELECT requestid, url FROM requests WHERE status IS NULL'
    logger.info('Getting new request urls to process')
    cursor = cnx.cursor()
    cursor.execute(sql)
    Requests = {}
    for (requestid, url) in cursor:
        Requests[requestid] = url
    return Requests

def GetRequestExtracts():
    sql = "select requestid, url from request_extractresults where requestid in (select requestid from requests where status='WORKING_EXTRACTED')"
    logger.info('Getting extracted urls to process')
    cursor = cnx.cursor()
    cursor.execute(sql)
    Requests = {}
    for (requestid, url) in cursor:
        Requests[requestid] = url
    return Requests
def GetRequestUploads():
    sql = "select requestid, url from request_uploads where requestid in (select requestid from requests where status='WORKING_UPLOADED')"
    logger.info('Getting upload urls to process')
    cursor = cnx.cursor()
    cursor = cnx.cursor()
    cursor.execute(sql)
    Requests = {}
    for (requestid, url) in cursor:
        Requests[requestid] = url
    return Requests

def UpdateAndProcessRequests(currentRequests, newRequests, processToStart):
    #remove any existing requests
    requestsToRemove = []
    for requestid in currentRequests.keys():
        if requestid in newRequests.keys():
            del newRequests[requestid] # existing key
        else:
            requestsToRemove.append(requestid) # old key
    
    for requestid in requestsToRemove:
        logger.info('removing old request for \nrequest - {0}\nurl - {1}\nprocess - {2}'.format(requestid, currentRequests[requestid], processToStart))
        del currentRequests[requestid] # remove old keys
        
        
    for requestid, url in newRequests.iteritems():
        currentRequests[requestid] = url # start process for request
        command = None
        if processToStart == 'new_requests':
            command = 'python2.7 request_urlextraction.py {0} "{1}"'.format(requestid, url)
        elif processToStart == 'new_extracts':
            command = 'python2.7 request_hlsgenerator.py {0} {1} "{2}"'.format('source', requestid, url)
        elif processToStart == 'new_uploads':
            command = 'python2.7 request_hlsgenerator.py {0} {1} "{2}"'.format('destination', requestid, url)
        
        logger.info('starting new process for \nrequest - {0}\nurl - {1}\nprocess - {2}\ncommand - {3}'.format(requestid, url, processToStart, command))
        subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return currentRequests
    
logger = get_logger(logfile)
if __name__ == '__main__':
    logfile = '/vidblit/logs/watcher.log'
    logger = get_logger(logfile)
    cnx = mysql.connector.connect(host=db_host, user=db_user, password=db_pwd, database=db_name)
    
    CurrentNewRequests = {}
    CurrentExtractRequests = {}
    CurrentUploadRequests = {}
    
    logger.info("Starting Watcher....")
    
    while True:
        NewNewRequests = GetNewRequests()
        NewExtractRequests = GetRequestExtracts()
        NewUploadRequests = GetRequestUploads()
        CurrentNewRequests = UpdateAndProcessRequests(CurrentNewRequests, NewNewRequests, 'new_requests')
        CurrentExtractRequests = UpdateAndProcessRequests(CurrentExtractRequests, NewExtractRequests, 'new_extracts')
        CurrentUploadRequests = UpdateAndProcessRequests(CurrentUploadRequests, NewUploadRequests, 'new_uploads')
        time.sleep(WATCHER_SLEEP_TIME)
