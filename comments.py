#!usr/bin/env python
# --coding:utf-8--
# copyright:Pzoom@BUAA
# 2017.9.27-
# 参考链接：https://www.zhihu.com/question/36081767/answer/65820705

import requests
import json
import os
import base64
from Crypto.Cipher import AES
from pprint import pprint
import time
import sys
from math import *
import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://cn-north-1.queue.amazonaws.com.cn/444376591338/sicm'

userId = ''
err_userId=''
results = []
playList_ids = []
url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_29393669/?csrf_token='

def buildHTML_head(userId):
    newPage=open("../"+str(userId)+".temp","w")
    print("hhh")
    newPage.write("<html>\n<head>\n<meta charset='UTF-8'>\n")
    newPage.write("<title>ta的评论</title>")
    newPage.write("<link rel='stylesheet' href='../style/comment.css' type='text/css'/>\n</head><body>\n")
    newPage.close()

def buildHTML_body(userId,songName,comment,songID):
    newPage=open("../"+str(userId)+".temp","a+")
    newPage.write("<p>ta在<a href='http://music.163.com/#/song?id="+str(songID)+"'><u>《"+str(songName)+"》</u></a>里说：</p>\n")
    newPage.write("<h3>“"+str(comment)+"”</h3>\n")
    newPage.close()

def buildHTML_tail(userId):
    newPage=open("../"+str(userId)+".temp","a+")
    newPage.write("</body>\n</html>\n")
    newPage.close()

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]


def dataGenerator(limit, offset):

    text = {
        'limit': limit,
        'offset': offset
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return data

def pre_steps(userId):
    headers = {
        'Cookie': 'appver=1.5.0.75771;',
        'Referer': 'http://music.163.com/'
    }
    text = {
        'uid': userId,
        'type': '0'
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    # playlist check
    req = requests.post('http://music.163.com/weapi/v1/play/record?csrf_token=', headers=headers, data=data)
    # print(req.json()['allData'])
    for song in req.json()['allData']:
        playList_ids.append({'id': song['song']['id'], 'name': song['song']['name']})
    print("{} songs inside\n".format(len(playList_ids)))

def number_of_comments(url):
    headers = {
        'Cookie': 'appver=1.5.0.75771',
        'Referer': 'http://music.163.com/'
    }
    data = dataGenerator(1, 0)
    req = requests.post(url, headers=headers, data=data)
    print("total comments:{}".format(req.json()['total']))
    return req.json()['total']

def search_start(limit, offset):
    for song in playList_ids:
        comments_url =  'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}/?csrf_token='.format(song['id'])
        song_name = song['name']
        song_name = song_name.encode('utf-8')
        # offset
        _offset = offset

        # 评论总数查询
        totalComments = number_of_comments(comments_url)

        while _offset < totalComments:
            time.sleep(2)
            sys.stdout.write("\rchecking songs: %s, progress: %s/%s, comments found: %d" % (song_name, _offset, totalComments, len(results)))
            sys.stdout.flush()
            headers = {
                'Cookie': 'appver=1.5.0.75771',
                'Referer': 'http://music.163.com/'
            }
            data = dataGenerator(limit, _offset)
            try:
                req = requests.post(comments_url, headers=headers, data=data)
            except requests.exceptions.ConnectionError, e:
                print('\nnetwork error.retrying..\n')
                continue

            index = 0
            for content in req.json()['comments']:
                index = index + 1
                if content['user']['userId'] == int(userId):
                    buildHTML_body(userId,song_name,content['content'].encode('utf-8'),song['id'])
            # print("本次查询完毕\n")
            _offset += limit
        print("\n\n")
    print("An~d we are done! Results.length = {}".format(len(results)))


    
    
failure_time=0#被反爬虫的次数。一旦次数超过10次，就先休息一下
while (True):#死循环，处理当前问题
    nonempty=0#0表示当前没有需要处理的userId
    while(nonempty==0):#等待新的userId进入
        print(str(nonempty)+"---\n")
        # Receive message from SQS queue
        response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
        )

        if ('Messages' in response):
            nonempty=1
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            userId=message['MessageAttributes'].get('UserID').get('StringValue')
            print(userId+"!!!")
        else:
            time.sleep(10)
    print(";;;\n")
    buildHTML_head(userId)
    try:
        pre_steps(userId)
    except KeyError:#隐私保护
        print("privacy\n")
        os.system("cp ../empty.html ../"+str(userId)+".html")
        # Delete received message from queue
        sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
        )
    try:
        search_start(1000, 0)
        # Delete received message from queue
        sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
        )
        buildHTML_tail(userId)
        os.rename("../"+str(userId)+".temp","../"+str(userId)+".html")#html上线
    except ValueError:
        failure_time+=1
        if (failure_time>5):
            os.system("cp ../sad.html ../"+str(userId)+".html")
            time.sleep(20000)#“避避风头”
            failure_time=0
    if (str(userId)=="135734841"):
        os.system("cp ../lyd.html ../"+str(userId)+".html")

    
