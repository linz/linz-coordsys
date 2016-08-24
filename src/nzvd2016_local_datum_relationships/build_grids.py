import pandas as pd
import subprocess
import os
import os.path
import re

reffile='nzgeoid2016.xyz'
srcdir='offset_csv'
geoiddir='geoid_grids'

if not os.path.isdir(geoiddir):
    os.mkdir(geoiddir)

print "Extracting the nzgd2016 geoid grid"
subprocess.call(['gzip','-d','-c','../nzgeoid2016/'+reffile+'.gz'],stdout=open(reffile,'w'))

for f in sorted(os.listdir(srcdir)):
    if not f.endswith('offset.csv'):
        continue
    basename=f[:-11]
    print "Processing",basename
    metafile=basename+'_metadata.txt'
    offsetgrd=basename+'_offset.csv'
    gdffile=basename.lower()+'_nzvd2016.gdf'
    grdfile=basename.lower()+'_nzvd2016.grd'
    if not os.path.exists(os.path.join(srcdir,metafile)):
        print "Metadata file {0} is missing".format(metafile)
    metadata={}
    with open(os.path.join(srcdir,metafile)) as mf:
        for l in mf:
            m=re.match(r'^(\w+)\:\s+(.*?)\s*$',l)
            if m:
                metadata[m.group(1).lower()]=m.group(2)
    if 'name' not in metadata or 'version' not in metadata:
        print "Metadata file {0} doesn't contain name and version".format(metafile)
        continue

    data=pd.read_csv(os.path.join(srcdir,f))
    fields=[data.columns[i] for i in (1,0,3)]
    subset=data.ix[:,[1,0,3]]
    subset.columns=['lon','lat','offset']
    subset.to_csv(offsetgrd,index=False)

    header1=metadata['name']+' NZVD2016 reference surface'
    header2='Version '+metadata['version']
    header3='Computed on 2"x2" offset grid relative to NZVD2016'

    subprocess.call([
        'gridtool',
        'read',reffile,
        'trimto','csv',offsetgrd,
        'subtract','csv',offsetgrd,
        'write_linzgrid','NZGD2000',header1,header2,header3,'resolution','0.0001',gdffile
        ])
    subprocess.call(['grid_convert',gdffile,os.path.join(geoiddir,grdfile)])
    os.remove(offsetgrd)
    os.remove(gdffile)

os.remove(reffile)
