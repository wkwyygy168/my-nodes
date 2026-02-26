import requests
import base64
import time

def universal_mirror_factory():
    # 只选 3 个目前公认最稳、更新最快的源
    sources = [
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt",
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml"
    ]
    
    all_nodes = []
    print("🚀 开始紧急抓取...")

    for url in sources:
        try:
            # 加上时间戳，强制 GitHub 给我们最新数据
            res = requests.get(f"{url}?t={int(time.time())}", timeout=15)
            if res.status_code == 200:
                content = res.text
                # 如果是 Base64 格式，先解码
                if "://" not in content[:50]:
                    try:
                        content = base64.b64decode(content).decode('utf-8', errors='ignore')
                    except:
                        pass
                
                # 提取包含 :// 的行
                for line in content.splitlines():
                    if "://" in line and len(line) > 20:
                        all_nodes.append(line.strip())
                print(f"✅ 成功从 {url} 提取节点")
        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")

    # 去重
    unique_nodes = list(set(all_nodes))
    
    # 转换为 Base64 格式输出
    final_content = "\n".join(unique_nodes)
    encoded_output = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')

    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(encoded_output)
    
    print(f"✨ 任务完成！共计获得 {len(unique_nodes)} 个节点并存入 nodes.txt")

if __name__ == "__main__":
    universal_mirror_factory()
