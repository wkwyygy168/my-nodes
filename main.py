import requests
import base64
import yaml
import re

def universal_mirror_factory():
    # 你的核心源列表
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
    seen_fingerprints = set()

    for url in sources:
        try:
            print(f"🚀 正在抓取: {url}")
            res = requests.get(url, timeout=15)
            content = res.text
            
            # 判断是 YAML 还是 TXT
            if url.endswith(".yaml") or "clash" in url:
                try:
                    data = yaml.safe_load(content)
                    if data and 'proxies' in data:
                        for node in data['proxies']:
                            fp = f"{node.get('server')}:{node.get('port')}"
                            if fp not in seen_fingerprints:
                                seen_fingerprints.add(fp)
                                yaml_nodes.append(node)
                except:
                    # 如果 YAML 抓取失败（可能是 base64），尝试作为文本处理
                    print(f"⚠️ {url} 格式异常，尝试按文本提取...")
                    pass 

            # 统一按文本逻辑再扫一遍（防止 YAML 里藏着节点链接）
            try:
                # Base64 自动补齐并解码
                if "://" not in content[:50]:
                    missing_padding = len(content) % 4
                    if missing_padding: content += '=' * (4 - missing_padding)
                    raw_links = base64.b64decode(content).decode('utf-8', errors='ignore')
                else:
                    raw_links = content
                
                for line in raw_links.splitlines():
                    if "://" in line:
                        match = re.search(r'@?([^:/]+):(\d+)', line)
                        fp = match.group(0) if match else line
                        if fp not in seen_fingerprints:
                            seen_fingerprints.add(fp)
                            txt_nodes.append(line)
            except: pass

        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")

    # --- 输出文件（强制生成） ---
    # 1. 保存为 Clash 格式
    with open("nodes.yaml", "w", encoding="utf-8") as f:
        # 即使为空也输出标准结构，防止 GitHub 报错
        yaml.dump({"proxies": yaml_nodes if yaml_nodes else []}, f, allow_unicode=True)
    
    # 2. 保存为 TXT 格式
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_nodes))
        
    print(f"✨ 提纯完成！TXT节点: {len(txt_nodes)}, YAML节点: {len(yaml_nodes)}")

if __name__ == "__main__":
    universal_mirror_factory()
