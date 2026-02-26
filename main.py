import requests
import base64
import time

def universal_mirror_factory():
    # 2026 顶级生存率源：只留最硬的，不注水
    sources = [
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt",
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
        "https://raw.githubusercontent.com/Pawpieee/Free-Nodes/main/node.txt"
    ]
    
    nodes_list = []
    print("🚀 正在执行第 50 次迭代优化：深度抓取中...")

    for url in sources:
        try:
            # 加入随机时间戳防止 GitHub 缓存死节点
            r = requests.get(f"{url}?t={int(time.time())}", timeout=20)
            if r.status_code == 200:
                raw_text = r.text
                # 自动识别 Base64 并解码
                if "://" not in raw_text[:50]:
                    try:
                        raw_text = base64.b64decode(raw_text).decode('utf-8', errors='ignore')
                    except: pass
                
                # 提取并初步去重
                lines = [l.strip() for l in raw_text.splitlines() if "://" in l and len(l) > 20]
                nodes_list.extend(lines)
                print(f"✅ 源 {url} 抓取成功，贡献 {len(lines)} 个节点")
        except:
            continue

    # 深度排重
    final_nodes = list(set(nodes_list))
    
    # 强制生成 Base64 结果
    content = "\n".join(final_nodes)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(encoded)
    
    print(f"🏁 第 50 代脚本运行完毕！共保存 {len(final_nodes)} 个活跃节点。")

if __name__ == "__main__":
    universal_mirror_factory()
