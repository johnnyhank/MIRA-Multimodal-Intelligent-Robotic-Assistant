#!/bin/bash

# 1. 连接无线网络（学创中心WiFi）
# nmcli dev wifi connect "sic-guest" password "sicguest"
sudo nmcli connection modify "sic-guest" ipv4.route-metric 50
sudo nmcli connection down "sic-guest" && sudo nmcli connection up "sic-guest"

# 2. 修改lightdm.conf文件
LIGHTDM_CONF="/etc/lightdm/lightdm.conf"
AUTOLOGIN_LINE="autologin-user=HwHiAiUser"

if [ -f "$LIGHTDM_CONF" ]; then
    # 检查是否已存在该配置
    if ! grep -q "^$AUTOLOGIN_LINE" "$LIGHTDM_CONF"; then
        echo "在$LIGHTDM_CONF中添加自动登录配置..."
        echo -e "\n$AUTOLOGIN_LINE" | sudo tee -a "$LIGHTDM_CONF" > /dev/null
    else
        echo "$LIGHTDM_CONF中已存在自动登录配置"
    fi
else
    echo "警告：$LIGHTDM_CONF文件不存在！"
fi

# 3. 修改sleep.conf文件
SLEEP_CONF="/etc/systemd/sleep.conf"
TEMP_FILE=$(mktemp)

if [ -f "$SLEEP_CONF" ]; then
    echo "修改$SLEEP_CONF中的休眠设置..."
    
    # 处理文件内容
    while IFS= read -r line; do
        case "$line" in
            "#AllowSuspend=yes")
                echo "AllowSuspend=no" >> "$TEMP_FILE"
                ;;
            "#AllowHibernation=yes")
                echo "AllowHibernation=no" >> "$TEMP_FILE"
                ;;
            "#AllowSuspendThenHibernate=yes")
                echo "AllowSuspendThenHibernate=no" >> "$TEMP_FILE"
                ;;
            *)
                echo "$line" >> "$TEMP_FILE"
                ;;
        esac
    done < "$SLEEP_CONF"
    
    # 替换原文件
    sudo mv "$TEMP_FILE" "$SLEEP_CONF"
    sudo chmod 644 "$SLEEP_CONF"
else
    echo "警告：$SLEEP_CONF文件不存在！"
    rm -f "$TEMP_FILE"
fi

# 4. 安装 pygame
pip install pygame playsound -i https://pypi.tuna.tsinghua.edu.cn/simple
