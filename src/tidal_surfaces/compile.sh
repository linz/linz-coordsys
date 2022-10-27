#!/bin/bash

surfaces="HAT LAT MHW MLW  MHWS10 MLWS10"
version=20221025
sourcedir=JLAS_xyz_${version}


for surface in $surfaces; do
    lsurface=${surface,,}
    gridtool read csv ${sourcedir}/${surface}_Grid.xyz write_linzgrid NZGD2000 "Tidal service: ${surface} ${version} (TEST ONLY)" "Reference surface: NZVD2016" "Compiled: 2022-10-25"  resolution 0.0000001 nz_tidal_surface_${lsurface}_${version}.asc
    perl -MLINZ::Geodetic::Util::GridFile -e LINZ::Geodetic::Util::GridFile::Convert nz_tidal_surface_${lsurface}_${version}.asc nz_tidal_surface_${lsurface}_${version}.grd format=GRID2L
done
