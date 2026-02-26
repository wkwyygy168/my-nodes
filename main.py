import requests
import base64
import yaml
import re
import time

def universal_mirror_factory():
    # 2026 亲测高存活率源列表
    sources = [
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt",
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
        "https://raw.githubusercontent.com/free18/v2ray/main/v.txt",
        "https://raw.githubusercontent.com/mianfeifq/share/main/data2025.txt",
        "https://raw.githubusercontent.com/Pawpieee/Free-Nodes/main/node.txt",
        "https://fastly.jsdelivr.net/gh/v820965095/E-V2ray-Singbox-Clash@main/V2ray_all",
        "https://raw.githubusercontent.com/openitlib/no-more-free-proxies/main/data.txt"
    ]
    
    yaml_nodes = []
    txt_nodes = []
    seen_fingerprints = set()

    print(f"🚀 正在从高活跃源提纯节点...")
    for url in sources:
        try:
            res = requests.get(f"{url}?t={int(time.time())}", timeout=10)
            content = res.text
            
            if "yaml" in url or "clash" in url:
                data = yaml.safe_load(content)
                if data and 'proxies' in data:
                    for node in data['proxies']:
                        # 检查是否有必要字段，排除残缺节点
                        if node.get('server') and node.get('port'):
                            fp = f"{node.get('server')}:{node.get('port')}"
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                yaml_nodes.append(node)
            else:
                # 智能识别 Base64 或明文
                if "://" not in content:
                    try:
                        missing_padding = len(content) % 4
                        if missing_padding: content += '=' * (4 - missing_padding)
                        raw_links = base64.b64decode(content).decode('utf-8', errors='ignore')
                    except: raw_links = content
                else:
                    raw_links = content
                
                for line in raw_links.splitlines():
                    line = line.strip()
                    if "://" in line:
                        match = re.search(r'(?:@|//)([^/?#:]+):(\d+)', line)
                        fp = match.group(0) if match else line
                        if fp not in seen_fingerprints:
                            seen_fingerprints.add(fp)
                            txt_nodes.append(line)
        except: continue

    # 导出
    full_txt = "\n".join(txt_nodes)
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(full_txt.encode('utf-8')).decode('utf-8'))
    
    with open("nodes.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": yaml_nodes}, f, allow_unicode=True)
        
    print(f"✨ 提纯完成！唯一节点: {len(seen_fingerprints)} 个。")

if __name__ == "__main__":
    universal_mirror_factory()
