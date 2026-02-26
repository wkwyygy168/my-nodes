import requests
import base64
import yaml
import re

def universal_mirror_factory():
    # 1. 扩充的优质源列表 (包含 2026 最新活跃源)
    sources = [
        "https://raw.githubusercontent.com/free18/v2ray/main/v.txt",
        "https://raw.githubusercontent.com/free18/v2ray/main/c.yaml",
        "https://raw.githubusercontent.com/zipvpn/FreeVPNNodes/main/free_v2ray_xray_nodes.txt",
        "https://raw.githubusercontent.com/zipvpn/FreeVPNNodes/main/free_clash_nodes.yaml",
        "https://raw.githubusercontent.com/Flikify/Free-Node/main/v2ray.txt",
        "https://raw.githubusercontent.com/Flikify/Free-Node/main/clash.yaml"
    ]
    
    yaml_nodes = []
    txt_nodes = []
    seen_fingerprints = set() # 用于去重

    for url in sources:
        try:
            print(f"🚀 正在抓取: {url}")
            res = requests.get(url, timeout=15)
            content = res.text
            
            if url.endswith(".yaml") or "clash" in url:
                # --- Clash YAML 处理 & 去重 ---
                try:
                    data = yaml.safe_load(content)
                    if data and 'proxies' in data:
                        for node in data['proxies']:
                            # 指纹 = 服务器地址 + 端口 (唯一标识)
                            fp = f"{node.get('server')}:{node.get('port')}"
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                yaml_nodes.append(node)
                except: continue
            else:
                # --- TXT (Base64/明文) 处理 & 去重 ---
                # 尝试Base64解密
                try:
                    decoded = base64.b64decode(content + "=" * (-len(content) % 4)).decode('utf-8', errors='ignore')
                    raw_links = decoded if "://" in decoded else content
                except:
                    raw_links = content
                
                for line in raw_links.splitlines():
                    if "://" in line:
                        # 简单正则提取地址端口去重 (针对 vmess/ss/ssr)
                        match = re.search(r'@?([^:/]+):(\d+)', line)
                        if match:
                            fp = match.group(0)
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                txt_nodes.append(line)
                        else:
                            txt_nodes.append(line)

        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")

    # 3. 输出文件
    # 保存为 Clash 格式
    with open("nodes.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": yaml_nodes}, f, allow_unicode=True)
    
    # 保存为 TXT 格式
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_nodes))
        
    print(f"✨ 处理完成！去重后剩余 {len(seen_fingerprints)} 个唯一节点。")

if __name__ == "__main__":
    universal_mirror_factory()
