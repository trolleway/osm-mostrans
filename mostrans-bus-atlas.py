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
import sys


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
            try:
                result = json.loads(response.text)
                upload_url = result['href']
            except:
                print response.text
                print str(response.status_code())
                quit()
                
            response = requests.put(upload_url, filedata,headers={'Authorization': 'OAuth '+token}, timeout=120)
            if response.status_code <> 201:
                print 'Error upload file to Yandex'
                

    
    
def render_atlas(host,dbname,user,password):

    size_main=9500
    ConnectionString="dbname=" + dbname + " user="+ user + " host=" + host + " password=" + password
    try:
        conn = psycopg2.connect(ConnectionString)
    except:
        print 'I am unable to connect to the database                  ' 
        print ConnectionString
        return 0
    cur = conn.cursor()




    def ngw2png(where,ngwstyles,size,filename):
            #if size is big, then image will be retrieved from wfs service
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
                if size > 3500:
                    #url="http://trolleway.nextgis.com/api/resource/828/wms?service=WMS&request=GetMap&layers=lines-print,terminals-print&styles=&format=image%2Fpng&transparent=false&version=1.1.1&height=6000&width=6000&srs=EPSG%3A3857&bbox=4226661.916057106,7435794.111581949,4304933.433021126,7514065.628545967"
                    url="http://trolleway.nextgis.com/api/resource/828/wms?service=WMS&request=GetMap&layers=lines-print,terminals-print&styles=&format=image%2Fpng&transparent=true&version=1.1.1&height="+str(size)+"&width="+str(int(round(size*float(currentmap[1]))))+"&srs=EPSG%3A3857&bbox="+str(currentmap[0])
                print url
                if retrive_map:
                    try:
                        response = urllib2.urlopen(url)
                    except:
                        print sys.exc_info()[0]
                        print url
                        quit()
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
        
    def wfs2png(where,size,filename,wfs_url='',wfslayers=''):

            cur.execute('''
        SELECT 
        CONCAT(
        ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),',',
        ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),',',
        ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),',',
        ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
        ) AS gdal_translate_projwin_bbox 
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
            size = 10000
            for currentmap in rows:
                wms_xml='''
    <GDAL_WMS>
     <Service name="WMS">
         <Version>1.1.1</Version>
         <ServerUrl>http://trolleway.nextgis.com/api/resource/828/wms?</ServerUrl>
         <SRS>EPSG:3857</SRS>
         <ImageFormat>image/png</ImageFormat>
         <Layers>basemap-water,basemap-landuse,basemap-roads,basemap-railways,lines-print,terminals-print</Layers>
         <Styles></Styles>
     </Service>
     <DataWindow>
       <UpperLeftX>-20037508.34</UpperLeftX>
       <UpperLeftY>20037508.34</UpperLeftY>
       <LowerRightX>20037508.34</LowerRightX>
       <LowerRightY>-20037508.34</LowerRightY>
       <SizeY>40075016</SizeY>
       <SizeX>40075016.857</SizeX>
     </DataWindow>
     <Projection>EPSG:3857</Projection>
     <BandsCount>4</BandsCount>
    </GDAL_WMS>
    '''
                xml_filename='wms.xml'
                if os.path.exists(xml_filename):
                    os.remove(xml_filename)
                text_file = open(xml_filename, "w")
                text_file.write(wms_xml) 
                text_file.close()
                cmd = 'gdal_translate -of "png" -outsize ' + str(size) + ' ' + str(size * currentmap[1]) + ' -r lanczos   "<GDAL_WMS><Service name="WMS"><Version>1.1.1</Version><ServerUrl>http://trolleway.nextgis.com/api/resource/828/wms?</ServerUrl><SRS>EPSG:3857</SRS><ImageFormat>image/png</ImageFormat><Layers>basemap-water,basemap-landuse,basemap-roads,basemap-railways,lines-print,terminals-print</Layers><Styles></Styles></Service><DataWindow><UpperLeftX>' + str(currentmap[2]) + '</UpperLeftX><UpperLeftY>' + str(currentmap[3]) + '</UpperLeftY><LowerRightX>' + str(currentmap[4]) + '</LowerRightX><LowerRightY>' + str(currentmap[5]) + '</LowerRightY><SizeY>40075016</SizeY><SizeX>40075016.857</SizeX></DataWindow><Projection>EPSG:3857</Projection><BandsCount>4</BandsCount></GDAL_WMS>" ' + filename +'.png'
                print cmd #
                os.system(cmd)
                
            
                if retrive_map:
                    try:
                        os.system(cmd)
                    except:
                        print sys.exc_info()[0]
                        print cmd
                        quit()
                worldfile=open(filename+'.pngw','w')
                worldfile.write(str((currentmap[4]-currentmap[2])/size)+"\n")
                worldfile.write('0'+"\n")
                worldfile.write('0'+"\n")
                worldfile.write('-'+str((currentmap[3]-currentmap[5])/int(round(size*float(currentmap[1]))))+"\n")
                worldfile.write(str(currentmap[2])+"\n")
                worldfile.write(str(currentmap[3])+"\n")
                worldfile.close()
            return

    #debug
    retrive_map=True

    #Получаем одну картинку со всеми слоями на всю карту
    #Генерируем к этой картинке файл привязки
    #Запрашиваем охваты отдельных страниц атласа
    #Режем картинку на страницы по географическим координатам в EPSG:3857 используя gdal
    #Собираем из страниц книжку

    now = datetime.datetime.now()

    mapname='Московский автобус'
    longname_atlas = 'Москва, атлас автобусных маршрутов'
    longname_single = 'Москва, карта автобусных маршрутов'
    tmpfiles=dict()   
    tmpfiles['folder'] = 'tmp'

    tmpfiles['screenall']=os.path.join(tmpfiles['folder'], "mostrans-bus-all-screen") #no extension
    tmpfiles['atlas'] = 'tmp/moscow_bus_ru_openstreetmap_'+now.strftime("%Y-%m-%d")+'.pdf'
    tmpfiles['atlas_yandex'] = 'archive/moscow_bus_ru_openstreetmap_'+now.strftime("%Y-%m-%d") #withouth time - only one file at day will saved

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    #Load to PostGIS config file with pages bounds
    cmd='''
ogr2ogr -f PostgreSQL "PG:host='''+host+''' dbname='''+dbname+''' user='''+user+''' password='''+password+'''" cfg/mostrans-bus-atlas.geojson -nln atlaspages  -overwrite'''
    os.system(cmd)
  

    #Согласно принципу KISS: генерируются одиночные pdf в gdal, затем они склеиваются в один посредством imagemagick
    atlaspages=list()
    cur.execute('''
SELECT 
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdaltranslate,
ref,map
FROM atlaspages
WHERE ref<>'all' AND ref<>'center'
ORDER BY map,ref;
                ''')
    rows = cur.fetchall()
    #не имплементировано для автобусной карты москвы, не выполняется
    if len(rows) > 0:
        
        #used for convert to atlas 
        ngw2png(where="map='mostrans-bus' AND ref='all'",
            ngwstyles='762,764,759,758,760,753,810,811',
            size=size_main,
            filename=os.path.join(tmpfiles['folder'], "mostrans-bus-all-atlas")
        )  
        for currentmap in rows:
            page_filename=os.path.join(tmpfiles['folder'], currentmap[1]+'-'+currentmap[2])+".png"
            if os.path.exists(page_filename):
                os.remove(page_filename)
            cmd="gdal_translate -of ""PNG""  -a_srs ""EPSG:3857""   -projwin "+currentmap[0]+" "+os.path.join(tmpfiles['folder'], "mostrans-bus-all-atlas") +".png "+page_filename
            os.system(cmd)
            atlaspages.append(page_filename)

       

        #Вставка выходных данных на первую страницу
        datestring="Дата рендеринга: " + time.strftime("%d.%m.%Y")
        cmd='convert ' + atlaspages[0] + ' branding/logo.png -geometry +0+38 -composite ' + atlaspages[0]
        os.system(cmd)
        cmd='convert ' + atlaspages[0] + ' -background white  -alpha remove  ' + atlaspages[0]
        os.system(cmd)
        cmd='convert ' + atlaspages[0] +  "  -pointsize 24 label:'" + mapname + "' -gravity NorthEast -flatten " + atlaspages[0]
        os.system(cmd)
        cmd='convert ' + atlaspages[0] + "  -background white -undercolor white -pointsize 10 -annotate +0+33 '" + datestring + "'  -flatten " + atlaspages[0]
        os.system(cmd)
        
        cmd="convert "+' '.join(atlaspages)+'  "'+tmpfiles['atlas']+'"'
        print cmd
        os.system(cmd) 
        for page_filename in atlaspages:
            os.remove(page_filename)
        #end of generate atlas
    else:
        print "Atlas generation skipped, Not found pages coordinates  with ref<>'all' AND ref<>'center' in geojson file"


    
    wfs2png(where="map='mostrans-bus' AND ref='all'",size=1000,filename=os.path.join(tmpfiles['folder'], "mostrans-bus-all-screen"),wfs_url='',wfslayers='')

    
    #add overlay logo, and keep same filename
    datestring="Дата рендеринга: " + time.strftime("%d.%m.%Y")
    cmd='convert ' + tmpfiles['screenall'] + '.png' + ' branding/logo.png -geometry +0+38 -composite ' + tmpfiles['screenall'] + '.png '
    os.system(cmd)
    cmd='convert ' + tmpfiles['screenall'] + '.png' + ' -background white  -alpha remove  ' + tmpfiles['screenall'] + '.png'
    os.system(cmd)
    cmd='convert ' + tmpfiles['screenall'] + '.png' + "  -pointsize 24 label:'" + mapname + "' -gravity NorthEast -flatten " + tmpfiles['screenall'] + '.png'
    os.system(cmd)
    cmd='convert ' + tmpfiles['screenall'] + '.png' + "  -colors 64  -background white -undercolor white -pointsize 10 -annotate +0+33 '" + datestring + "'  -flatten " + tmpfiles['screenall'] + '.png'
    os.system(cmd)

    #print 'Upload map to Yandex'
    #upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path + longname_single + ' [Openstreetmap] [latest].png',overwrite='True'),filedata=open(tmpfiles['screenall']+'.png', 'rb'))

    cmd="gdal_translate -of ""GTiff"" -a_srs ""EPSG:3857"" -co ""COMPRESS=DEFLATE"" -co ""ZLEVEL=9"" " + tmpfiles['screenall'] + ".png " + tmpfiles['screenall'] + '.tiff'

    os.system(cmd)
    print 'Upload GeoTIF to Yandex'
    upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path + longname_single + ' [Openstreetmap] [latest].tif',overwrite='True'),filedata=open(tmpfiles['screenall']+'.tiff', 'rb'))
    upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path + tmpfiles['atlas_yandex']+'.tif',overwrite='True'),filedata=open(tmpfiles['screenall']+'.tiff', 'rb'))

    #print 'Upload PDF to Yandex'
    #upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path + longname_atlas + ' [Openstreetmap] [latest].pdf',overwrite='True'),filedata=open(tmpfiles['atlas'], 'rb'))
    #upload_yandex(config.yandex_token,pathdata=dict(path=config.yandex_disk_path + tmpfiles['atlas_yandex'] + '.pdf',overwrite='True'),filedata=open(tmpfiles['atlas'], 'rb'))


    
    
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
