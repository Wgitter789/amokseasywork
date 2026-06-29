import json

with open('南校地图.pos', 'r', encoding='utf-8') as f:
    data = json.load(f)

elements = data['diagram']['elements']['elements']

# 查找所有文本元素（可能是地点名称标签）
text_elements = []
for key, value in elements.items():
    if 'text' in value and value.get('name') != 'linker':
        x = value.get('x', 0)
        y = value.get('y', 0)
        text = value.get('text', '')
        if text and (x != 0 or y != 0):
            text_elements.append({
                'key': key,
                'text': text,
                'x': x,
                'y': y
            })

print("文本标签（可能是地点名称）：")
print("=" * 60)
for t in sorted(text_elements, key=lambda x: (x['y'], x['x'])):
    print(f"{t['text']}: ({t['x']:.1f}, {t['y']:.1f})")

print(f"\n共找到 {len(text_elements)} 个文本标签")

# 查找圆形节点及其位置
round_nodes = []
for key, value in elements.items():
    if value.get('name') == 'round':
        # 查找位置
        x, y = 0, 0
        if 'x' in value and 'y' in value:
            x, y = value['x'], value['y']
        elif 'path' in value and isinstance(value['path'], list) and len(value['path']) >= 2:
            x, y = value['path'][0], value['path'][1]
        
        # 检查是否有子节点（可能包含文本标签）
        children = value.get('children', [])
        round_nodes.append({
            'key': key,
            'x': x,
            'y': y,
            'children': children,
            'title': value.get('title', '')
        })

print("\n圆形节点位置：")
print("=" * 60)
for r in sorted(round_nodes, key=lambda x: (x['y'], x['x'])):
    print(f"节点 {r['key']}: ({r['x']:.1f}, {r['y']:.1f}) 子节点:{r['children']}")

print(f"\n共找到 {len(round_nodes)} 个圆形节点")

# 从linker提取所有节点位置
node_positions = {}
for key, value in elements.items():
    if value.get('name') == 'linker':
        if 'from' in value:
            f = value['from']
            if 'x' in f and 'y' in f and 'id' in f:
                if f['id'] not in node_positions:
                    node_positions[f['id']] = {'x': f['x'], 'y': f['y'], 'refs': []}
                node_positions[f['id']]['refs'].append(('from', key))
        if 'to' in value:
            t = value['to']
            if 'x' in t and 'y' in t and 'id' in t:
                if t['id'] not in node_positions:
                    node_positions[t['id']] = {'x': t['x'], 'y': t['y'], 'refs': []}
                node_positions[t['id']]['refs'].append(('to', key))

print("\n从linker提取的节点：")
print("=" * 60)
for nid, pos in sorted(node_positions.items(), key=lambda x: (x[1]['y'], x[1]['x'])):
    print(f"{nid}: ({pos['x']:.1f}, {pos['y']:.1f})")

print(f"\n共找到 {len(node_positions)} 个节点")
