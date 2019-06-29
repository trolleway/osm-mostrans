#!/usr/bin/env python
# -*- coding: utf-8 -*-

#interface for osmconvert+osmfilter

def get_args():
    p = argparse.ArgumentParser(description='Filter pbf file using osmfilter')
    p.add_argument('--filter', help='filter string', type=str)
    p.add_argument('--debug', '-d', help='debug mode', action='store_true')
    p.add_argument('source', help='source pbf file')
    p.add_argument('result', help='result pbf file')
    return p.parse_args()


def process(filter, source_filename, result_filename, debug=false):
        filename = 'a.pbf'
        print 'pbf to o5m'
        cmd='osmconvert {filename}.osm.pbf -o={filename}.o5m'.format(filename=filename)
        if debug:
            print cmd        
        os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep="{fl}"   --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=filter)
        if debug:
            print cmd        
        os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        if debug:
            print cmd        
        os.system(cmd)

args = get_args()
process(filter=args.filter, source_filename = args.source, result_filename = args.result)        
