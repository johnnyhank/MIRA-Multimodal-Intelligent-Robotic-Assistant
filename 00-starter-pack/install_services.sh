#!/bin/bash
SCRIPT_NAME="speak_ip.py"
SCRIPT_SOURCE="$(pwd)/$SCRIPT_NAME"
PYTHON_PATH="/usr/local/miniconda3/bin/python"
SERVICE_NAME="speakip.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

echo "Start config..."

if [ ! -f "$SCRIPT_SOURCE" ]; then
  echo "Error! Can't find $SCRIPT_NAME"
  exit 1
else
  chmod +x "$SCRIPT_SOURCE"
fi

echo "Write systemd into: $SERVICE_PATH"
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Auto speak IP at boot
After=network-online.target sound.target
Wants=network-online.target

[Service]
ExecStart=$PYTHON_PATH $SCRIPT_SOURCE
Restart=on-failure
RestartSec=60
User=HwHiAiUser
WorkingDirectory=/home/HwHiAiUser/OrangePi-SIC/00-starter-pack

[Install]
WantedBy=multi-user.target
EOF

echo "Reload systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "Config Finished!"
