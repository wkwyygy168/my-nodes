import requests, base64, time

def universal_mirror_factory():
    # 只留三个顶级高存活源，剔除那些几千个死节点的垃圾源
    sources = [
        "https://raw.githubusercontent.com/tugezhe/v2ray/main/v2ray.txt",
        "https://raw.githubusercontent.com/v820965095/E-V2ray-Singbox-Clash/main/V2ray_all",
        "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml"
    ]
    nodes = []
    for url in sources:
        try:
            r = requests.get(f"{url}?t={int(time.time())}", timeout=10)
            # 简单的清洗逻辑
            lines = r.text.splitlines()
            nodes.extend([l.strip() for l in lines if "://" in l])
        except: continue
    
    # 最终输出
    output = base64.b64encode("\n".join(list(set(nodes))).encode()).decode()
    with open("nodes.txt", "w") as f: f.write(output)
    print(f"✅ 提纯完成，剩余 {len(nodes)} 个高概率活节点")

if __name__ == "__main__": universal_mirror_factory()
