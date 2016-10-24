import pandas as pd
import os
import os.path
import subprocess
import re

reffile='nzgeoid2016.xyz'
srcdir='offset_csv'
tgtdir='offset_grids'

if not os.path.isdir(tgtdir):
    os.mkdir(tgtdir)

for f in sorted(os.listdir(srcdir)):
    if not f.endswith('offset.csv'):
        continue

    basename=f[:-11]
    print "Processing",basename
    metafile=os.path.join(srcdir,basename+'_metadata.txt')
    offsetgrd=os.path.join(srcdir,basename+'_offset.csv')
    tmpfile=os.path.join(tgtdir,basename.lower()+'_nzvd2016_offset_tmp.csv')
    grdfile=os.path.join(tgtdir,basename.lower()+'_nzvd2016_offset.bin')

    if not os.path.exists(metafile):
        print "Metadata file {0} is missing".format(metafile)
    metadata={}
    with open(metafile) as mf:
        for l in mf:
            m=re.match(r'^(\w+)\:\s+(.*?)\s*$',l)
            if m:
                metadata[m.group(1).lower()]=m.group(2)


    header1=metadata['name']+' height datum NZVD2016 offset grid'
    header1=header1.replace(' (NZVD2016)','')
    header2='Version '+metadata['version']
    header3='Computed on 2"x2" offset grid relative to NZVD2016'

    try:
        data=pd.read_csv(offsetgrd)
        fields=[data.columns[i] for i in (1,0,3)]
        subset=data.ix[:,[1,0,3]]
        subset.columns=['lon','lat','offset']
        subset.to_csv(tmpfile,index=False)
        subprocess.call((
            'build_linzgrid',
            '-r','0.0001',
            '-f','GRID2L',
            '-c','NZGD2000',
            '-d',header1,
            '-d',header2,
            '-d',header3,
            tmpfile,
            grdfile
        ))
        os.remove(tmpfile)
    except Exception as ex:
        print ex.message
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
