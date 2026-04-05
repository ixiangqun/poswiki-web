import os
import re
import shutil

# 我们现在位于 POSWIKI-Web 目录下
VAULT_DIR = '../POSWIKI/wiki'
DOCS_DIR = 'docs'

def convert_obsidian_links(content, file_path):
    def replacer(match):
        inner = match.group(1)
        if '|' in inner:
            target, text = inner.split('|', 1)
        else:
            target = inner
            text = inner
        
        # 补充缺失的扩展名，但不去破坏锚点
        if not target.endswith('.md') and '#' not in target:
            target += '.md'
            
        return f'[{text}]({target})'

    pattern = r'\[\[(.*?)\]\]'
    return re.sub(pattern, replacer, content)

def main():
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

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
                    
                converted_content = convert_obsidian_links(content, source_file)
                
                # 修复 Obsidian 首页问题
                if file == '_index.md' and root == VAULT_DIR:
                    target_file = os.path.join(target_dir, 'index.md')
                    
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
            else:
                shutil.copy2(source_file, target_file)
                
    print("知识库内容单向抓取并转换完成！")

if __name__ == '__main__':
    main()
