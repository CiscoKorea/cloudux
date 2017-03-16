# CloudUX

CloudUX is simplified self-service portal for SMB target customers.
Main features are below.
  - End-user self-service portal for consuming catalogs created from UCS Director.
  - Virtual machine creation, GuestOS VM action & remote console( currently only VMWare vSphere support)
  - No user registration required, only single configuration on UCS Director
  - Opensource and easy to extend functionalites & look-and-feels

# Basic Installation Guide !
CloudUX is developed for Linux environment, support two famous distributsions Ubunut/Debian and Redhat/CentOS
CloudUX has ansible playbook for installation for RHEL/CentOS & Ubuntu/Debian diestribution
Ansible 2.2+ required for installation.

You need to have a Linux or Macbook for ansible installation 

```
$ pip install ansible==2.2 --upgrade 
$ git clone https://github.com/CiscoKorea/cloudux -b selfserviceportal 
$ vi cloudux/hosts 
$ ansible-playbook -u root -K -k -i hosts setup.yml 
```

Before execute setup.yml, update hosts inventory which VM is destined for installation CloudUX and fill-out required parameters on roles/portal/var/main.yml
You need replace your vCenter environment and your UCSDirector information, just ignore UCS Manager information for self-service portal.

Here is mannual installation ( for CentOS 7.x )

```
$ yum update -y 
$ yum install mariadb mariadb-server mariadb-devel mariadb-libs python-devel gcc gcc-c++ make openssl-devel openldap-devel libselinux-python git pip-python -y
```

Update database configuration file with below examples ( on /etc/my.cnf or /etc/my.cnf.d/server.conf)

```
[mariadb-5.5] 
init_connect = "SET collation_connection = utf8_general_ci"
init_connect = "SET NAMES utf8"
character-set-server = utf8
collation-server = utf8_general_ci
```

Setup mariadb auto-start at boot 

```
$ systemctl enable mariadb && systemctl restart mariadb 
```

Create database & user for cloudux, here username portal and password 1234Qwer database name cloudportal 

```
$ mysql -u root
mysql> CREATE DATABASE cloudportal;
mysql > GRANT ALL PRIVILEGES ON cloudportal.* TO 'portal'@'localhost' IDENTIFIED BY '1234Qwer';
```

CloudUX code downloads from github repository

```
$ git clone https://github.com/CiscoKorea/cloudux -b selfserviceportal 
```

Install all required python package from requirements.txt

```
$ cd cloudux
$ sudo pip install -r requirements.txt
```

Run django framework commands  makemigrations, migrate & createsuperuser 

```
$ cd cloudux
$ python manage.py makemigrations {prepare database migration}
$ python manage.py migrate {do actual migration job} 
$ python manage.py createsuperuser {add new super user }
``` 

Upload configuration data(vCenter Info, UCSDirector Info) to Mariadb instance 

```
initial looks like this 
update variable {{xxx}} to your environments 

INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.HOST', '{{ vcenter_host}}', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.USER', '{{vcenter_user}}', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PASS', '{{vcenter_pass}}', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('VC.PORT', '{{vcenter_port}}', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.HOST', '{{ucsd_host}}', '1', 'Y');
INSERT INTO cloudportal.ux_config (`key`, val, type, is_used) VALUES ('UCSD.KEY', '{{ucsd_apikey}}', '1', 'Y');

$ mysql -u portal --password=1234Qwer cloudprtal < initial.sql 
```

Update configuration for django database connection 

```
$ cd cloudux/cloudmgmt
cat connection.cfg 

[mysql]
hostname=maridb_host_name
dbname=cloudportal
username=portal
password=1234Qwer
port=3306
```

Now it is ready to run CloudUX

```
$ cd cloudux
$ python manage.py runserver 0.0.0.0:8080 
``` 

Enjoy self-service portal wich CloudUX !
