# coding=utf-8

#!/usr/bin/python
# FileName: upload.py
# author: Anakin Song
import os
import sys
import hashlib
import json
import urllib2
import urllib
import zipfile
import commands
import time
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from sys import argv
from multiprocessing import Process

url = ""

def is_ok(name):
    white = ['lua', 'jpg', 'png', 'plist', 'zip',
            'json', 'mp3', 'ogg', 'fnt', 'ttf',
            'zip', 'txt', 'py', 'zh']
    if name[0] == '.':
        return False
    for suffix in white:
        if name[-len(suffix):] == suffix:
            return True
        elif 'ygt' in name:
            return True
    return False

def is_path_ok(re_path):
    #white = ['res_raw/', 'scripts_raw/', 'monitor_agent/']
    white = ['res/', 'scripts/', 'monitor_agent/']
    for name in white:
        if re_path.startswith(name):
            return True
    return False

def scan(project_dir, ans):  #扫描文件目录计算md5值
    print 'scan dir ', project_dir

    for root, dirs, files in os.walk(project_dir, True):
        for name in files:
            if not is_ok(name):
                continue
            ab_path = os.path.join(root, name),  # 绝对路径
            re_path = os.path.relpath(ab_path[0], project_dir)  # 相对路径
            if not is_ok(re_path):
                continue
            if not is_path_ok(re_path):
                continue
            #print re_path
            handle = open(ab_path[0])
            data = handle.read()
            size = len(data)
            handle.close()
            checksum = hashlib.new("md5", data).hexdigest()
            ans.append({'name': name, 'md5': checksum, 'path': re_path, 'ab_path': ab_path[0], 'size': size})
    return ans

def upload(ans, url, version, level, game):
    global session
    files = []
    for i in ans:
        #print "name:%s md5:%s path:%s"%(i['name'], i['md5'], i['path'])
        files.append({ 'md5': i['md5'], 'path': i['path'], 'size': i['size']})
    args = {'game' : game, 'vsn' : version, 'lv' : level, 'files' : files}
    post_data = {'data': json.JSONEncoder().encode(args)}
    print post_data
    req = urllib2.Request(url + "cliapp/upload_index", urllib.urlencode(post_data))
    response = urllib2.urlopen(req)
    res = json.loads(response.read())

    print "res[error]", res["error"]
    print "res filelist len:%d"%(len(res.get('filelist', {})))
    if res['error'] == 2:
        print u'重复的版本'
    elif len(res['filelist']) == 0:  #没有需要上传的文件
        print u"没有文件需要上传"
    elif res['error'] != 0:  #服务端错误
        print u'系统错误, errno : %d' % res['error']
    else:
        #首先打包zip文件
        zip_path = "/tmp/" + game + '_' + version + '.zip'
        zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        zcount = 0
        for i in res['filelist']:
            for j in ans:
                if j['md5'] == i:
                    zcount += 1
                    zip_file.write(j['ab_path'], j['md5'])
                    break
        zip_file.close()
        print("zcount:%d"%(zcount))
        register_openers()
        # datagen: 对POST参数的encode(multipart/form-data)
        # headers: 发起POST请求时的http header的信息

        datagen, headers = multipart_encode(
            {'file': open(zip_path, 'rb'), 'vsn': version, 'game': game})
        # Create a Request object
        request = urllib2.Request(url + "cliapp/upload_file", datagen, headers)
        # Actually do POST request
        response = urllib2.urlopen(request)
        print "over", response.read()

game_oppo = "oppo"
version_oppo = '1.8.64'
level_oppo = 0
game_vivo = "vivo"
version_vivo = '1.8.60'
level_vivo = 0
game_lenovo = "lenovo"
version_lenovo = '1.5.36'
level_lenovo = 0
game_mz = "mz"
version_mz = '1.5.38'
level_mz = 0

def upload_pack(source_dir, name, up_url):
    source_dir = "%s/bin/hookheroes2/assets/%sres"%(source_dir, name)

    '''
    @doc
    game :: 游戏名字
    url  :: 版本服务器地址，只需要地址加端口
    version :: 版本号 xx.xx.xx
    level :: 本次版本等级，2 : 大版本，需要到平台下载， 非 2：小版本，
    '''
    game = name
    url = up_url 
    if name == game_oppo:
        version = version_oppo
        level = level_oppo
    if name == game_vivo:
        version = version_vivo
        level = level_vivo
    if name == game_lenovo:
        version = version_lenovo
        level = level_lenovo
    if name == game_mz:
        version = version_mz
        level = level_mz
    # 0：更新不重启，1： 更新必须重启，2 ： 必须去appstore 下载

    print "=============================================================="
    print "project_dir:", source_dir
    print "game:", game
    print "upload url:", url
    print "version:", version
    print "level:", level
    print "=============================================================="
    #confirm = raw_input("is the upload info right? [y/n]")
    #if confirm <> 'y' and confirm <> 'Y':
        #sys.exit(0)
    #res = scan("/Users/chockly/hhnew/quick-cocos2d-x-2.2.6-release/bin/hookheroes", [])
    #res = scan("/Users/songxiao/Downloads/cliapp", [])
    res = scan(source_dir, [])
    upload(res, url, version, level, game)

if __name__ == '__main__':
    print 'sys.argv', argv
    source_dir = commands.getoutput("echo ${QUICK_COCOS2DX_ROOT}")
    if len(source_dir) < 5:
        print("not found shell env variable QUICK_COCOS2DX_ROOT .")
        sys.exit(0)
    if source_dir[-1] == '/':
        source_dir = source_dir[0:-2]
    print source_dir


    processes = list()
    yh_url = "http://106.14.201.219:2052/" 
    print "=============================================================="
    print "upload url:", yh_url
    print "=============================================================="
    print "game_oppo:", game_oppo
    print "version_oppo:", version_oppo
    print "level_oppo:", level_oppo
    print "=============================================================="
    print "game_vivo:", game_vivo
    print "version_vivo:", version_vivo
    print "level_vivo:", level_vivo
    print "=============================================================="
    print "game_lenovo:", game_lenovo
    print "version_lenovo:", version_lenovo
    print "level_lenovo:", level_lenovo
    print "=============================================================="
    print "game_mz:", game_mz
    print "version_mz:", version_mz
    print "level_mz:", level_mz
    print "=============================================================="

    confirm = raw_input("is the upload info right? [y/n]")
    if confirm <> 'y' and confirm <> 'Y':
        sys.exit(0)

    p_oppo = Process(target = upload_pack, args = (source_dir, game_oppo, yh_url,))
    p_vivo = Process(target = upload_pack, args = (source_dir, game_vivo, yh_url,))
    p_lenovo = Process(target = upload_pack, args = (source_dir, game_lenovo, yh_url,))
    p_mz = Process(target = upload_pack, args = (source_dir, game_mz, yh_url,))

    p_oppo.start()
    processes.append(p_oppo)
    p_vivo.start()
    processes.append(p_vivo)
    p_lenovo.start()
    processes.append(p_lenovo)
    p_mz.start()
    processes.append(p_mz)

    for p in processes:
        p.join()
