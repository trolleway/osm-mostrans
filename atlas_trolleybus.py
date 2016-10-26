#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse


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
        
       
        #import cfg.geojson to postgis in 3857
        #generate png for all pages
        #montage pages
        #overlay texts
        #convert to pdf
        #save
