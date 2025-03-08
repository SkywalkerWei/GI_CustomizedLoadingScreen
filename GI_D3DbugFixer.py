import os
import sys
import re
import subprocess

def validate_input(user_input):
    if not user_input.endswith('.exe'):
        return False, "无法定位游戏位置，路径需要包含.exe"
    if re.search(r'[<>"|?*]', user_input):
        return False, "包含非法字符"
    return True, "正在修复..."

def main():
    print("输入完整路径，从盘符到游戏exe：")
    user_input = input().strip()
    is_valid, message = validate_input(user_input)
    if not is_valid:
        print(f"错误: {message}")
        print("按任意键关闭...")
        input()
        sys.exit(1)
    
    cmd_filename = "FixedLauncher.cmd"
    with open(cmd_filename, "w") as cmd_file:
        cmd_file.write(f'"{user_input}" -platform_type CLOUD_THIRD_PARTY_PC')
    print(f"修复插件已创建: {cmd_filename}")
    print("右键以管理员权限运行，会自动启动原神，等待直到可以开门进入后关闭修复插件即可。")
    print("按任意键关闭...")
    input()

if __name__ == "__main__":
    main()