# Andy Sayler
# Summer 2014
# Univerity of Colorado

ECHO = @echo

PYTHON = python2
PIP = pip2

REQUIRMENTS = requirments.txt

UNITTEST_PATTERN = '*_test.py'

COGS = ./cogs

.PHONY: all reqs test clean

all:
	$(ECHO) "This is a python project; nothing to build!"

reqs: $(REQUIRMENTS)
	sudo $(PIP) install -r $(REQUIRMENTS)

test:
	$(PYTHON) -m unittest discover -v -p $(UNITTEST_PATTERN)

clean:
	$(RM) *.pyc
	$(RM) $(COGS)/*.pyc
	$(RM) *~
	$(RM) $(COGS)/*~