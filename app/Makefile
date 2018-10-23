all: env
	chmod +x run

env:
	virtualenv env
	. env/bin/activate && pip install flask pymongo dnspython

clean:
	rm -fr __pycache__
	[ -d env ] && rm -fr env
