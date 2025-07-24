#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("🌐 启动Web服务...")
    print("📱 访问地址: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务")
    
    from web_app import app
    app.run(host='127.0.0.1', port=5000, debug=True)
