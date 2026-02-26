import requests
import base64
import yaml
import re
import time

def universal_mirror_factory():
    # 修正后的优质去重源列表 (2026 实时更新)
    sources = [
        # --- 基础源 ---
        "https://raw.githubusercontent.com/free18/v2ray/main/v.txt",
        "https://raw.githubusercontent.com/free18/v2ray/main/c.yaml",
        "https://raw.githubusercontent.com/zipvpn/FreeVPNNodes/main/free_v2ray_xray_nodes.txt",
        "https://raw.githubusercontent.com/zipvpn/FreeVPNNodes/main/free_clash_nodes.yaml",
        "https://raw.githubusercontent.com/Flikify/Free-Node/main/v2ray.txt",
        "https://raw.githubusercontent.com/Flikify/Free-Node/main/clash.yaml",
        
        # --- 聚合大池子 (节点量极多) ---
        "https://raw.githubusercontent.com/wzdnzd/aggregator/main/subscribe/proxy.txt",
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/mianfeifq/share/main/data2025.txt",
        
        # --- 精选/测速源 ---
        "https://raw.githubusercontent.com/yebige/FreeNode/main/node.txt",
        "https://raw.githubusercontent.com/Pawpieee/Free-Nodes/main/node.txt",
        
        # --- 高级协议源 (Hysteria2 / Reality) ---
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt"
    ]
    
    yaml_nodes = []
    txt_nodes = []
    seen_fingerprints = set() # 用于去重

    for url in sources:
        try:
            print(f"🚀 正在抓取: {url}")
            # 增加随机时间戳防止 GitHub 缓存旧内容
            fetch_url = f"{url}?t={int(time.time())}"
            res = requests.get(fetch_url, timeout=15)
            res.encoding = 'utf-8'
            content = res.text
            
            if url.endswith(".yaml") or "clash" in url:
                # --- Clash YAML 处理 & 去重 ---
                try:
                    data = yaml.safe_load(content)
                    if data and 'proxies' in data:
                        for node in data['proxies']:
                            # 指纹 = 服务器地址 + 端口
                            fp = f"{node.get('server')}:{node.get('port')}"
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                yaml_nodes.append(node)
                except: continue
            else:
                # --- TXT (Base64/明文) 处理 ---
                # 兼容性 Base64 解码
                try:
                    # 补齐 Base64 填充符
                    missing_padding = len(content) % 4
                    if missing_padding:
                        content += '=' * (4 - missing_padding)
                    decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                    raw_links = decoded if "://" in decoded else content
                except:
                    raw_links = content
                
                for line in raw_links.splitlines():
                    line = line.strip()
                    if "://" in line:
                        # 增强版正则：提取节点的核心地址和端口进行去重
                        # 逻辑：匹配 @符号后面 或 //后面的 IP/域名:端口
                        match = re.search(r'(?:@|//)([^/?#:]+):(\d+)', line)
                        if match:
                            fp = match.group(0) # 得到类似 @1.2.3.4:443 或 //my.node.com:80
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                txt_nodes.append(line)
                        else:
                            # 无法提取指纹的节点（如部分特殊 vmess），通过全文去重
                            if line not in seen_fingerprints:
                                seen_fingerprints.add(line)
                                txt_nodes.append(line)

        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")

    # --- 输出处理 ---
    # 1. 保存为 Clash 格式
    with open("nodes.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": yaml_nodes}, f, allow_unicode=True)
    
    # 2. 保存为 TXT 格式 (为了兼容性，我们将结果进行 Base64 编码)
    full_txt_content = "\n".join(txt_nodes)
    encoded_txt = base64.b64encode(full_txt_content.encode('utf-8')).decode('utf-8')
    
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(encoded_txt)
        
    print(f"✨ 处理完成！")
    print(f"📊 原始节点总数: 极多")
    print(f"🎯 去重后唯一节点: {len(seen_fingerprints)} 个")

if __name__ == "__main__":
    universal_mirror_factory()
