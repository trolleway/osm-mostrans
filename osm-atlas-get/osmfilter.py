
#interface for osmconvert+osmfilter

def process(filter, source_filename, result_filename):
        filename = 'a.pbf'
        print 'pbf to o5m'
        cmd='osmconvert {filename}.osm.pbf -o={filename}.o5m'.format(filename=filename)
        print cmd        
        os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep="{fl}"   --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=filter)
        print cmd        
        os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        os.system(cmd)
