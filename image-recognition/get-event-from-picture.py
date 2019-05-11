import requests
import logging
import time, re
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)s(%(levelname)s): %(message)s',level=logging.ERROR)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--url", help="", type=str)
args = parser.parse_args()

imagePath = args.url

mode = "URL" # default mode

azureEndpoint = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0'
# Azure access point consists of your endpoint + the specific service to use
azureURL = azureEndpoint + '/recognizeText?mode=Printed'
# key to Azure Cloud
key = 'insert API key here'

# Headers for URL call
headersURL = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': key }

def parseResults(result):
    '''parse for text in json object and check lines for dates and
    return a tuple containing a list that has the valid ones and
    a list that has the normal text lines.
    '''
    # list to store the regEx results in
    dates = []
    textLines = []
    # lines is an array that holds all the recognized text
    for line in result['recognitionResult']['lines']:
        text = line['text']
        # search for dates via regular expression
        re_pattern = '[0-9]{1,2}\\.[0-9]{1,2}\\.[20]*[1,2][0-9]'
        match = re.search(re_pattern, text)
        if (match):
            dateText = match.group()
            logger.info("Date: " + dateText)
            dates.append(dateText)
        else:
            logger.debug('Not a date: ' + text)
            textLines.append(text)
    logger.debug('returned dates: ' + str(dates))
    return dates, textLines

def getResult(url):
    '''get result of recognizeTextFromImage() request
    '''
    time.sleep(3) # give Azure time to compute
    try:
        i = 0
        # get the response of the image recognition
        request2 = requests.get(url, headers=headersURL)
        logger.debug ('STATUSTEXT: ' + request2.text)
        # test whether Azure needs more computing time. Break the loop after 10 tries
        while((request2.json()['status'] == 'Running' or request2.json()['status'] == 'Not started') and i <= 9):
            time.sleep(2)
            logger.debug ('STATUSTEXT in loop: ' + request2.text)
            logger.debug ("Loop iteration :" + str(i))
            i += 1
            try:
                request2 = requests.get(url, headers=headersURL)
            except requests.exceptions.RequestException as e:
                logger.exception ('RequestException in while loop: ' + e)
            # log unusual behaviour
            if i == 5:
                logger.warn('Azure computing needs longer than usual.')
            if i == 9:
                logger.error('Break loop after trying to get result for 20 seconds' )
        result = request2.json()        
        return result
    except requests.exceptions.RequestException as e:
        logger.critical('RequestException: ')
        logger.exception(e)
        return
    except Exception as e:
        logger.critical('Miscellaneous exception: ')
        logger.exception(e)
        return

def recognizeTextFromImage(mode, file):
    '''Post image to Azure cloud and call getResult() to get response text.

    Arguments:
    mode -- specifies in which mode the post request is done ('local', 'URL')
    file -- specifies which file to post (*.jpg, *.jpeg, *.bmp, *.png)

    Parameters:
    data -- file in binary, used for local access
    jsonData -- requestbody in json format ({"url": "imageURL"})
    request -- request object of post request. Used to access its headers (request.headers)
    '''
    try:
        if mode == 'local':
            # TO DO
            print("local mode not implemented yet")
        elif mode == 'URL':
            jsonData = {"url": file}
            request = requests.post(azureURL, headers=headersURL, json=jsonData, timeout=10)
        else:
            logger.error('recognizeTextFromImage() was called with wrong mode')
            return
    except requests.exceptions.RequestException as e:
        logger.critical('Can\'t access Azure services')
        logger.exception(e)
    except Exception as e:
        logger.critical('undefinded problem in recognizeTextFromImage')
        logger.exception(e)
    try:
        response = request.headers['Operation-Location']
        logger.debug(response)
        result = getResult(response)
        return result
    except Exception as e:
        logger.error('Exception:')
        logger.error(request.text)
        logger.exception(e)
    except Exception as e:
        logger.error('Exception:')
        logger.error(request.text)
        logger.exception(e)

result = recognizeTextFromImage(mode, imagePath)
if result:
    datesAndRest = parseResults(result)
    print("\nDate:")
    print(datesAndRest[0])
    print("\nOther text")
    print(datesAndRest[1]) 