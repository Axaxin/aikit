#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_NAME="aikit"
VENV_DIR="$SCRIPT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
PORT="5012"  # 默认端口

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}请使用root权限运行此脚本${NC}"
        exit 1
    fi
}

# 检查并安装python3-venv
install_python_venv() {
    if ! dpkg -l | grep -q python3-venv; then
        echo -e "${YELLOW}正在安装 python3-venv...${NC}"
        apt update
        apt install -y python3-venv
    fi
}

# 创建虚拟环境
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}正在创建虚拟环境...${NC}"
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}虚拟环境创建成功${NC}"
    else
        echo -e "${GREEN}虚拟环境已存在${NC}"
    fi

    # 激活虚拟环境并安装依赖
    source "$VENV_DIR/bin/activate"
    echo -e "${YELLOW}正在安装依赖...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
    deactivate
}

# 创建系统服务
create_service() {
    echo -e "${YELLOW}正在创建系统服务...${NC}"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=AIKit Proxy Service
After=network.target

[Service]
User=root
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/app.py --port=$PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    systemctl start $SERVICE_NAME
    echo -e "${GREEN}服务创建并启动成功${NC}"
}

# 卸载服务
uninstall_service() {
    if [ -f "$SERVICE_FILE" ]; then
        echo -e "${YELLOW}正在停止并删除服务...${NC}"
        systemctl stop $SERVICE_NAME
        systemctl disable $SERVICE_NAME
        rm "$SERVICE_FILE"
        systemctl daemon-reload
        echo -e "${GREEN}服务已成功删除${NC}"
    else
        echo -e "${YELLOW}服务文件不存在${NC}"
    fi

    # 询问是否删除虚拟环境
    read -p "是否删除虚拟环境？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "$VENV_DIR" ]; then
            rm -rf "$VENV_DIR"
            echo -e "${GREEN}虚拟环境已删除${NC}"
        fi
    fi
}

# 显示使用帮助
show_help() {
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  $0 install [-p|--port <port>]  - 安装服务 (可选指定端口，默认5012)"
    echo "  $0 uninstall                   - 卸载服务"
    echo "  $0 status                      - 查看服务状态"
    echo "  $0 help                        - 显示此帮助信息"
}

# 主逻辑
case "$1" in
    "install")
        shift  # 移除第一个参数
        # 处理可选的端口参数
        while [[ $# -gt 0 ]]; do
            case "$1" in
                -p|--port)
                    PORT="$2"
                    shift 2
                    ;;
                *)
                    echo -e "${RED}未知参数: $1${NC}"
                    show_help
                    exit 1
                    ;;
            esac
        done
        check_root
        install_python_venv
        setup_venv
        create_service
        systemctl status $SERVICE_NAME
        ;;
    "uninstall")
        check_root
        uninstall_service
        ;;
    "status")
        systemctl status $SERVICE_NAME
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac

exit 0