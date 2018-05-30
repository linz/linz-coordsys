#!/bin/sh

# Echo testing coordinate systems in coordsys.def

mkdir -p out
rm -f out/*

export COORDSYSDEF='../files/coordsys.def'

echo "Testing coordsys.def"

for c in `cat crdsyslist.txt`; do
   echo "=======================" >> out/crdsys.txt
   echo "Testing ${c}" >> out/crdsys.txt
   concord -L ${c} > out/crdsys_list_${c}.txt 2>&1
   concord -INZGD2000,NEH,H -o${c} -N6 -P6 in/test1.in out/test_${c}.out >> out/crdsys.txt 2>&1
done


for c in `cat crdsyslist2.txt`; do
   echo "=======================" >> out/crdsys.txt
   echo "Testing ${c}" >> out/crdsys.txt
   concord -L ${c} > out/crdsys_list_${c}.txt 2>&1
   concord -IITRF96,NEH,H -o${c} -Y2000.5 -N6 -P6 in/test1.in out/test_${c}.out >> out/crdsys.txt 2>&1
done

echo "Testing NZGD2000 versions"
for v in `cat in/test_nzgd2000.version`; do
    echo "Testing version $v"
    echo "Testing NZGD2000 version $v" >> out/crdsys.txt 2>&1
    for y in `cat in/test_nzgd2000.year`; do
        concord -iITRF96:ENH:D -oNZGD2000_$v:ENH:D -N3 -Y$y -P9 in/test_nzgd2000.in out/testnzgd2000_${v}_${y}.out >> out/crdsys.txt 2>&1
    done
done

echo "Testing height reference surfaces"
for c in `cat hgtreflist.txt`; do
   echo "=======================" >> out/hgtref.txt
   echo "Testing ${c}" >> out/hgtref.txt
   concord -L NZGD2000/${c} > out/hgtref_list_${c}.txt 2>&1
   concord -INZGD2000/${c},ENH,D -oNZGD2000,ENH,D -P4:3 in/nzpoints.in out/testhrs_${c}.out >> out/hgtref.txt 2>&1
done

echo "Testing ITRF systems"
for c in `cat itrf_csys.txt`; do
   echo "========== ${c} ============" >> out/itrf.txt
   concord -L ${c} >> out/itrf.txt 2>&1
   echo "ITRF96 to ${c}" >> out/itrf.txt
   concord -IITRF96_XYZ -o${c}_XYZ -Y2000 -N6 -P4 in/global.xyz out/test_${c}b.out >> out/itrf.txt 2>&1
   concord -IITRF96_XYZ -o${c}_XYZ -Y2010 -N6 -P4 in/global.xyz out/test_${c}c.out >> out/itrf.txt 2>&1
   echo "NZGD2000 to ${c}" >> out/itrf.txt
   concord -INZGD2000,NE,D -o${c},NEH,D -Y2000 -N8 -P8 in/test15.in out/test_${c}d.out >> out/itrf.txt 2>&1
   concord -INZGD2000,NE,D -o${c},NEH,D -Y2010 -N8 -P8 in/test15.in out/test_${c}e.out >> out/itrf.txt 2>&1
done

# Australian coordinate systems

echo "Testing Australian systems"
for c in `cat aus_csys.txt`; do
   echo "========== ${c} ============" >> out/aus.txt
   concord -L ${c} >> out/aus.txt 2>&1
   echo "GDA94 to ${c}" >> out/aus.txt
   concord -IGDA94:NEH:D -o${c}:ENH:D -Y2000 -N8 -P8 in/aus.in out/test_${c}b.out >> out/aus.txt 2>&1
   concord -IGDA94:NEH:D -o${c}:ENH:D -Y2010 -N8 -P8 in/aus.in out/test_${c}c.out >> out/aus.txt 2>&1
done
for c in `cat aus_proj.txt`; do
   echo "========== ${c} ============" >> out/aus.txt
   concord -L ${c} >> out/aus.txt 2>&1
   echo "GDA94 to ${c}" >> out/aus.txt
   concord -IGDA94:NEH:D -o${c}:ENH -Y2000 -N8 -P4 in/aus.in out/test_${c}b.out >> out/aus.txt 2>&1
   concord -IGDA94:NEH:D -o${c}:ENH -Y2010 -N8 -P4 in/aus.in out/test_${c}c.out >> out/aus.txt 2>&1
done
for c in `cat aus_xyz.txt`; do
   echo "========== ${c} ============" >> out/aus.txt
   concord -L ${c} >> out/aus.txt 2>&1
   echo "GDA94 to ${c}" >> out/aus.txt
   concord -IGDA94:NEH:D -o${c} -Y2000 -N8 -P4 in/aus.in out/test_${c}b.out >> out/aus.txt 2>&1
   concord -IGDA94:NEH:D -o${c} -Y2010 -N8 -P4 in/aus.in out/test_${c}c.out >> out/aus.txt 2>&1
done


perl fix_output.pl out/*.*
rm -f out/*.bak

diff -r -b -B -q check out


