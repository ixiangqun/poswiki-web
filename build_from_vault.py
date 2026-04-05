import os
import re
import shutil

VAULT_DIR = '../../wiki'
DOCS_DIR = 'docs'

def build_maps(vault_dir):
    """
    Two-pass support: dynamically collect file maps and real H1 titles for all md files first.
    """
    file_map = {}
    title_map = {}
    for root, dirs, files in os.walk(vault_dir):
        for file in files:
            if file.endswith('.md'):
                base_name = file[:-3]
                rel_path = os.path.relpath(os.path.join(root, file), vault_dir)
                file_map[base_name] = rel_path
                
                # Fetch Chinese title if exists for resolving internal ugly links
                source_file = os.path.join(root, file)
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 动态拦截：如果是案例库的代码，强制检查是否带有读书笔记基因“来源章节”
                # 如果没有，则判定为外部/非书籍案例，直接剔除出地图
                if 'cases' in root.split(os.sep) and '来源章节' not in content:
                    continue

                title = base_name
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    title = re.sub(r'\[\[.*?\|(.*?)\]\]', r'\1', title)
                    title = re.sub(r'\[\[(.*?)\]\]', r'\1', title)
                title_map[base_name] = title
                
    return file_map, title_map

def convert_obsidian_links(content, current_basename, current_file_path, vault_dir, file_map, title_map, alias_map, unique_edges):
    current_file_rel = os.path.relpath(current_file_path, vault_dir)
    current_dir_rel = os.path.dirname(current_file_rel)
    
    def replacer(match):
        inner = match.group(1)
        if '|' in inner:
            target, text = inner.split('|', 1)
        else:
            target = inner
            text = inner
            
        target_clean = target.split('#')[0]
        anchor = target.split('#')[1] if '#' in target else ''
        target_basename = os.path.basename(target_clean)
        
        if target_basename in alias_map:
            target_basename = alias_map[target_basename]
            
        if target_basename in file_map:
            target_rel_to_vault = file_map[target_basename]
            
            # Use real Chinese Title if the user didn't specify an explicit '|' display text
            if '|' not in inner and target_basename in title_map:
                text = title_map[target_basename]
                
            if current_dir_rel == '':
                final_link = target_rel_to_vault
            else:
                depth = len(current_dir_rel.split(os.sep))
                up_path = '../' * depth
                final_link = up_path + target_rel_to_vault
                final_link = final_link.replace('\\', '/')
                
            unique_edges.add((current_basename, target_basename))
        else:
            final_link = target_clean + '.md'
            
        if anchor: final_link += '#' + anchor
        return f'[{text}]({final_link})'

    pattern = r'\[\[(.*?)\]\]'
    content = re.sub(pattern, replacer, content)
    
    content = re.sub(r'\s*`/wiki/.*?/`', '', content)
    content = re.sub(r'> \*\*维护规则\*\*.*?本文件由 LLM 自动更新。.*?\n', '', content)
    content = re.sub(r'^>\s*\*\*分类\*\*：.*?\n+', '', content, flags=re.MULTILINE)
    
    return content

def generate_index_page(categories):
    total_tags = sum(len(items) for items in categories.values())

    layout = []
    layout.append("---")
    layout.append("layout: doc")
    layout.append("---")
    layout.append("")
    layout.append("<script setup>")
    layout.append("import KnowledgeGraph from './.vitepress/components/KnowledgeGraph.vue'")
    layout.append("</script>")
    layout.append("")
    layout.append("# 定位词典")
    layout.append("")
    layout.append(f"整个定位理论、实践框架、商业历史战役与阅读笔记交织成一张互相连接的知识图谱。当前收录 **{total_tags} 个核心节点**。所有概念、公司案例均能一键溯源。")
    layout.append("")
    layout.append("<ClientOnly><KnowledgeGraph /></ClientOnly>")
    layout.append("")

    sections = [
        ("概念词条", "concepts", "理解特劳特与里斯定位理论的核心基石。"),
        ("案例库", "cases", "涵盖半个世纪以来的残酷商战与定位实践。"),
        ("分析框架", "frameworks", "实用的诊断模板与竞争环境沙盘推演模型。"),
    ]

    for title, folder_key, desc in sections:
        items = categories.get(folder_key, [])
        if not items: continue
        
        layout.append('<details open class="index-section">')
        layout.append(f'  <summary><h2>{title}</h2></summary>')
        layout.append('')
        layout.append(f"> {desc}")
        layout.append('<div class="index-grid">')
        # Sort by title
        for item_base, item_title in sorted(items, key=lambda x: x[1]):
            layout.append(f'  <a class="index-tag" href="/{folder_key}/{item_base}">{item_title}</a>')
        layout.append('</div>')
        layout.append('</details>')
        layout.append("")

    notes = categories.get("notes", [])
    if notes:
        layout.append('<details open class="index-section">')
        layout.append('  <summary><h2>章节阅读笔记</h2></summary>')
        layout.append('')
        layout.append("> 对经典战略定位原著书籍的深度研读解构。")
        layout.append("")
        
        book_categories = {
            "ch": {"title": "《定位：争夺用户心智的战争》", "items": []},
            "sw": {"title": "《商战》", "items": []},
            "il": {"title": "《22条商规 (营销22条铁律)》", "items": []},
            "other": {"title": "综合 / 序言与其他", "items": []}
        }
        
        for item_base, item_title in notes:
            if item_base.startswith("ch"):
                book_categories["ch"]["items"].append((item_base, item_title))
            elif item_base.startswith("sw"):
                book_categories["sw"]["items"].append((item_base, item_title))
            elif item_base.startswith("il"):
                book_categories["il"]["items"].append((item_base, item_title))
            else:
                book_categories["other"]["items"].append((item_base, item_title))
                
        for key in ["ch", "sw", "il", "other"]:
            book_title = book_categories[key]["title"]
            book_items = book_categories[key]["items"]
            
            if not book_items: continue
            
            layout.append('<details open class="index-subsection">')
            layout.append(f'  <summary><h3>{book_title}</h3></summary>')
            layout.append('')
            layout.append('<div class="index-grid">')
            for item_base, item_title in sorted(book_items, key=lambda x: x[0]):
                layout.append(f'  <a class="index-tag" href="/notes/{item_base}">{item_title}</a>')
            layout.append('</div>')
            layout.append('</details>')
            layout.append("")
            
        layout.append('</details>')
        
    return "\n".join(layout)

def main():
    import json
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    # TWO PASS processing: 
    # Pass 1: generate mappings so all Chinese titles are known ahead of time.
    file_map, title_map = build_maps(VAULT_DIR)
    
    alias_map = {
        'ch21-成功六步曲': 'ch25-成功六步曲',
        'ch19-为天主教会定位': 'ch23-机构定位-天主教会',
        'il-ch01-领导定律': 'il-ch01-领导者定律',
        'il-ch12-重新定位战略': '重新定位战略'
    }

    categories = {
        "concepts": [],
        "cases": [],
        "frameworks": [],
        "notes": []
    }
    
    graph_nodes = {}
    unique_edges = set()

    # Pass 2: render contents
    for root, dirs, files in os.walk(VAULT_DIR):
        relative_path = os.path.relpath(root, VAULT_DIR)
        target_dir = os.path.join(DOCS_DIR, relative_path) if relative_path != '.' else DOCS_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            if file.endswith('.md'):
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 第二次遍历同样实施拦截
                if 'cases' in root.split(os.sep) and '来源章节' not in content:
                    continue

                base_name = file[:-3]
                title = title_map.get(base_name, base_name)
                
                top_level = relative_path.split(os.sep)[0]
                if top_level in categories and not base_name.startswith('_'):
                    categories[top_level].append((base_name, title))
                    if base_name not in graph_nodes:
                        graph_nodes[base_name] = {
                            "id": base_name,
                            "name": title,
                            "category": top_level
                        }

                converted_content = convert_obsidian_links(content, base_name, source_file, VAULT_DIR, file_map, title_map, alias_map, unique_edges)
                
                if file == '_index.md' and root == VAULT_DIR:
                    target_file = os.path.join(target_dir, 'internal_index.md')
                    
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
            else:
                shutil.copy2(source_file, target_file)

    index_content = generate_index_page(categories)
    with open(os.path.join(DOCS_DIR, "index.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)
        
    # Generate Force Directed Graph JSON
    nodes_list = []
    category_map = {"concepts": 0, "cases": 1, "frameworks": 2, "notes": 3}
    for k, v in graph_nodes.items():
        degree = sum(1 for (s, t) in unique_edges if s == k or t == k)
        val = 15 + min(degree * 2.5, 35) # Size ranges from 15 to 50 based on links
        nodes_list.append({
            "id": v["id"],
            "name": v["name"],
            "category": category_map.get(v["category"], 4),
            "symbolSize": val
        })
        
    links_list = [{"source": s, "target": t} for s, t in unique_edges if s in graph_nodes and t in graph_nodes]
    
    os.makedirs(os.path.join(DOCS_DIR, "public"), exist_ok=True)
    with open(os.path.join(DOCS_DIR, "public", "graph_data.json"), 'w', encoding='utf-8') as f:
        json.dump({
            "nodes": nodes_list,
            "links": links_list,
            "categories": [
                {"name": "概念"},
                {"name": "案例"},
                {"name": "框架"},
                {"name": "笔记"},
            ]
        }, f, ensure_ascii=False)
        
    print("Build complete: Removed anchor #, updated links, and generated Knowledge Graph data!")

if __name__ == '__main__':
    main()
