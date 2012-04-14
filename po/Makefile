POTFILE=$(shell cat POTFILES.in)
SOURCES=$(addprefix ../, $(POTFILE))
POFILES=$(wildcard *.po)
MOFILES=$(patsubst %.po,%.mo,$(POFILES))

all: asmaa.pot $(MOFILES)

asmaa.pot: $(SOURCES)
	intltool-update -g asmaa -p

%.mo: %.po
	msgfmt $*.po -o $*.mo
	mkdir -p ../locale/$*/LC_MESSAGES/ || :
	cp $*.mo ../locale/$*/LC_MESSAGES/asmaa.mo

%.po: asmaa.pot
	intltool-update -g asmaa -d $*

