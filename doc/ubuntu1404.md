# Requirements OS Package
sudo apt-get install mysql-server libmysqlclient-dev
sudo apt-get install python-pip python-dev build-essential
sudo apt-get install libsasl2-dev libldap2-dev libssl-dev
sudo apt-get install git

# Git Clone
git clone https://Neocyon@bitbucket.org/Neocyon/cloudportal.git

# Requirements Python package
cd cloudportal
sudo pip install -r requirements.txt

# Mysql DB create
mysql -u root -p
create database cloudportal

# DB Connection config
vi cloudmgmt/connection.cfg

# DB migrate
python manage.py makemigrations
python manage.py migrate

# DB Insert config data
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.HOST', '198.18.133.30', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.USER', 'root', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PASS', 'C1sco12345!', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PORT', '443', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSM.HOST', '198.18.133.90', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSM.USER', 'admin', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSM.PASS', 'C1sco12345', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSM.PORT', '443', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.HOST', '198.18.133.112', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.KEY', '629FB012BADE48BCA7492F0068133024', '1', 'Y');


# add superuser
python manage.py createsuperuser

# Run
python manage.py runserver 0.0.0.0:8080


# show reload button
Developer Tools(F12) - console
$(".header p").show()