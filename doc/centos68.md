# Requirements OS Package
yum install mysql-server mysql-devel mysql-lib
yum install python-devel gcc gcc-c++ make openssl-devel
yum install python-ldap openldap-devel
yum install wget

# Install python 2.7
yum install xz
yum install -y centos-release-SCL
~~yum install -y python27~~

wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tar.xz
tar Jxvf Python-2.7.9.tar.xz

# Install pip
wget https://bootstrap.pypa.io/get-pip.py
python2.7 get-pip.py


# Git Clone
git clone https://Neocyon@bitbucket.org/Neocyon/cloudportal.git

# Requirements Python package
cd cloudportal
python2.7 -m pip install -r requirements.txt

# Mysql DB create
mysql -u root -p
create database cloudportal character set utf8 collate utf8_general_ci;

# DB Connection config
vi cloudmgmt/connection.cfg

# DB migrate
python2.7 manage.py makemigrations
python2.7 manage.py migrate

# DB Insert config data
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.HOST', '198.18.133.30', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.USER', 'root', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PASS', 'C1sco12345!', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PORT', '443', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.HOST', '198.18.133.112', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.KEY', '629FB012BADE48BCA7492F0068133024', '1', 'Y');


# add superuser
python2.7 manage.py createsuperuser

# Firewall
vi /etc/sysconfig/iptables
-A INPUT -m state --state NEW -m tcp -p tcp --dport 8080 -j ACCEPT
service iptables restart

~~service iptables stop~~

# Run
python2.7 manage.py runserver 0.0.0.0:8080

# start celery for background sync
celery --workdir=/home/cisco/cloudux -A cloudmgmt worker -B -l info & 


