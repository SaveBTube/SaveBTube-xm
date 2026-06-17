#!/usr/bin/env python3
"""
Bosco Tsang CLI - 命令行工具
支持登录、下载、历史、订阅等操作
"""

import argparse
import sys
import os
import json
import requests
from datetime import datetime

API_BASE = "http://localhost:8000/api"
CONFIG_FILE = os.path.expanduser("~/.bosco_cli_config.json")

class BoscoCLI:
    def __init__(self):
        self.token = None
        self.username = None
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.token = config.get('token')
                self.username = config.get('username')
    
    def save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'token': self.token, 'username': self.username}, f)
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
    
    def login(self, username, password):
        """登录"""
        try:
            resp = requests.post(
                f"{API_BASE}/admin/login",
                json={'username': username, 'password': password}
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data['token']
                self.username = data['username']
                self.save_config()
                print(f"✅ 登录成功！欢迎 {self.username}")
                return True
            else:
                print(f"❌ 登录失败: {resp.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def logout(self):
        """登出"""
        self.token = None
        self.username = None
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        print("👋 已退出登录")
    
    def whoami(self):
        """查看当前用户"""
        if not self.token:
            print("❌ 未登录，请先使用 login 命令")
            return
        print(f"👤 当前用户: {self.username}")
    
    def download(self, url, quality='best'):
        """下载视频"""
        if not self.token:
            print("❌ 未登录，请先使用 login 命令")
            return
        
        try:
            resp = requests.post(
                f"{API_BASE}/download",
                json={'url': url, 'quality': quality},
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ 下载任务已创建！")
                print(f"   任务ID: {data.get('task_id')}")
                print(f"   平台: {data.get('platform')}")
            else:
                print(f"❌ 创建失败: {resp.json().get('detail', '未知错误')}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def list_downloads(self, status=None):
        """列出下载任务"""
        if not self.token:
            print("❌ 未登录")
            return
        
        params = {}
        if status:
            params['status'] = status
        
        try:
            resp = requests.get(
                f"{API_BASE}/downloads",
                params=params,
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                tasks = data.get('tasks', [])
                if not tasks:
                    print("📭 暂无下载任务")
                    return
                
                print(f"\n{'ID':<8} {'平台':<12} {'标题':<30} {'状态':<10} {'进度':<8} {'大小':<12}")
                print("-" * 85)
                for task in tasks[:20]:
                    title = (task.get('title', '未知') or '未知')[:28]
                    print(f"{task.get('task_id', '')[:8]:<8} {task.get('platform', '-'):<12} {title:<30} {task.get('status', '-'):<10} {task.get('progress', 0)}% {'N/A':<12}")
            else:
                print(f"❌ 请求失败: {resp.json().get('detail')}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def list_history(self, limit=20):
        """列出下载历史"""
        if not self.token:
            print("❌ 未登录")
            return
        
        try:
            resp = requests.get(
                f"{API_BASE}/history",
                params={'limit': limit},
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                history = data.get('history', [])
                if not history:
                    print("📭 暂无下载历史")
                    return
                
                print(f"\n{'平台':<12} {'标题':<30} {'状态':<10} {'时间':<20}")
                print("-" * 80)
                for item in history:
                    title = (item.get('title', '未知') or '未知')[:28]
                    time = item.get('created_at', '')[:19].replace('T', ' ')
                    print(f"{item.get('platform', '-'):<12} {title:<30} {item.get('status', '-'):<10} {time:<20}")
            else:
                print(f"❌ 请求失败")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def list_subscriptions(self):
        """列出订阅"""
        if not self.token:
            print("❌ 未登录")
            return
        
        try:
            resp = requests.get(
                f"{API_BASE}/subscriptions",
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                subs = data.get('subscriptions', [])
                if not subs:
                    print("📡 暂无订阅")
                    return
                
                print(f"\n{'频道':<20} {'平台':<12} {'状态':<10} {'已下载':<10}")
                print("-" * 60)
                for sub in subs:
                    name = (sub.get('channel_name', '未知') or '未知')[:18]
                    print(f"{name:<20} {sub.get('platform', '-'):<12} {sub.get('status', '-'):<10} {sub.get('total_downloads', 0):<10}")
            else:
                print(f"❌ 请求失败")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def monitor(self):
        """查看统计数据"""
        if not self.token:
            print("❌ 未登录")
            return
        
        try:
            resp = requests.get(
                f"{API_BASE}/statistics",
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                overview = data.get('overview', {})
                system = data.get('system', {})
                
                print("\n📊 下载统计")
                print("-" * 40)
                print(f"  总下载次数: {overview.get('total_tasks', 0)}")
                print(f"  成功: {overview.get('success_count', 0)}")
                print(f"  失败: {overview.get('fail_count', 0)}")
                print(f"  视频: {overview.get('video_count', 0)}")
                print(f"  音频: {overview.get('audio_count', 0)}")
                
                print("\n💻 系统资源")
                print("-" * 40)
                print(f"  CPU: {system.get('cpu_percent', 0)}%")
                print(f"  内存: {system.get('memory_percent', 0)}%")
                print(f"  磁盘: {system.get('disk_percent', 0)}%")
            else:
                print(f"❌ 请求失败")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def view_logs(self, date=None, level=None, limit=50):
        """查看日志"""
        if not self.token:
            print("❌ 未登录")
            return
        
        params = {'limit': limit}
        if date:
            params['date'] = date
        if level:
            params['level'] = level
        
        try:
            resp = requests.get(
                f"{API_BASE}/logs",
                params=params,
                headers=self.get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                logs = data.get('logs', [])
                if not logs:
                    print("📋 暂无日志")
                    return
                
                for log in logs:
                    print(log)
            else:
                print(f"❌ 请求失败")
        except Exception as e:
            print(f"❌ 请求失败: {e}")

def main():
    cli = BoscoCLI()
    parser = argparse.ArgumentParser(description='Bosco Tsang CLI', prog='bosco')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # login
    login_parser = subparsers.add_parser('login', help='登录')
    login_parser.add_argument('-u', '--username', required=True, help='用户名')
    login_parser.add_argument('-p', '--password', required=True, help='密码')
    
    # logout
    subparsers.add_parser('logout', help='登出')
    
    # whoami
    subparsers.add_parser('whoami', help='查看当前用户')
    
    # download
    dl_parser = subparsers.add_parser('dl', help='管理下载队列')
    dl_parser.add_argument('action', nargs='?', choices=['list'], default='list', help='操作')
    dl_parser.add_argument('--status', help='按状态筛选')
    
    # url
    url_parser = subparsers.add_parser('url', help='提交下载链接')
    url_parser.add_argument('url', help='视频链接')
    url_parser.add_argument('-q', '--quality', default='best', choices=['best', '1080p', '720p', 'audio'], help='质量')
    
    # history
    his_parser = subparsers.add_parser('his', help='管理下载历史')
    his_parser.add_argument('action', nargs='?', choices=['list'], default='list', help='操作')
    his_parser.add_argument('-n', '--limit', type=int, default=20, help='显示数量')
    
    # subscriptions
    subparsers.add_parser('sub', help='管理订阅')
    
    # monitor
    subparsers.add_parser('mon', help='查看统计')
    
    # logs
    log_parser = subparsers.add_parser('log', help='查看日志')
    log_parser.add_argument('--date', help='日期 YYYY-MM-DD')
    log_parser.add_argument('--level', choices=['INFO', 'WARNING', 'ERROR'], help='日志级别')
    log_parser.add_argument('-n', '--limit', type=int, default=50, help='显示数量')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'login':
        cli.login(args.username, args.password)
    elif args.command == 'logout':
        cli.logout()
    elif args.command == 'whoami':
        cli.whoami()
    elif args.command == 'dl':
        if args.action == 'list':
            cli.list_downloads(args.status)
    elif args.command == 'url':
        cli.download(args.url, args.quality)
    elif args.command == 'his':
        if args.action == 'list':
            cli.list_history(args.limit)
    elif args.command == 'sub':
        cli.list_subscriptions()
    elif args.command == 'mon':
        cli.monitor()
    elif args.command == 'log':
        cli.view_logs(args.date, args.level, args.limit)

if __name__ == '__main__':
    main()
