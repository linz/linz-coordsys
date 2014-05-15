# Script to install the LINZ coordinate system definition files into a standard location
#

prefix=/usr
datadir=$(prefix)/share/linz/coordsys
profiled=/etc/profile.d
profilef=linz_coordsys.sh

all: envsh

envsh: makefile
	echo "\nCOORDSYSDEF=${datadir}/coordsys.def\nexport COORDSYSDEF\n" > ${profilef}

install: all
	mkdir -p ${DESTDIR}${datadir}
	cp files/* ${DESTDIR}${datadir}
	mkdir -p ${DESTDIR}${profiled}
	cp ${profilef} ${DESTDIR}${profiled}

uninstall:
	rm -rf ${DESTDIR}${datadir}
	rm -f ${DESTDIR}${profiled}/${profilef}

clean:
	rm -f ${profilef}
