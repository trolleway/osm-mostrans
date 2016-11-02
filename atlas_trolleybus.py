#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse
import urllib

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

def render_atlas(host,dbname,user,password):
    ConnectionString="dbname=" + dbname + " user="+ user + " host=" + host + " password=" + password
    try:
        conn = psycopg2.connect(ConnectionString)
    except:
        print 'I am unable to connect to the database                  ' 
        print ConnectionString
        return 0
    cur = conn.cursor()




    #Получаем одну картинку со всеми слоями на всю карту

    #Генерируем к этой картинке файл привязки
    #Запрашиваем охваты отдельных страниц атласа
    #Режем картинку на страницы по географическим координатам в EPSG:3857 используя gdal
    #Собираем из страниц книжку

    
    tmpfiles=dict()
    tmpfiles['lines'] = 'tmp/lines.png'
    tmpfiles['lines_worldfile'] = 'tmp/lines.pngw'
    tmpfiles['folder'] = 'tmp'
    tmpfiles['terminals'] = 'tmp/terminals.png'

    tmpfiles['stage1'] = 'tmp/stage1.tif'
    tmpfiles['background'] = 'tmp/background.png'

    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    #Query for active maps
    
    #Запрашиваем охват листа с названием all
    cmd='''
ogr2ogr -f PostgreSQL "PG:host='''+host+''' dbname='''+dbname+''' user='''+user+''' password='''+password+'''" cfg/atlaspages.geojson -nln atlaspages -progress -overwrite    \

    '''
    
    os.system(cmd)
    cur.execute('''
SELECT 
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdal
,
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
WHERE map='mostrans-frequent-atlas4' AND ref='all'
ORDER BY map,ref;
                ''')
    rows = cur.fetchall()
    for currentmap in rows:
        

        size=7500

        url="http://trolleway.nextgis.com/api/component/render/image?resource=715,725&extent="+str(currentmap[1])+"&size="+str(size)+","+str(int(round(size*float(currentmap[2]))))
        #print url
        #urllib.urlretrieve (url, tmpfiles['lines'])

        worldfile=open(tmpfiles['lines_worldfile'],'w')
        worldfile.write(str((currentmap[5]-currentmap[3])/size)+"\n")
        worldfile.write('0'+"\n")
        worldfile.write('0'+"\n")
        worldfile.write('-'+str((currentmap[4]-currentmap[6])/int(round(size*float(currentmap[2]))))+"\n")
        worldfile.write(str(currentmap[3])+"\n")
        worldfile.write(str(currentmap[4])+"\n")
        worldfile.close()


        cur.execute('''
SELECT 
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMax(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdalwarp,

ref,map
FROM atlaspages
WHERE map='mostrans-frequent-atlas4' AND ref<>'all'
ORDER BY map,ref;
                ''')
        rows = cur.fetchall()
        for currentmap in rows:
            print currentmap

            #Согласно принципу KISS: генерируются одиночные pdf в gdal, затем они склеиваются в один посредством pdfjoin

            cmd="gdalwarp -of ""PDF"" -overwrite -t_srs ""EPSG:3857"" -co ""COMPRESS=JPEG"" -co ""JPEG_QUALITY=76"" -te "+currentmap[0]+" "+tmpfiles['lines'] +" "+os.path.join(tmpfiles['folder'], currentmap[1]+'-'+currentmap[2])+".pdf"
            print cmd
            os.system(cmd)

        continue

        
            
        #stage1 - simple png picture

        gdalcmd='gdal_translate -of "GTiff" -a_nodata 0 -co ALPHA=YES -outsize '+currentmap['size_px']+' -r lanczos -projwin  '+currentmap['bbox_string_gdal']+'   gdal_wms/wmsosmot.xml '+tmpfiles['stage1']
        print gdalcmd
        os.system( gdalcmd)      

        gdalcmd='gdal_translate -of "PNG" -outsize '+currentmap['size_px']+' -r lanczos -projwin  '+currentmap['bbox_string_gdal']+'   gdal_wms/wmsosm.xml '+tmpfiles['background']
        print gdalcmd
        os.system( gdalcmd)   
      

        import Image

        background = Image.open(tmpfiles['background'])
        overlay = Image.open(tmpfiles['stage1'])

        background = background.convert("RGBA")
        overlay = overlay.convert("RGBA")

        background.paste(overlay, (0, 0), overlay)
        #new_img = Image.blend(background, overlay, 0.5)
        background.save("stage02.png","PNG")
        
        fileDateStrinng=strftime('%Y-%m-%d %H%M%S', gmtime())
        os.rename("stage02.png",os.path.join('output',currentmap['map_id']+' MAP '+fileDateStrinng+'.png'))


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
