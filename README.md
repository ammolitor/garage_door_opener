# garage_door_opener
simple Flask app to host a garage door button

### Basic Pi Setup
```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python-pip
```

### Put project files in place
```
sudo mkdir -p /opt/src
sudo chown -R pi:pi /opt/src
git clone https://github.com/ammolitor/garage_door_opener.git
sudo pip install -r /opt/src/garage_door_opener/requirements.txt
```

### Install and enable the service
```
sudo ln -s /opt/src/garage_door_opener/garage_door_opener.service /etc/systemd/system/garage_door_opener.service
sudo systemctl enable garage_door_opener.service
sudo systemctl start garage_door_opener.service
```
