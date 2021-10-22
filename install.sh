# 裝talib前要先裝numpy
pip install numpy==1.21.2
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
cd ..
pip install TA-Lib