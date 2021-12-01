
from datetime import datetime
from datetime import timedelta
import argparse
from pathlib import Path
import os.path
from os import path

import pytz
import requests
import multiprocessing as mp

def usage():
    message="usage: $0 -s START -e END [-p PERIOD] [-o OUTDIR] [-l FILELIST]\n\nSTART, END: ISO-format dates (e.g., 2020-10-10T10:10)\nPERIOD: Number of seconds between downloads [1 week]\nOUTDIR: Where to place dumps [$(pwd)/bgpdumps]\nFILELIST: FIle with list of successfully downloaded dumps [dumps.%date.txt]\n\nThe following will download the midnight dump for every day in Oct. 2020:\n $0 -s 2020-10-01 -e 2020-11-01 -p 86400"
    print(message)

def download(url,outfile,f):
        if path.exists(outfile):
            print("File "+outfile+" already exists")
            text_file = open(outfile,"r+")
            f.write(outfile+"\n")
        else:
            print("Downloading "+url)
            text_file = open(outfile+".tmp","wb+")
            try:
                response = requests.get(url, stream = True)
                if (response.status_code == 200):
                    for chunk in response.iter_content(chunk_size=1024):
                        text_file.write(chunk)
                        f.write(outfile+"\n")
                else:
                        print("HTTP error "+ str(response.status_code)+"removing output file")
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                print("exception: "+url)
                f.write("exception: "+url+"\n")
            text_file.close();
            os.rename(outfile+".tmp",outfile)

def download_ris_ribs(beginTime,endTime,f):
    period=300
    epoch=datetime.strptime(beginTime, '%Y-%m-%dT%H:%M:%S-%z').timestamp()
    endepoch=datetime.strptime(endTime, '%Y-%m-%dT%H:%M:%S-%z').timestamp()
    while (epoch<endepoch):
        #    fname=bview.$(date -d @$epoch +%Y%m%d.%H%M).gz
        epochTime=datetime.utcfromtimestamp(epoch)
        fname="updates."+epochTime.strftime("%Y%m%d.%H%M")+".gz"
        for rid in range(0,26):
            if rid<10:
                ridStr="0"+str(rid)
            else:
                ridStr=str(rid)
            path="rrc"+ridStr+"/"+epochTime.strftime("%Y.%m")
            # path = "rrc"
            print(fname)
            fnumber= int(fname.split('.')[-2]) - int(fname.split('.')[-2])%5
            fname = fname.split('.')[0] +'.'+ fname.split('.')[1] +'.' + str(fnumber)+ '.'+ fname.split('.')[-1]
            url="http://data.ris.ripe.net/"+path+"/"+fname
            outfile="cache/ris.rrc"+ridStr+".updates."+str(int(epoch))+"."+str(period)+".cache"
            download(url,outfile, f)
        epoch +=period


def download_rv_ribs(beginTime,endTime,f):
    period=900
    RVDIRS=["route-views2.saopaulo","route-views3", "route-views4", "route-views6", "route-views.amsix",\
           "route-views.chicago","route-views.chile", "route-views.eqix", "route-views.flix", "route-views.fortaleza",\
            "route-views.gixa", "route-views.gorex", "route-views.isc", "route-views.jinx", "route-views.kixp",\
            "route-views.linx" ,"route-views.mwix", "route-views.napafrica","route-views.nwax", "route-views.perth",\
            "route-views.phoix", "route-views.telxatl","route-views.rio", "route-views.saopaulo", "route-views.sfmix",\
            "route-views.sg", "route-views.soxrs", "route-views.sydney", "route-views.wide"]
    #    fname=rib.$(date -d @$epoch +%Y%m%d.%H%M).bz2
    epoch=datetime.strptime(beginTime, '%Y-%m-%dT%H:%M:%S-%z').timestamp()
    endepoch=datetime.strptime(endTime, '%Y-%m-%dT%H:%M:%S-%z').timestamp()
    while (epoch<endepoch):
        epochTime=datetime.utcfromtimestamp(epoch)
    #    fname=bview.$(date -d @$epoch +%Y%m%d.%H%M).gz
        fname="updates."+epochTime.strftime("%Y%m%d.%H%M")+".bz2"
        for rtr in RVDIRS:
            path=rtr+"/bgpdata/"+epochTime.strftime("%Y.%m")+"/UPDATES"
            #path="$rtr/bgpdata/$(date -d @$epoch +%Y.%m)/RIBS"
            url="http://archive.routeviews.org/"+path+"/"+fname
            outfile="cache/routeviews."+rtr+".updates."+str(int(epoch))+"."+str(period)+".cache"
            download(url,outfile,f)
        epoch += period

def process(epoch):
    beginTime=epoch[0]
    endTime=epoch[1]
    fileName=str(epoch[3])+'-'+epoch[2]
    f = open(fileName, "a+")
    download_ris_ribs(beginTime,endTime,f)
    download_rv_ribs(beginTime,endTime,f)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    startdate = None
    enddate = None
    filelist=datetime.now().strftime("%Y%m%dT%H%M%S")+".txt"
    period= 7 * 86400
    outdir="cache"
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", default='2020-10-10T10:10:10', help="start date in 2020-10-10T10:10:10 format")
    parser.add_argument("-e", "--end",default='2020-10-10T20:10:10', help="end date in 2020-10-10T10:10:10 format")
    parser.add_argument("-f", "--filelist", help="FILELIST: FIle with list of successfully downloaded dumps [dumps.%date.txt]" )
    parser.add_argument("-p", "--procNum", help="Number of processors")
    args = parser.parse_args()
    if args.start:
        startdate=args.start
    if args.end:
        enddate=args.end
    if args.filelist:
        filelist=args.filelist
    if args.procNum:
        procNum = args.procNum
    Path(outdir).mkdir(parents=True, exist_ok=True)
    timezone = pytz.timezone("UTC")
    currepoch=datetime.strptime(startdate, '%Y-%m-%dT%H:%M:%S')
    currepoch=timezone.localize(currepoch)
    currTimestamp =900*(int(currepoch.timestamp())//900)
    currepoch=datetime.utcfromtimestamp(currTimestamp)
    currepoch=timezone.localize(currepoch)
    stopepoch=datetime.strptime(enddate, '%Y-%m-%dT%H:%M:%S')
    stopepoch=timezone.localize(stopepoch)
    stopTimestamp =max(900*(int(stopepoch.timestamp())//900+1),currTimestamp+900)
    stopepoch=datetime.utcfromtimestamp(stopTimestamp)
    stopepoch=timezone.localize(stopepoch)
    procNum=20
    intervalSize=(stopTimestamp-currTimestamp)//procNum
    epochs=[]
    beginTime=currepoch
    endTime=beginTime+timedelta(seconds=intervalSize-1)
    for i in range(0,procNum):
        epochs.append([beginTime.strftime('%Y-%m-%dT%H:%M:%S-%z'),endTime.strftime('%Y-%m-%dT%H:%M:%S-%z'),filelist,i])
        beginTime += timedelta(seconds=intervalSize)
        endTime=beginTime+timedelta(seconds=intervalSize-1)
    # pool = mp.Pool(processes=procNum)
    # pool.map(process,epochs)
    print(epochs[-1])
    process(epochs[-1])
