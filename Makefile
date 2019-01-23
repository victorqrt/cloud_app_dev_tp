all: env
	chmod +x run

env:
	virtualenv -p python3 env
	. env/bin/activate && pip install flask pymongo dnspython

clean:
	rm -fr env app/__pycache__ app/*.pyc *.csv
	chmod -x run
