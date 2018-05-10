#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Order photoes and videos according to Exif infomation or ctime.
#
# Order your photos and video like this:
#
#   201805/Canon Canon EOS600D/IMG_20180511_121002.JPG
#
#   201805/Videos/VID_20180511_121002.mov
#
# Suport file formate:  jpg,JPG,CR2,cr2,mov,MOV,mp4,MP4,avi,AVI,3gp,3GP
#
# Author: sunyimo
#
# Using Python2.7.14 + exifread
#
# Examples:
#   In command line:
#
#           Python2.7 orderphotovideo -i /src/ -o /des/ --move
#i      OR
#           ./orderphotovideo -i /src/ -o /des/ --move
#
#
#

import time
import sys
import getopt
import exifread
import shutil
import os
import md5

"""
generate MD5 code for a photo or video, to compare it with the other
"""
def generate_md5(photo):
    fp=open(photo,'rb')
    m=md5.new()
    while True:
        d=fp.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

"""
generate dirs and name for a photo or vedio,according to its' EXIF
"""
def generate_des(photo):
    photo_name=os.path.basename(photo)
    photo_type=photo_name.split('.')[1]
    if photo_type in ("jpg","JPG","CR2","cr2"):
        fp=open(photo)
        tags=exifread.process_file(fp)
        fp.close()

        if "Image Make" in tags.keys():
            ImageMake=str(tags["Image Make"]).strip()+" "
        else:
            ImageMake=""

        if "Image Model" in tags.keys():
            ImageModel=str(tags["Image Model"]).strip()
            ImageModel=ImageModel.replace("/"," ").replace("\\"," ")
            ImageModel=ImageModel.replace("<","(").replace(">",")")
        else:
            ImageModel="Other Devices"

        if "EXIF DateTimeOriginal" in tags.keys():
            DateTime=str(tags["EXIF DateTimeOriginal"]).replace(':','').replace(' ','_')
        else:
            DateTime=os.path.getmtime(photo)
            DateTime=time.localtime(DateTime)
            DateTime=time.strftime('%Y%m%d_%H%M%S',DateTime)

        photo_dirname=os.path.join(DateTime[:6],ImageMake+ImageModel)
        photo_basename="IMG_"+DateTime+"."+photo_type

    if photo_type in ("mp4","MP4","mov","MOV","avi","AVI","3gp","3GP"):
        DateTime=os.path.getmtime(photo)
        DateTime=time.localtime(DateTime)
        DateTime=time.strftime('%Y%m%d_%H%M%S',DateTime)
        photo_dirname=os.path.join(DateTime[:6],"Videos")
        photo_basename="VID_"+DateTime+"."+photo_type

    return os.path.join(photo_dirname,photo_basename)

"""
process a photo or vedio,move it to destination
"""
def process_file(src,outputfile,flag):
    file_type=os.path.basename(src).split(".")[1]
    if file_type not in ("jpg","JPG","CR2","cr2","mov","MOV","mp4","MP4","avi","AVI","3gp","3GP"):
        print("%s is neither a photo or video"%src)
        return
    des=generate_des(src)
    des=os.path.join(outputfile,des)
    dirname=os.path.dirname(des)
    if False==os.path.exists(dirname):
        os.makedirs(dirname)

    basename=os.path.basename(des)
    new_des=des
    tail=0
    while os.path.exists(new_des):
        if tail==0:
            md5_src=generate_md5(src)
        md5_des=generate_md5(new_des)
        if md5_src==md5_des:
            os.remove(new_des)
            break
        tail+=1
        new_basename=basename.split('.')[0]+'_'+str(tail)+'.'+basename.split('.')[1]
        new_des=os.path.join(dirname,new_basename)

    print("%s ---- %s"%(src,new_des))
    if flag=="move":
        os.rename(src,new_des)
"""
search every dirs to process photo or vedio
"""
def orderphotovideo(inputfile,outputfile,flag):
    if not os.path.exists(inputfile):
        print("ERROR: %s is not exists"%inputfile)
        sys.exit()
    if not os.path.exists(outputfile):
        os.mkdir(outputfile)

    for photofile in os.listdir(inputfile):
        photofile=os.path.join(inputfile,photofile)
        if os.path.isfile(photofile):
            process_file(photofile,outputfile,flag)
        elif os.path.isdir(photofile):
            orderphotovideo(photofile,outputfile,flag)
        else:
            print("%s is neither a dir or a photo/video"%photofile)


def main():
    inputfile=''
    outputfile=''
    flag=''
    try:
        opts,args=getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile=","move"])
    except getopt.GetoptError:
        print("photo_rename.py -i <inputfile> -o <outputfile> --[move]")
        sys.exit(2)

    for opt,arg in opts:
        if opt=="-h":
            print("photo_rename.py -i <inputfile> -o <outputfile> --[move]")
            sys.exit()
        elif opt in ("-i","--ifile"):
            inputfile=arg
        elif opt in ("-o","--ofile"):
            outputfile=arg
        elif opt in ("--copy","--move","--find"):
            flag=opt.replace("-","")
        else:
             print("photo_rename.py -i <inputfile> -o <outputfile> --[move]")
             sys.exit()

    if inputfile!='' and outputfile!='' and flag !="":
        orderphotovideo(inputfile,outputfile,flag)


if __name__=='__main__':
    main()





