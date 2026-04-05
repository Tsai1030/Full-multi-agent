"""
靽桀儔?蔭??
"""

import os
from pathlib import Path

def fix_env_file():
    """靽桀儔 .env ?辣銝剔??蔭??"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("??.env ?辣銝???)
        return False
    
    # 霈??摰?
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("? 靽桀儔 .env ?辣?蔭...")
    
    # 靽桀儔 Anthropic 璅∪??迂
    if "Claude Sonnet 3.5 2024-10-22" in content:
        content = content.replace(
            "ANTHROPIC_MODEL=Claude Sonnet 3.5 2024-10-22",
            "ANTHROPIC_MODEL=claude-3-5-sonnet-20241022"
        )
        print("??靽桀儔 Anthropic 璅∪??迂?澆?")
    
    # 瑼Ｘ敹???蝵?
    required_configs = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY"
    ]
    
    missing_configs = []
    for config in required_configs:
        if f"{config}=" not in content or f"{config}=your_" in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"??  蝻箏??閮剔蔭??蝵? {', '.join(missing_configs)}")
        
        # 瘛餃?蝻箏???蝵?
        if "OPENAI_API_KEY" not in content:
            content += "\n# OpenAI API 閮剖?\nOPENAI_API_KEY=your_openai_api_key_here\n"
        
    # 撖怠??辣
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("??.env ?辣靽桀儔摰?")
    return True

def test_imports():
    """皜祈岫??璅∠?????""
    print("\n?妒 皜祈岫璅∠?撠...")
    
    try:
        from backend.src.config.settings import get_settings
        settings = get_settings()
        print("??閮剖?璅∠?撠??")
        
        # 瑼Ｘ Anthropic 閮剖?
        print(f"?? Anthropic 璅∪?: {settings.anthropic.model}")
        print(f"?? Anthropic API Key: {'撌脰身蝵? if settings.anthropic.api_key and not settings.anthropic.api_key.startswith('your_') else '?芾身蝵?}")
        
    except Exception as e:
        print(f"??閮剖?璅∠?撠憭望?: {e}")
        return False
    
    try:
        from backend.src.rag.bge_embeddings import BGEM3Embeddings, HybridEmbeddings
        print("??BGE 撋璅∠?撠??")
    except Exception as e:
        print(f"??BGE 撋璅∠?撠憭望?: {e}")
        return False
    
    try:
        from backend.src.rag.rag_system import ZiweiRAGSystem
        print("??RAG 蝟餌絞璅∠?撠??")
    except Exception as e:
        print(f"??RAG 蝟餌絞璅∠?撠憭望?: {e}")
        return False
    
    try:
        from backend.src.agents.claude_agent import ClaudeAgent
        print("??Claude Agent 璅∠?撠??")
    except Exception as e:
        print(f"??Claude Agent 璅∠?撠憭望?: {e}")
        return False
    
    return True

def main():
    """銝餃??""
    print("? ?蔭??靽桀儔撌亙")
    print("=" * 50)
    
    # 1. 靽桀儔 .env ?辣
    fix_env_file()
    
    # 2. 皜祈岫撠
    if test_imports():
        print("\n?? ??芋蝯??交葫閰阡?嚗?)
        print("\n?? 銝?甇?")
        print("1. 蝣箔???.env ?辣銝剛身蝵格??? API 撖")
        print("2. ?? python main.py 皜祈岫摰蝟餌絞")
        
        # 憿舐內?嗅??蔭???
        try:
            from backend.src.config.settings import get_settings
            settings = get_settings()
            
            print(f"\n?? ?嗅??蔭???")
            print(f"   OpenAI API Key: {'??撌脰身蝵? if settings.openai.api_key and not settings.openai.api_key.startswith('your_') else '???芾身蝵?}")
            print(f"   Anthropic API Key: {'??撌脰身蝵? if settings.anthropic.api_key and not settings.anthropic.api_key.startswith('your_') else '???芾身蝵?}")
            print(f"   Anthropic Model: {settings.anthropic.model}")
            
        except Exception as e:
            print(f"??  ?⊥?霈??蝵? {e}")
    else:
        print("\n???典?璅∠?撠憭望?嚗?瑼Ｘ?航炊靽⊥")

if __name__ == "__main__":
    main()

