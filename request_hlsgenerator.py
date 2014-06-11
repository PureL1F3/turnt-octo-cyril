import logging
import os
import shutil
import subprocess
import time
import sys
import mysql.connector

FFMPEG_CREATE_WAIT = 0.2 # wait from when create request to get m3u8 playlist file
FFMPEG_MAX_WAIT_FOR_PLAYLIST = 1500


# request input
requestid = None
url = None

# logfile
logfile = None
logger = None

# db
db_host = '167.88.34.62'
db_user = 'Brun0'
db_pwd = '65UB3b3$'
db_name = 'vidblit'
cnx = None


def get_request_params():
    vtype = sys.argv[1]
    requestid = sys.argv[2]
    src_path = sys.argv[3]
    return (vtype, requestid, src_path)

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

def start_ffmeg_hlsgen(vtype, requestid, src_path, dest_path):
    logger.info('Creating directory for ffmpeg hls generation at {0}'.format(dest_path))
    if os.path.exists(dest_path):
        logger.info('Removing existing')
        shutil.rmtree(dest_path)
    os.makedirs(dest_path)
    
    os.chdir(dest_path)
    dest_playlist_path = 'playlist.m3u8'
    dest_segmentfmt_path = 'out%03d.ts'
    
    ffmpeg_cmd = r'ffmpeg -i "{0}" -map 0 -codec:v libx264 -codec:a libfaac -f ssegment -segment_list {1} -segment_list_flags +live -segment_time 10 {2}'.format(src_path, dest_playlist_path, dest_segmentfmt_path)
    output_file = open(logfile, 'a')
    logger.info('Preparing to run ffmpeg with command:\n{0}'.format(ffmpeg_cmd))
    p = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    dest_playlist_path = '{0}/playlist.m3u8'.format(dest_path)    
    playlistAvailable = False
    for i in range(FFMPEG_MAX_WAIT_FOR_PLAYLIST):
        time.sleep(FFMPEG_CREATE_WAIT)
        if os.path.exists(dest_playlist_path):
            time.sleep(10)
            UpdateRequestPlaylistCreated(vtype, requestid, dest_playlist_path)
            playlistAvailable = True
            break
    
    if not playlistAvailable:
        FinishWithError(requestid, "Could not process video")

    logger.info("Waiting for ffmpeg to finish")
    p.wait()
    logger.info("ffmpeg finished - hls creation successful")

def FinishWithError(requestid, error):
    logger.info('Finished with error: {0}'.format(error))
    cursor = cnx.cursor()
    args = (requestid, 'ERROR', error)
    cursor.callproc('request_error', args)
    cursor = cnx.cursor()
    cnx.close()
    sys.exit()

def UpdateRequestPlaylistCreated(vtype, requestid, url):
    logger.info('Created playlist at url: {0}'.format(url))
    cursor = cnx.cursor()
    args = (requestid, url)
    if vtype == 'source':
        cursor.callproc('request_create_locationsource', args)
    else:
        cursor.callproc('request_create_locationdestination', args)
    cursor = cnx.cursor()
    cnx.close()

logger = get_logger(logfile)
if __name__ == '__main__':
    vtype, requestid, src_path = get_request_params()
    #vtype = 'destination'
    #requestid = 2
    #src_path = r'https://r5---sn-gvbxgn-tt1z.googlevideo.com/videoplayback?mt=1402263737&gcr=ca&mv=m&ipbits=0&ratebypass=yes&sparams=gcr%2Cid%2Cip%2Cipbits%2Citag%2Cratebypass%2Crequiressl%2Csource%2Cupn%2Cexpire&source=youtube&ms=au&fexp=908566%2C910207%2C913434%2C923341%2C929305%2C930008%2C931979%2C932617%2C933907%2C938805&expire=1402286135&sver=3&ip=99.233.86.161&key=yt5&mws=yes&upn=ukD10nTOgaA&id=o-AHm0IDTtt_giUrpSShTaSQFx3MaVXiLkdRSPLhyxqbly&itag=43&requiressl=yes&signature=CBCD7C7B76F883469FF67EFABAD463EBDCD04628.096A4E92882A55A26FD2B6A0B8EC3C708ADD2EE0'
    dest_path = '/vidblit/videos/requests/{0}/{1}'.format(requestid, vtype)
    logfile = '/vidblit/logs/requests/{0}/playlist_gen_{1}.log'.format(requestid, vtype)
    logger = get_logger(logfile)
    cnx = mysql.connector.connect(host=db_host, user=db_user, password=db_pwd, database=db_name)
    start_ffmeg_hlsgen(vtype, requestid, src_path, dest_path)
