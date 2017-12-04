#!/usr/bin/env python
# encoding: utf-8

import re
import os
import pandas
import time
from datetime import datetime

# os.chdir(os.path.abspath('D:\workspace\GitHub\sec-edgar'))
# os.chdir(os.path.abspath('D:\workspace\TwCrawler'))
# sys.path.append("D:\workspace\TwCrawler")
import SecCrawler

# read in data
sp500 = pandas.read_csv('D:\workspace\TwCrawler\SP500.csv')
if sp500.shape[1] == 8:
    sp500 = sp500.assign(trBlockPrev="")
    sp500 = sp500.assign(trBlock="")
    sp500 = sp500.assign(trBlockNext="")

    sp500 = sp500.assign(Remarks="")

# loop thru each row = company
loop = 0
for loop in range(0, 505):
    if 400 <= loop < 505: # Number/Index of Rows to Run; Processed 0-49
        # read crawling parameters from SP500.csv
        companyCode = sp500['Ticker symbol'][loop]
        cik = sp500['CIK'][loop]
        date = "20161128"
        count = 1
        print('Acquired Info:', companyCode, cik)

        remark = ""
        data = ""
        start = None
        end = None
        trBlock0 = ""
        trBlock1 = ""
        trBlock2 = ""

        # crawl 10K report
        SecCrawler.get_filings_par(str(companyCode), str(cik), str(date), str(count))
        # if failed:
        #   date2 = "20151231"
        #   SecCrawler.get_filings(str(companyCode), str(cik), str(date2), str(count))

        # find the file
        filePath = os.path.join('D:\workspace\GitHub\sec-edgar\SEC-Edgar-Data', str(companyCode), str(cik), '10-K')
        fileList = os.listdir(filePath)
        if len(fileList) >= 1:
            fileName = fileList[0]
        else:
            print('FILE NOT FOUND!')
            remark += '[file NOT found]'
            sp500['Remarks'][loop] = remark
            continue

        fileNameAbs = os.path.join(filePath, fileName)
        try:
            with open(fileNameAbs, 'r') as fr:
                data = fr.read()
                # data = fr.read().replace('\n', '')
            print('File Connected. Length:', len(data))
        except:
            print('FILE NOT FOUND!')
            remark += '[file NOT found]'
            sp500['Remarks'][loop] = remark
            continue

        # truncate the file using string "POWER OF ATTORNEY"  ~~ "Chief Executive Officer"
        start = re.search('POWER OF ATTORNEY', data)
        if start is None:
            print("P.O.A. NOT found! ")
            start = re.search('Signature', data, re.IGNORECASE)
            remark += '[P.O.A. NOT found, search "SIGNATURE"]'
            if start is None:
                print("Sign. NOT found! ")
                remark += '[SIG. NOT found, use manual search line ~80]'
                sp500['Remarks'][loop] = remark
                continue  # jump to next loop to extract next file
            else:
                startLocation = start.span()[0]
                data = data[startLocation:]
        else:
            startLocation = start.span()[0]
            data = data[startLocation:]

        for end in re.finditer(r'Chief Executive Officer', data, re.IGNORECASE):
            pass
            # print(data[end.span()[0]-80:end.span()[1]+80]) # Manually extracting info about CEO
        if end is not None:
            endLocation = min(end.span()[1] + 2000, len(data))
            data = data[:endLocation]
            print('File Truncated.', len(data))
        else:
            remark += '[C.E.O. NOT found!]'
            sp500['Remarks'][loop] = remark
            continue  # jump to next loop to extract file

        # removing html tags: <td></td>, <div></div>, <font></font>, &#160;, multiple white space chars
        p = re.compile('<td[\w\s=.,:;"#%-]*>', re.I)
        data = p.sub('', data)

        p = re.compile('<font[\w\s=.,:;"#%-]*>', re.I)
        data = p.sub('|', data)

        p = re.compile('<div[\w\s=.,:;"#%-]*>', re.I)
        data = p.sub('', data)

        p = re.compile('</td>', re.I)
        data = p.sub('', data)

        p = re.compile('</font>', re.I)
        data = p.sub('', data)

        p = re.compile('</div>', re.I)
        data = p.sub('', data)

        p = re.compile('&#160;')
        data = p.sub('', data)

        p = re.compile('(\s)+')
        data = p.sub(' ', data)

        print('File length - removing tags', len(data))

        # fetch CEO block using Regex
        ceoLocation = len(data)
        patternCEO = re.compile('Chief Executive Officer')
        ceoLocation = patternCEO.search(data).span()[0]

        trLocation = []
        patternTr = re.compile('<tr[\w\s=:;"#%-]*>', re.IGNORECASE)
        for match in patternTr.finditer(data):
            trLocation.append(match.span()[0])

        trEndLocation = []
        patternTrEnd = re.compile('</tr[\w\s=:;"#%-]*>', re.IGNORECASE)
        for match in patternTrEnd.finditer(data):
            trEndLocation.append(match.span()[0])

        if (len(trLocation) > 0 and len(trEndLocation) > 0):
            while trEndLocation[0] < trLocation[0]:
                del trEndLocation[0]

        # save the name in pandas dataframe
        for i in range(len(trLocation)):
            if trLocation[i] <= ceoLocation < trEndLocation[i]:
                trBlock1 = data[trLocation[i]:trEndLocation[i]]

                if i < (len(trLocation) - 1) and i < len(trEndLocation) - 1:
                    if trLocation[i + 1] < len(data) and trEndLocation[i + 1] < len(data):
                        trBlock2 = data[trLocation[i+1]:trEndLocation[i+1]]

                if i > 0:
                    trBlock0 = data[trLocation[i - 1]:trEndLocation[i - 1]]

        sp500['trBlockPrev'][loop] = trBlock0
        sp500['trBlock'][loop] = trBlock1
        sp500['trBlockNext'][loop] = trBlock2

        sp500['Remarks'][loop] = remark
        print('record updated at row:', loop)

        time.sleep(1)

    loop += 1

# save edited dataframe
fileSaveName = 'SP500WithNames' + datetime.now().strftime('%m%d_%H%M%S') + '.csv'
sp500.to_csv(fileSaveName)