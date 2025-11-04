# Makefile for EJDict tools
.PHONY: build-all

build-all:
	make clean
	make build
	make makezip

build:
	php ./join-files.php
	php ./tojson.php
	php ./tosqlite.php
	echo "Build complete."

makezip:
	php ./makezip.php
	echo "make archive complete."

clean:
	php ./clean.php
	echo "Clean complete."