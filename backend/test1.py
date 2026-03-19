#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼（dashscope）SSL/API 全链路测试代码
适配你替换后的阿里云百炼调用逻辑，精准定位SSL/网络/SDK问题
"""
import sys
import ssl
import socket
import time
import json
import os

# 先禁用SSL警告，避免终端刷屏
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
requests.packages.urllib3.disable_warnings()

# ==================== 基础信息打印 ====================
print("=== 阿里云百炼（dashscope）全链路诊断报告 ===")
print(f"Python 版本: {sys.version}")
print(f"OpenSSL 版本: {ssl.OPENSSL_VERSION}")

# 检查certifi证书
try:
    import certifi
    cert_path = certifi.where()
    print(f"证书存储路径: {cert_path}")
    print(f"证书是否存在: {os.path.exists(cert_path)}")
except ImportError:
    print("⚠️ 未安装certifi库，跳过证书路径检查")
    cert_path = None
print("=" * 60)

# ==================== 配置项（请修改这里！）====================
ALIYUN_API_KEY = "sk-c2ae362125424bf2852250cf2333600d"  # 替换成你自己的API Key！
TEST_HOST = "dashscope.aliyuncs.com"     # 阿里云百炼核心域名
TEST_PORT = 443                          # HTTPS默认端口
TIMEOUT = 10                             # 超时时间（秒）

# ==================== 工具函数 ====================
def print_step(title):
    """打印测试步骤分隔符"""
    print(f"\n📌 {title}")
    print("-" * 40)

# ==================== 测试步骤 ====================

# 1. 基础Socket连接测试（验证网络连通性）
print_step("1. 测试基础Socket连接")
try:
    sock = socket.create_connection((TEST_HOST, TEST_PORT), timeout=TIMEOUT)
    print("✅ Socket连接成功")
    sock.close()
except Exception as e:
    print(f"❌ Socket连接失败: {str(e)[:100]}")

# 2. SSL握手测试（带/不带证书验证）
print_step("2. 测试SSL握手")
# 2.1 带证书验证的SSL握手
try:
    context = ssl.create_default_context()
    with socket.create_connection((TEST_HOST, TEST_PORT), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=TEST_HOST) as ssock:
            print("✅ 带证书验证的SSL握手成功")
            print(f"   协议版本: {ssock.version()}")
            print(f"   加密套件: {ssock.cipher()[0]}")
except Exception as e:
    print(f"❌ 带证书验证的SSL握手失败: {str(e)[:100]}")

# 2.2 禁用证书验证的SSL握手（关键测试）
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection((TEST_HOST, TEST_PORT), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=TEST_HOST) as ssock:
            print("✅ 禁用证书验证的SSL握手成功")
except Exception as e:
    print(f"❌ 禁用证书验证的SSL握手失败: {str(e)[:100]}")

# 3. Requests直接调用阿里云百炼API（模拟SDK底层）
print_step("3. 测试Requests直接调用阿里云百炼API")
# 阿里云百炼基础生成接口
api_url = f"https://{TEST_HOST}/api/v1/services/aigc/text-generation/generation"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ALIYUN_API_KEY}"
}
# 测试请求体（符合阿里云百炼格式）
test_data = {
    "model": "qwen-plus",
    "input": {
        "prompt": "测试阿里云百炼API，仅返回'测试成功'即可"
    },
    "parameters": {
        "temperature": 0.3,
        "max_tokens": 100,
        "top_p": 0.7
    }
}

# 3.1 默认验证证书调用
try:
    resp = requests.post(api_url, json=test_data, headers=headers, timeout=TIMEOUT)
    print(f"✅ 默认验证证书 - 状态码: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   响应内容: {json.dumps(resp.json(), ensure_ascii=False)[:200]}")
    else:
        print(f"   错误信息: {resp.text[:200]}")
except Exception as e:
    print(f"❌ 默认验证证书 - 调用失败: {str(e)[:100]}")

# 3.2 禁用证书验证调用（核心测试）
try:
    resp = requests.post(api_url, json=test_data, headers=headers, timeout=TIMEOUT, verify=False)
    print(f"✅ 禁用证书验证 - 状态码: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   响应内容: {json.dumps(resp.json(), ensure_ascii=False)[:200]}")
    else:
        print(f"   错误信息: {resp.text[:200]}")
except Exception as e:
    print(f"❌ 禁用证书验证 - 调用失败: {str(e)[:100]}")

# 4. 测试阿里云百炼官方SDK调用（最终验证你的业务代码）
print_step("4. 测试阿里云百炼SDK直接调用")
try:
    # 先强制SDK底层的requests禁用SSL验证（解决证书问题）
    import functools
    requests.post = functools.partial(requests.post, verify=False)
    requests.get = functools.partial(requests.get, verify=False)
    
    # 导入并初始化阿里云百炼SDK
    import dashscope
    dashscope.api_key = ALIYUN_API_KEY
    
    # 调用你业务代码中使用的dashscope.Generation.call方法
    response = dashscope.Generation.call(
        model='qwen-plus',
        prompt="测试阿里云百炼SDK，仅返回'SDK测试成功'即可",
        temperature=0.3,
        max_tokens=100,
        top_p=0.7,
    )
    
    if response.status_code == 200:
        print("✅ 阿里云百炼SDK调用成功！")
        print(f"   返回结果: {response.output.text}")
    else:
        print(f"❌ 阿里云百炼SDK调用失败: {response.code} - {response.message}")
except ImportError:
    print("❌ 未安装阿里云百炼SDK，请执行: pip install dashscope")
except Exception as e:
    print(f"❌ 阿里云百炼SDK调用异常: {str(e)[:200]}")

# 5. 测试你封装的_call_zhipu函数（验证业务逻辑）
print_step("5. 测试你封装的_call_zhipu函数")
try:
    # 导入你封装的函数（确保该函数在当前目录可导入）
    # 如果函数在其他文件，先添加导入：from your_file import _call_zhipu
    
    # 定义测试提示词
    test_prompt = "测试封装函数，仅返回'封装函数测试成功'即可"
    # 调用你的函数
    result = _call_zhipu(test_prompt, temperature=0.3, max_tokens=100)
    
    if result:
        print("✅ 封装函数调用成功！")
        print(f"   返回结果: {result}")
    else:
        print("❌ 封装函数调用失败，返回空字符串")
except Exception as e:
    print(f"❌ 封装函数调用异常: {str(e)[:200]}")

# ==================== 测试总结 ====================
print_step("5. 测试总结")
print("📝 关键结论:")
print("   1. 如果步骤4调用成功 → 可直接使用你的阿里云百炼业务代码")
print("   2. 如果步骤3.2成功但步骤4失败 → SDK版本/参数/SSL配置问题")
print("   3. 如果步骤3.2失败 → 网络/防火墙/API Key无效问题")
print("   4. 如果步骤5失败 → 你封装的函数逻辑需调整")
print("=" * 60)