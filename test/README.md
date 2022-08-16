Test conversion dataset
=======================

The file test_coord.csv is a set of coordinates that can be used to validate coordinate conversions.
This has the following columns:

| Field | Description |
| --- | --- |
| id | The test id |
| crdsys_in | The code for the input coordinate system |
| cstype_in | The type of the input coordinate system (P,G,X) |
| order_in |  The order of the input coordinates (ENH or XYZ)|
| crdsys_out | The code for the output coordinate system |
| cstype_out |  The type of the output coordinate system |
| order_out | The order of the output coordinates |
| epoch | The epoch for the conversion (decimal years or blank) |
| ord1_in | The first ordinate of the input coordinate |
| ord2_in | The second ordinate of the input coordinate |
| ord3_in | The third ordinate of the input coordinate |
| ord1_out | The first ordinate of the output coordinate |
| ord2_out | The second ordinate of the output coordinate |
| ord3_out | The third ordinate of the output coordinate |

Coordinate precision is approximately 0.1 mm.

The test_conversions.py python script can be used to test the online
coordinate conversion API or concord against these tests.  By default
these are testing using the coordinate system definition installed with
each software.

To test the coordinate system definition in this repositry against this
list using concord run:

``` shell
COORDSYS_DEF=../files/coordsys.def python3 test_conversions.py -c
```
