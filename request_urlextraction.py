import youtube_dl
import logging
import sys
import os
import traceback
import mysql.connector
import json

# request input
requestid = None
url = None

# logfile
logfile = None
logger = None

# ydl
ydl_params = {}
ydl = None

# db
db_host = '167.88.34.62'
db_user = 'Brun0'
db_pwd = '65UB3b3$'
db_name = 'vidblit'
cnx = None

def get_request_params():
    requestid = sys.argv[1]
    url = sys.argv[2]
    return (requestid, url)

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

def get_ydl(params):
    logger.info('Setting up ydl')
    ydl = youtube_dl.YoutubeDL(params)
    ydl.add_default_info_extractors()
    return ydl

def get_suitable_extractor(url):
    logger.info('Looking for a suitable extractor')
    iekey = None
    for ie in ydl._ies:
        if ie.suitable(url):
            iekey = ie.ie_key()
            logger.info('Found suitable extractor: {0}'.format(iekey))
            break;
    return iekey

def get_extraction_result(extractor_key, url):
    logger.info('Performing info extraction')
    result = ydl.extract_info(url, download=False, ie_key=extractor_key)
    logger.info('Received info extraction result:\n{0}'.format(result))
    return result

def FinishWithError(requestid, error):
    logger.info('Finished with error: {0}'.format(error))
    cursor = cnx.cursor()
    args = (requestid, 'ERROR', error)
    cursor.callproc('request_error', args)
    cursor = cnx.cursor()
    cnx.close()
    sys.exit()
    
def GetSmallestUrl(extractor, result):
    extractor = extractor.lower()
    url = None
    if extractor == 'vine':
        url = GetVineSmallestUrl(result)
    elif extractor == 'youtube':
        url = GetYoutubeSmallestUrl(result)
    elif extractor == 'vimeo':
        url = GetVimeoSmallestUrl(result)
    
    if url is None:
        url = result['url']
    return url

def FinishWithSuccess(requestid, result, url, title, vtype, length):
    logger.info('Finished with success: {0}'.format(result))
    cursor = cnx.cursor()
    extractor = result['extractor']
    url = GetSmallestUrl(extractor, result)
    args = (requestid, url, result['title'], json.dumps(result), extractor, 0)
    cursor.callproc('request_create_extractresult', args)
    cursor = cnx.cursor()
    cnx.close()

def GetYoutubeSmallestUrl(result):
    smallest_url = None
    try:
        good_format_ids = ("36", "5", "18")
        good_formats = {}
        result_formats = result['formats']
        for f in result_formats:
            if f['format_id'] in good_format_ids:
                good_formats[f['format_id']] = f['url']
        for f in good_format_ids:
            if f in good_formats.keys():
                smallest_url = good_formats[f]
                break
    except:
        logger.info('Error running smallest vine url:\n: {0}'.format(traceback.print_exc()))
    return smallest_url    

def GetVineSmallestUrl(result):
    smallest_url = None
    try:
        result_formats = result['formats']
        smallest_url = None
        for f in result_formats:
            if f['format_id'] == 'low':
                smallest_url = f['url']
                break
    except:
	logger.info('Error running smallest vine url:\n: {0}'.format(traceback.print_exc()))
    return smallest_url

def GetVimeoSmallestUrl(result):
    smallest_url = None
    try:
        result_formats = result["formats"]
        smallest_format = None
        smallest_area = 1000000000
        smallest_url = None
        for f in result_formats:
            area = f['height'] * f['width']
            if area < smallest_area:
                smallest_format = f
                smallest_area = area
                smallest_url = f['url']
    except:
        logger.info('Error running smallest vimeo url:\n: {0}'.format(traceback.print_exc()))
    return smallest_url

logger = get_logger(logfile)
if __name__ == '__main__':
    requestid, url = get_request_params()
    #requestid = 2
    #url = "https://vine.co/v/b9KOOWX7HUx"
    logfile = '/vidblit/logs/requests/{0}/extraction.log'.format(requestid)
    logger = get_logger(logfile)
    cnx = mysql.connector.connect(host=db_host, user=db_user, password=db_pwd, database=db_name)
    ydl = get_ydl(ydl_params)
    
    extractor_key = get_suitable_extractor(url)
    if extractor_key is None:
        logger.info("Failed to find suitable extractor for url")
        FinishWithError(requestid, 'Sorry this url is not supported')
    result = None
    try:
        result = get_extraction_result(extractor_key, url)
    except:
        logger.info("Could not get video info:\n{0}".format(traceback.format_exc()))
        FinishWithError(requestid, 'Sorry this video is not available')
    FinishWithSuccess(requestid, result, 'url', 'title', 'type', 100)
