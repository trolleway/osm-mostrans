#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse
import urllib
import urllib2
import requests
import datetime
import json
import pprint


'''
Система тут такая.
Предварительно, обработанные данные загружаются в NextGIS Web. 
Он умеет их рендрить рендером QGIS, и отдавать картинку по bbox (в epsg:3857)
и id стилей. Пример запроса:
http://trolleway.nextgis.com/api/component/render/image?resource=759,758,760,753,715,725&extent=4161212.7615459412,7478364.404967272,4215253.740543561,7542265.760613679&size=708,836

bbox страниц и их названия хранятся в отдельном файле cfg/atlaspages.geojson
Он генерируется (сейчас вручную в qgis) так, что бы страницы накладывались друг на друга. Он может быть всё равно в какой системе координат. 
Файл geojson импортируется в PostGIS через ogr2ogr.

Этот скрипт:
-Запрашивает с сервера png на весь город, и генерит к нему world-файл.
-Сохраняет png в geotiff.
-Сохраняет geotiff на яндекс-диск

-Режет png на страницы в gdal (это сделано что бы не терялись подписи на стыках)

-Запрашивает с сервера в более крупном масштабе карту центра города
-склеивает листы в pdf
-сохраняет pdf на яндекс-диск

Конфигурирование на новый город
1. Задать листы в geojson, указать атрибуты map,ref
2. Задать названия выходных файлов в tmpfiles
3. Задать стили в переменной ngwstyles

'''

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='',
            formatter_class=PrettyFormatter)
    #parser.add_argument('--download', dest='download', action='store_true')
    #parser.add_argument('--no-download', dest='download', action='store_false')
    #parser.set_defaults(download=True)

    parser.epilog = \
        '''Samples:
%(prog)s 
''' \
        % {'prog': parser.prog}
    return parser



def upload_yandex(token,pathdata,filedata):
    #Upload file to yandex.disk from local disk
            method_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
            response = requests.get(method_url, pathdata,headers={'Authorization': 'OAuth '+token}, timeout=20)
            result = json.loads(response.text)
            upload_url = result['href']

            response = requests.put(upload_url, filedata,headers={'Authorization': 'OAuth '+token}, timeout=120)
            if response.status_code <> 201:
                print 'Error upload file to Yandex'


def render_atlas(host,dbname,user,password):

    size_main=3500

    ConnectionString="dbname=" + dbname + " user="+ user + " host=" + host + " password=" + password
    try:
        conn = psycopg2.connect(ConnectionString)
    except:
        print 'I am unable to connect to the database                  ' 
        print ConnectionString
        return 0
    cur = conn.cursor()


    #debug
    retrive_map=True




    #Получаем одну картинку со всеми слоями на всю карту

    #Генерируем к этой картинке файл привязки
    #Запрашиваем охваты отдельных страниц атласа
    #Режем картинку на страницы по географическим координатам в EPSG:3857 используя gdal
    #Собираем из страниц книжку

    now = datetime.datetime.now()

    tmpfiles=dict()   
    tmpfiles['folder'] = 'tmp'
    tmpfiles['lines'] = 'tmp/lines.png'
    tmpfiles['lines_worldfile'] = 'tmp/lines.pngw'

    tmpfiles['screenall']=os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-all-screen") #no extension
    tmpfiles['center'] = 'tmp/center.png'
    tmpfiles['center_worldfile'] = 'tmp/center.pngw'

    tmpfiles['atlas'] = 'tmp/moscow_trolleybus_ru_openstreetmap_'+now.strftime("%Y-%m-%d %H:%M")+'.pdf'
    tmpfiles['atlas_yandex'] = 'archive/moscow_trolleybus_ru_openstreetmap_'+now.strftime("%Y-%m-%d") #withouth time - only one file at day will saved

    tmpfiles['terminals'] = 'tmp/terminals.png'

    tmpfiles['stage1'] = 'tmp/stage1.tif'
    tmpfiles['background'] = 'tmp/background.png'

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    
    #Load to PostGIS config file with pages bounds
    cmd='''
ogr2ogr -f PostgreSQL "PG:host='''+host+''' dbname='''+dbname+''' user='''+user+''' password='''+password+'''" cfg/atlaspages.geojson -nln atlaspages  -overwrite    \

    '''
    
    os.system(cmd)
    


    #get
    def ngw2png(where,ngwstyles,size,filename):

        cur.execute('''
    SELECT 
    CONCAT(
    ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),',',
    ST_YMin(Box2D(ST_Transform(wkb_geometry,3857))),',',
    ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),',',
    ST_YMax(Box2D(ST_Transform(wkb_geometry,3857)))
    ) AS bbox_string_ngw_image
    ,
    (
    ST_YMax(ST_Transform(wkb_geometry,3857)) - ST_YMin(ST_Transform(wkb_geometry,3857))
    )/
    (
    ST_XMax(ST_Transform(wkb_geometry,3857)) - ST_XMin(ST_Transform(wkb_geometry,3857))
    )::real AS aspect,

    ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))) AS xmin,
    ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))) AS ymax,
    ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))) AS xmax,
    ST_YMin(Box2D(ST_Transform(wkb_geometry,3857))) AS ymin,
    ref,
    map
    FROM atlaspages
    WHERE '''+where+'''
    ORDER BY map,ref;
                    ''')
        rows = cur.fetchall()
        size
        for currentmap in rows:
            url="http://trolleway.nextgis.com/api/component/render/image?resource="+ngwstyles+"&extent="+str(currentmap[0])+"&size="+str(size)+","+str(int(round(size*float(currentmap[1]))))
            if retrive_map:
                response = urllib2.urlopen(url)
                image=open(filename+'.png','w')
                image.write(response.read())
                image.close()
            worldfile=open(filename+'.pngw','w')
            worldfile.write(str((currentmap[4]-currentmap[2])/size)+"\n")
            worldfile.write('0'+"\n")
            worldfile.write('0'+"\n")
            worldfile.write('-'+str((currentmap[3]-currentmap[5])/int(round(size*float(currentmap[1]))))+"\n")
            worldfile.write(str(currentmap[2])+"\n")
            worldfile.write(str(currentmap[3])+"\n")
            worldfile.close()


        return

    #used for convert to atlas 
    ngw2png(where="map='mostrans-trolleybus-atlas4' AND ref='all'",
        ngwstyles='759,758,760,753,715,725',
        size=size_main,
        filename=os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-all-atlas")
    )      

    

    #used for convert to atlas 
    ngw2png(where="map='mostrans-trolleybus-atlas4' AND ref='center'",
        ngwstyles='759,758,760,753,715,725',
        size=1500,
        filename=os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-center")
    )    




#Согласно принципу KISS: генерируются одиночные pdf в gdal, затем они склеиваются в один посредством imagemagick
    atlaspages=list()
    cur.execute('''
SELECT 
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdaltranslate,
ref,map
FROM atlaspages
WHERE map='mostrans-trolleybus-atlas4' AND ref<>'all' AND ref<>'center'
ORDER BY map,ref;
                ''')
    rows = cur.fetchall()
    for currentmap in rows:
            page_filename=os.path.join(tmpfiles['folder'], currentmap[1]+'-'+currentmap[2])+".png"
            if os.path.exists(page_filename):
                os.remove(page_filename)
            cmd="gdal_translate -of ""PNG""  -a_srs ""EPSG:3857"" -co ""COMPRESS=JPEG"" -co ""JPEG_QUALITY=76""  -projwin "+currentmap[0]+" "+os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-all-atlas") +".png "+page_filename
            os.system(cmd)
            atlaspages.append(page_filename)


        #Врезка center

    cur.execute('''
SELECT 
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdaltranslate,
ref,map
FROM atlaspages
WHERE map='mostrans-trolleybus-atlas4' AND ref<>'all' AND ref='center'
ORDER BY map,ref;
                ''')
    rows = cur.fetchall()
    for currentmap in rows:
        page_filename=os.path.join(tmpfiles['folder'], currentmap[1]+'-'+currentmap[2])+".png"
        cmd="gdal_translate -of ""PNG""  -a_srs ""EPSG:3857""  -projwin "+currentmap[0]+" "+os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-center") +".png "+page_filename
        os.system(cmd)
        atlaspages.append(page_filename)


    cmd="convert "+' '.join(atlaspages)+' "'+tmpfiles['atlas']+'"'
    print cmd
    os.system(cmd) 
    for page_filename in atlaspages:
        os.remove(page_filename)





    ngw2png(where="map='mostrans-trolleybus-atlas4' AND ref='all'",
        ngwstyles='749,755,751,753,715,725',
        size=size_main,
        filename=os.path.join(tmpfiles['folder'], "mostrans-trolleybus-atlas4-all-screen")
    )
      
    #add overlay logo, and keep same filename
    cmd='composite branding/logo.svg '+tmpfiles['screenall']+'.png'+' -gravity NorthWest '+tmpfiles['screenall']+'_logo.png'
    #print command
    os.system(cmd)
    os.rename(tmpfiles['screenall']+'_logo.png',tmpfiles['screenall']+'.png')

    cmd="gdal_translate -of ""GTiff""  -a_srs ""EPSG:3857"" -co ""COMPRESS=JPEG"" -co ""JPEG_QUALITY=96""   "+tmpfiles['screenall'] +".png "+tmpfiles['screenall']+'.tiff'
    os.system(cmd)

    print 'Upload GeoTIF to Yandex'
    upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path+'Москва, атлас троллейбусных маршрутов [Openstreetmap] [latest].tif',overwrite='True'),filedata=open(tmpfiles['screenall']+'.tiff'), 'rb'))
    upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path+tmpfiles['atlas_yandex']+'.tif',overwrite='True'),filedata=open(tmpfiles['screenall']+'.tiff'), 'rb'))





    print 'Upload PDF to Yandex'
    method_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
    data = dict(path=config.yandex_disk_path+'Москва, атлас троллейбусных маршрутов [Openstreetmap] [latest].pdf',overwrite='True')
    response = requests.get(method_url, data,headers={'Authorization': 'OAuth '+config.yandex_token}, timeout=20)
    result = json.loads(response.text)
    upload_url = result['href']

    response = requests.put(upload_url, data=open(tmpfiles['atlas'], 'rb'),headers={'Authorization': 'OAuth '+config.yandex_token}, timeout=120)
    if response.status_code <> 201:
        print 'Error upload file to Yandex'

    method_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
    data = dict(path=config.yandex_disk_path+tmpfiles['atlas_yandex']+'.pdf',overwrite='True')
    response = requests.get(method_url, data,headers={'Authorization': 'OAuth '+config.yandex_token}, timeout=20)
    result = json.loads(response.text)
    upload_url = result['href']

    response = requests.put(upload_url, data=open(tmpfiles['atlas'], 'rb'),headers={'Authorization': 'OAuth '+config.yandex_token}, timeout=120)
    if response.status_code <> 201:
        print 'Error upload file to Yandex'

    '''
toilet -f bigmono12 --width 250 -k -F border  --export tga "Атлас Московского троллейбуса" > title.tga
        '''


        
            



if __name__ == '__main__':


        host=config.host
        dbname=config.dbname
        user=config.user
        password=config.password

        parser = argparser_prepare()
        args = parser.parse_args()
        
        import time
        now = time.strftime("%c")
        print ("Current time %s"  % now )
        
        render_atlas(host,dbname,user,password)
        #import geojson to postgis in 3857
        #generate png for all pages
        #montage pages
        #overlay texts
        #convert to pdf
        #save
