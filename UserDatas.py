script_mysql = '''#!/bin/bash
sudo apt update
sudo apt install mysql-server -y
sudo mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'cloud';CREATE USER 'root'@'%' IDENTIFIED BY 'cloud';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';FLUSH PRIVILEGES;CREATE DATABASE tasks;"
sudo sed -i 's/bind-address/#banana/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i 's/mysqlx/#banana/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo ufw allow 3306/tcp
sudo systemctl restart mysql
'''

script_django_mysql = f"""#!/bin/bash
cd /home/ubuntu
sudo apt update
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential -y
git clone https://github.com/raulikeda/tasks.git
cd tasks
sudo sed -i 's/node1/{public_ip_ohio}/g' portfolio/settings.py
sudo sed -i 's/django.db.backends.postgresql/django.db.backends.mysql/g' portfolio/settings.py
sudo sed -i 's/5432/3306/g' portfolio/settings.py
sudo sed -i "s/'USER': 'cloud'/'USER': 'root'/g" portfolio/settings.py
echo "mysqlclient" >> requirements.txt
./install.sh
sudo reboot 
"""