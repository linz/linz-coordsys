#!/bin/sh
gzip -d -c nzgeoid2016.xyz.gz > nzgeoid2016.xyz
gridtool read nzgeoid2016.xyz write_linzgrid NZGD2000 "New Zealand Geoid 2016 (NZGeoid2016)" 'Geoid values computed on 1" by 1" grid' "Computed by Land Information New Zealand" resolution 0.001 nzgeoid2016.gdf
grid_convert nzgeoid2016.gdf nzgeoid2016.grd
concord -g nzgeoid2016.grd -i nzgd2000:enh:d -o nzgd2000:eno:d -p 9 nzgeoid2016.xyz check.xyz
perl <<'EOD'
use strict;
my $min=0;
my $max=0;
my $ncheck=0;
open(my $f,'check.xyz');
while( my $l=<$f> )
{
    next if $l =~ /\*\*\*\*/;
    my($lon,$lat,$hgt)=split(' ',$l);
    $ncheck++;
    $min=$max=$hgt if $ncheck == 1;
    $min=$hgt if $hgt < $min;
    $max=$hgt if $hgt > $max;
}
print "Checked $ncheck heights: min error $min, max errro $max\n";
EOD
rm -rf nzgeoid2016.xyz
rm -rf nzgeoid2016.gdf
rm -rf check.xyz

