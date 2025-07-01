#!/usr/bin/env python3
"""
覆蓋率測試運行腳本
運行測試並生成覆蓋率報告
"""

import subprocess
import sys
import os

def run_coverage():
    """運行覆蓋率測試"""
    print("正在運行覆蓋率測試...")
    
    # 運行 pytest 並生成覆蓋率報告
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=project", 
        "--cov-report=xml", 
        "--cov-report=html", 
        "--cov-report=term-missing",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd(), encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 覆蓋率測試完成！")
            print(f"覆蓋率報告已生成：")
            print(f"  - XML 報告: coverage.xml")
            print(f"  - HTML 報告: htmlcov/index.html")
            print("\n現在您可以在 VS Code 中使用 Coverage Gutters 擴展查看覆蓋率信息。")
        else:
            print("❌ 覆蓋率測試失敗！")
            print("錯誤輸出：")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 運行覆蓋率測試時發生錯誤：{e}")

if __name__ == "__main__":
    run_coverage() 