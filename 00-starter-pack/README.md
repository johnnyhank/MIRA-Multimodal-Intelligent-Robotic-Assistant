# 香橙派启动自动播报IP地址

本部分用于设置香橙派启动自动播报IP地址的功能，仅限于教师和助教操作。

### 使用方式

请首先使用`pwd`指令查看本repo的路径是否为`/home/HwHiAiUser/OrangePi-SIC/00-starter_pack`

```bash
# 设置学创WiFi、配置自动登录、配置关闭休眠
bash set_network.sh

# 退出终端，再次打开终端
pip install pygame playsound

# 配置自动启动服务
bash install_speak_ip.sh
```

在配置完毕后，也不要随意改动本repo的位置。