#!/usr/bin/env python
# -*- coding: utf-8 -*-

#interface for osmconvert+osmfilter

import tempfile
import os

def get_args():
    p = argparse.ArgumentParser(description='Filter pbf file using osmfilter')
    p.add_argument('--filter', help='filter string', type=str)
    p.add_argument('--debug', '-d', help='debug mode', action='store_true')
    p.add_argument('source', help='source pbf file')
    p.add_argument('result', help='result pbf file')
    return p.parse_args()


def process(filter, source_filename, result_filename, debug=false):
        o5m_unfiltered = tempfile.NamedTemporaryFile(suffix=".o5m")
        o5m_filtered = tempfile.NamedTemporaryFile(suffix=".o5m")
        o5m_unfiltered_filename = o5m_unfiltered.name
        o5m_filtered_filename = o5m_filtered.name
        print 'pbf to o5m'
        cmd='osmconvert {filename} -o={o5m_unfiltered_filename}'.format(filename=source_filename,
                                                                        o5m_unfiltered_filename=o5m_unfiltered_filename)
        if debug:
            print cmd        
        os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {o5m_unfiltered_filename} --drop-author --keep="{fl}" --out-o5m >{o5m_filtered_filename}'.format(o5m_unfiltered_filename=o5m_unfiltered_filename,
                                                                                                         fl=filter,
                                                                                                     o5m_filtered_filename = o5m_filtered_filename)
        if debug:
            print cmd        
        os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {o5m_filtered_filename} -o={result_filename}'.format(o5m_filtered_filename=o5m_filtered_filename,
                                                                             result_filename = result_filename)
        if debug:
            print cmd        
        os.system(cmd)
        
        os.remove(o5m_unfiltered_filename)
        os.remove(o5m_filtered_filename)

args = get_args()
process(filter=args.filter, source_filename = args.source, result_filename = args.result)        
