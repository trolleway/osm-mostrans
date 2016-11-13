#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Update and crop osm dump file for Moscow Oblast
# Author: Artem Svetlov <artem.svetlov@nextgis.com>



import os

#if prevdump not exists - download CFO from geofabrik and crop to MosOblast
def updateDump():
    
    dump_url='http://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf'
    downloaded_dump='central-fed-district-latest.osm.pbf'
    work_dump='moscow_russia.osm.pbf'
    updated_dump='osm/just_updated_dump.osm.pbf'
    poly_file='cfg/mostrans.poly'

    #frist run of program
    if os.path.exists(work_dump) == False:
        os.system('wget '+dump_url)
        os.rename(downloaded_dump, work_dump) 

    #if prevdump dump exists - run osmupdate, it updating it to last hour state with MosOblast clipping, and save as currentdump
    cmd='osmupdate '+ work_dump + ' ' + updated_dump + ' --base-url=download.geofabrik.de/russia-updates  -v -B='+poly_file #--day --hour 
    print cmd
    os.system(cmd)    

    #rename currentdump to prevdump
    os.remove(work_dump)
    os.rename(updated_dump, work_dump)

    return 0

updateDump()
