"""
GitHub 銝??皜??單
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_for_github():
    """皜?銝?閬??喳 GitHub ??隞?""
    
    print("?完 ??皜??辣隞交????喳 GitHub...")
    
    # 閬?斤??辣璅∪?
    files_to_remove = [
        # 皜祈岫?辣
        "test_*.py",
        "debug_*.py", 
        "*_test.py",
        "test_*.html",
        "test_*.json",
        "*_test.txt",
        
        # ???辣
        "*_response_*.html",
        "debug_full_response_*.html",
        "correct_encoding_*.html",
        "final_test_*.html",
        "ziwei_raw_response_*.html",
        "ziwei_parsed_data_*.json",
        
        # ?孵??辣
        "love_analysis_test.txt",
        "corrected_response.html",
        "debug_response.html",
        "mcp_demo_response.json",
        "working_test_result.json",
        "test_result_*.json",
        "performance_test_results_*.json",
        
        # ?寞活瑼?
        "*.bat",
    ]
    
    # 閬?斤??桅?
    dirs_to_remove = [
        "cache",
        "__pycache__",
        "src/__pycache__",
        "logs",
        "vector_db_*",
        "test_*_vector_db",
        "?券瑼???閫??",
        "??蝡臬??曄??,
    ]
    
    removed_files = 0
    removed_dirs = 0
    
    # ?芷?辣
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"  ???芷?辣: {file_path}")
                    removed_files += 1
                except Exception as e:
                    print(f"  ???⊥??芷?辣 {file_path}: {e}")
    
    # ?芷?桅?
    for pattern in dirs_to_remove:
        for dir_path in glob.glob(pattern):
            if os.path.isdir(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"  ???芷?桅?: {dir_path}")
                    removed_dirs += 1
                except Exception as e:
                    print(f"  ???⊥??芷?桅? {dir_path}: {e}")
    
    # 皜? frontend/node_modules嚗????剁?
    frontend_node_modules = "frontend/node_modules"
    if os.path.exists(frontend_node_modules):
        try:
            shutil.rmtree(frontend_node_modules)
            print(f"  ???芷?桅?: {frontend_node_modules}")
            removed_dirs += 1
        except Exception as e:
            print(f"  ???⊥??芷?桅? {frontend_node_modules}: {e}")
    
    # 皜? mcp-server/node_modules嚗????剁?
    mcp_node_modules = "mcp-server/node_modules"
    if os.path.exists(mcp_node_modules):
        try:
            shutil.rmtree(mcp_node_modules)
            print(f"  ???芷?桅?: {mcp_node_modules}")
            removed_dirs += 1
        except Exception as e:
            print(f"  ???⊥??芷?桅? {mcp_node_modules}: {e}")
    
    print(f"\n?? 皜?摰?:")
    print(f"  ?芷?辣: {removed_files} ??)
    print(f"  ?芷?桅?: {removed_dirs} ??)

def check_sensitive_files():
    """瑼Ｘ?臬????隞?""
    
    print("\n?? 瑼Ｘ???辣...")
    
    sensitive_patterns = [
        "*.env",
        "*key*",
        "*secret*", 
        "*token*",
        "*.pdf",
    ]
    
    found_sensitive = []
    
    for pattern in sensitive_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if file_path != ".env.example" and not file_path.startswith(".git"):
                found_sensitive.append(file_path)
    
    if found_sensitive:
        print("  ?? ?潛?航????隞?")
        for file_path in found_sensitive:
            print(f"    - {file_path}")
        print("  隢??炎?仿??辣?臬???靽⊥")
    else:
        print("  ???芰?暹?憿舐????辣")

def check_file_sizes():
    """瑼Ｘ憭扳?隞?""
    
    print("\n?? 瑼Ｘ憭扳?隞?(>10MB)...")
    
    large_files = []
    
    for root, dirs, files in os.walk("."):
        # 頝喲? .git ?桅?
        if ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 10 * 1024 * 1024:  # 10MB
                    large_files.append((file_path, size))
            except:
                continue
    
    if large_files:
        print("  ?? ?潛憭扳?隞?")
        for file_path, size in large_files:
            size_mb = size / (1024 * 1024)
            print(f"    - {file_path}: {size_mb:.1f}MB")
        print("  隢?臬?閬??日??辣")
    else:
        print("  ???芰?曉之?辣")

def show_final_structure():
    """憿舐內?蝯??蝯?"""
    
    print("\n?? 皜?敺??蝯?:")
    
    important_items = [
        "src/",
        "frontend/",
        "mcp-server/",
        "docs/",
        "examples/",
        "main.py",
        "api_server.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".env.example",
    ]
    
    for item in important_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                print(f"  ?? {item}")
            else:
                print(f"  ?? {item}")
        else:
            print(f"  ??{item} (蝻箏仃)")

def main():
    """銝餃??""
    
    print("?? GitHub 銝皞?撌亙")
    print("=" * 50)
    
    # 蝣箄???
    response = input("蝣箏?閬???隞嗅?嚗??芷皜祈岫?辣???隞?(y/N): ")
    if response.lower() != 'y':
        print("??撌脣?瘨?)
        return
    
    # ?瑁?皜?
    cleanup_for_github()
    
    # 瑼Ｘ???辣
    check_sensitive_files()
    
    # 瑼Ｘ憭扳?隞?
    check_file_sizes()
    
    # 憿舐內?蝯?瑽?
    show_final_structure()
    
    print("\n??皜?摰?嚗?)
    print("\n?? 銝?甇?")
    print("1. 瑼Ｘ .env ?辣?臬??祕??API ?嚗?閰脫??歹?")
    print("2. 蝣箄? .gitignore 閮剖?甇?Ⅱ")
    print("3. ?瑁? git add . ??git commit")
    print("4. ?券 GitHub: git push origin main")

if __name__ == "__main__":
    main()

