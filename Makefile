DESTDIR?=/
datadir?=$(DESTDIR)/usr/share
INSTALL=install

SOURCES=$(wildcard *.desktop.in)
TARGETS=${SOURCES:.in=}

all: $(TARGETS) icons

icons:
	for i in 128 96 72 64 48 36 32 24 22 16; do \
		convert -background none asmaa.svg -resize $${i}x$${i} asmaa-$${i}.png; \
	done
pos:
	make -C po all

install: all
	python setup.py install -O2 --root $(DESTDIR)
	$(INSTALL) -d $(datadir)/applications/
	$(INSTALL) -m 0644 asmaa.desktop $(datadir)/applications/
	$(INSTALL) -m 0644 -D asmaa.svg $(datadir)/icons/hicolor/scalable/apps/asmaa.svg;
	for i in 128 96 72 64 48 36 32 24 22 16; do \
		install -d $(datadir)/icons/hicolor/$${i}x$${i}/apps; \
		$(INSTALL) -m 0644 -D asmaa-$${i}.png $(datadir)/icons/hicolor/$${i}x$${i}/apps/asmaa.png; \
	done

%.desktop: %.desktop.in pos
	intltool-merge -d po $< $@
clean:
	rm -f $(TARGETS)
	for i in 96 72 64 48 36 32 24 22 16; do \
		rm -f asmaa-$${i}.png; \
	done

