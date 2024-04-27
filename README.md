#!/bin/bash
```
sudo adduser --system --quiet --shell=/bin/bash --home=/opt/flectra --gecos 'flectra' --group flectra
sudo mkdir /etc/flectra && mkdir /var/log/flectra/
sudo apt-get update && apt-get upgrade -y && apt-get install postgresql postgresql-server-dev-14 build-essential python3-pillow python3-lxml python3-dev python3-pip python3-setuptools npm nodejs git gdebi libldap2-dev libpq-dev libsasl2-dev libxml2-dev libxslt1-dev libjpeg-dev -y
sudo pip3 install --upgrade pip
sudo service postgresql restart
git clone --depth=1 --branch=3.0 https://gitlab.com/daco3/DAco.git /opt/flectra/flectra
sudo chown flectra:flectra /opt/flectra/ -R && sudo chown flectra:flectra /var/log/flectra/ -R && cd /opt/flectra/flectra && sudo pip3 install -r requirements.txt
sudo npm install -g less less-plugin-clean-css rtlcss -y
cd /tmp && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb && sudo gdebi -n wkhtmltox_0.12.6.1-3.jammy_amd64.deb && rm wkhtmltox_0.12.6.1-3.jammy_amd64.deb
sudo ln -s /usr/local/bin/wkhtmltopdf /usr/bin/ && sudo ln -s /usr/local/bin/wkhtmltoimage /usr/bin/
sudo su - postgres -c "createuser -s flectra"
sudo su - flectra -c "/opt/flectra/flectra/flectra-bin --addons-path=/opt/flectra/flectra/addons -s --stop-after-init"
sudo mv /opt/flectra/.flectrarc /etc/flectra/flectra.conf
sudo sed -i "s,^\(logfile = \).*,\1"/var/log/flectra/flectra-server.log"," /etc/flectra/flectra.conf
sudo sed -i "s,^\(logrotate = \).*,\1"True"," /etc/flectra/flectra.conf
sudo sed -i "s,^\(proxy_mode = \).*,\1"True"," /etc/flectra/flectra.conf
sudo cp /opt/flectra/flectra/debian/init /etc/init.d/flectra && chmod +x /etc/init.d/flectra
sudo ln -s /opt/flectra/flectra/flectra-bin /usr/bin/flectra
sudo update-rc.d -f flectra start 20 2 3 4 5 .
sudo service flectra restart
```

