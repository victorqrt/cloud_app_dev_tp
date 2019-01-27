all: env
	chmod +x run

env:
	cd app && tar xvf static.tar.gz
	virtualenv -p python3 env
	. env/bin/activate && pip install flask pymongo dnspython

clean:
	rm -fr env app/__pycache__ app/static app/*.pyc *.csv
	chmod -x run

static-archive:
	cd app && tar cvzf static.tar.gz static
