# Script to install the LINZ coordinate system definition files into a standard location
#

datadir=${DESTDIR}/usr/share/linz/coordsys

dummy: 

# Need install to depend on something for debuild

install: dummy
	mkdir -p ${datadir}
	cp -p files/* ${datadir}

uninstall:
	rm -rf ${datadir}

clean:
