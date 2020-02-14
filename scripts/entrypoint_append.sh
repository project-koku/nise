pip uninstall -y koku-nise
cd /var/nise;
python3 setup.py build -f
python3 setup.py install -f