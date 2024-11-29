# aikit


# 使用默认端口(5012)安装
sudo ./setup_service.sh install

# 指定端口安装
sudo ./setup_service.sh install -p 5000
# 或
sudo ./setup_service.sh install --port 5000

# 卸载服务
sudo ./setup_service.sh uninstall

# 查看服务状态
./setup_service.sh status