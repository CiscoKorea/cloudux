FROM centos:7

MAINTAINER Cisco DevOps <hyungsok@cisco.com>

RUN yum install python-devel python-pip -y
RUN pip install pyvmomi django requests mysqlclient tabulate websocket-client

git clone https://bitbucket.org/Neocyon/cloudportal /opt/cloudportal
python /opt/cloudportal/manage.py makemigrations
python /opt/cloudportal/manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('cisco', 'hyungsok@cisco.com', 'C1sco123!')" | python /opt/cloudportal/manage.py shell

# Start Services
EXPOSE 80

CMD python /opt/cloudportal/manage.py runserver 0.0.0.0:80
