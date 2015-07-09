all:
	rm -rf ~/cloud/data/*
	python simulator.py 5

server:
	rm -rf ~/cloud/data/*
	python server.py

sserver:
	python sserver.py
	
master:
	rm -rf ~/cloud/data/master/*
	python master.py

mclient:
	python mclient.py
	
worker:
	rm -rf ~/cloud/data/*
	python worker.py

torrent:
	echo "execute torrent mission"

mapreduce:
	echo "execute mapreduce mission"

clean:
	rm -rf ~/cloud/data/*

bootstrap:
	mkdir ~/cloud/data/

spacelink:
	sudo tc qdisc add dev eth0 root netem rate 100mbit delay 1ms 100us distribution normal loss 0.3% 25%

groundlink:
	sudo tc qdisc add dev eth0 root netem rate 9600bit delay 2ms 200us distribution normal loss 0.3% 25%

resetlinks:
	sudo tc qdisc del dev eth0 root

showlinks:
	sudo tc -s qdisc ls dev eth0

install:
	echo "Install required software"
	sudo apt-get install python-twisted cython python-dev python-matplotlib python-numpy python-scipy python-pip python-yaml
	sudo pip install -U scikit-image
	cd /usr/local/lib/python2.7/dist-packages
	sudo chown -R pi:pi *
