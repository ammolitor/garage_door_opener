# garage_door_opener
simple api for a garage door

### Basic Pi Setup
```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python3-pip
```

### Put project files in place
```
sudo mkdir -p /opt/src
sudo chown -R pi:pi /opt/src
git clone https://github.com/ammolitor/garage_door_opener.git
```

### Install project requirements
NOTE: this must be run with sudo (or as `root`) for the systemd service to run
```
sudo pip3 install -r /opt/src/garage_door_opener/requirements.txt
```

### Install and enable the api service
```
sudo ln -s /opt/src/garage_door_opener/door_api.service /etc/systemd/system/door_api.service
sudo systemctl enable door_api.service
sudo systemctl start door_api.service
```

### Install and enable the monitor service
```
sudo ln -s /opt/src/garage_door_opener/door_monitor.service /etc/systemd/system/door_monitor.service
sudo systemctl enable door_monitor.service
sudo systemctl start door_monitor.service
```
