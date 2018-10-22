all: env
	chmod +x run

env:
	virtualenv env
	. env/bin/activate && pip install flask pymongo

clean:
	[ -d env ] && rm -fr env
