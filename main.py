import requests
import base64
import yaml
import re
import time
from concurrent.futures import ThreadPoolExecutor

def universal_mirror_factory():
    # 扩展后的高权重源，专挑存活率高的
    sources = [
        "https://raw.githubusercontent.com/free18/v2ray/main/v.txt",
        "https://raw.githubusercontent.com/free18/v2ray/main/c.yaml",
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt",
        "https://raw.githubusercontent.com/Pawpieee/Free-Nodes/main/node.txt",
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
        "https://raw.githubusercontent.com/mianfeifq/share/main/data2025.txt",
        "https://raw.githubusercontent.com/wzdnzd/aggregator/main/subscribe/proxy.txt"
    ]
    
    yaml_nodes = []
    txt_nodes = []
    seen_fingerprints = set()

    print(f"🚀 开始深度扫描优质节点...")
    for url in sources:
        try:
            res = requests.get(f"{url}?t={int(time.time())}", timeout=10)
            content = res.text
            
            # Clash 格式处理
            if "yaml" in url or "clash" in url:
                data = yaml.safe_load(content)
                if data and 'proxies' in data:
                    for node in data['proxies']:
                        fp = f"{node.get('server')}:{node.get('port')}"
                        if fp not in seen_fingerprints:
                            seen_fingerprints.add(fp)
                            yaml_nodes.append(node)
            # 链接格式处理
            else:
                # 尝试Base64解码
                try:
                    missing_padding = len(content) % 4
                    if missing_padding: content += '=' * (4 - missing_padding)
                    raw_links = base64.b64decode(content).decode('utf-8', errors='ignore')
                except:
                    raw_links = content
                
                for line in raw_links.splitlines():
                    line = line.strip()
                    if "://" in line:
                        # 简单的连接指纹提取用于去重
                        match = re.search(r'(?:@|//)([^/?#:]+):(\d+)', line)
                        fp = match.group(0) if match else line
                        if fp not in seen_fingerprints:
                            seen_fingerprints.add(fp)
                            txt_nodes.append(line)
        except: continue

    # 保存 TXT (Base64 加密输出，Karing 最爱)
    full_txt = "\n".join(txt_nodes)
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(full_txt.encode('utf-8')).decode('utf-8'))
    
    # 保存 YAML
    with open("nodes.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": yaml_nodes}, f, allow_unicode=True)
        
    print(f"✨ 提纯完成！共获得 {len(seen_fingerprints)} 个精选节点。")

if __name__ == "__main__":
    universal_mirror_factory()
