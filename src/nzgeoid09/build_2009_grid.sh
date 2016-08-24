#!/bin/sh
gzip -d -c nzgeoid09.gdf.gz > nzgeoid09.gdf
grid_convert nzgeoid09.gdf nzgeoid09.grd
rm -rf nzgeoid09.gdf

