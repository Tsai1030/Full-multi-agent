"""
靽桀儔 Claude 閮剖???
"""

import os
from pathlib import Path

def fix_claude_settings():
    """靽桀儔 Claude 閮剖?"""
    print("? 靽桀儔 Claude 閮剖???...")
    
    # 1. 瑼Ｘ .env ?辣
    env_file = Path(".env")
    if not env_file.exists():
        print("??.env ?辣銝???)
        return False
    
    # 2. 霈??.env ?辣
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("?? 瑼Ｘ .env ?辣?批捆...")
    
    # 瑼Ｘ?臬??ANTHROPIC_API_KEY
    if "ANTHROPIC_API_KEY=" in content:
        lines = content.split('\n')
        for line in lines:
            if line.startswith('ANTHROPIC_API_KEY='):
                key = line.split('=', 1)[1].strip()
                if key and not key.startswith('your_'):
                    print(f"???曉????ANTHROPIC_API_KEY: {key[:20]}...")
                else:
                    print("??ANTHROPIC_API_KEY ?芾身蝵格??⊥?")
                    return False
                break
    else:
        print("??.env ?辣銝剜???ANTHROPIC_API_KEY")
        return False
    
    # 3. 撘瑕?頛?啣?霈
    print("?? ?頛?啣?霈...")
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # 4. 皜祈岫閮剖?蝟餌絞
    print("?妒 皜祈岫閮剖?蝟餌絞...")
    try:
        # ?撠閮剖?
        import importlib
        import sys
        
        # 皜閮剖?璅∠?敹怠?
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        
        # ?撠
        from backend.src.config.settings import get_settings
        settings = get_settings()
        
        print(f"   Anthropic API Key: {'??撌脰身蝵? if settings.anthropic.api_key and not settings.anthropic.api_key.startswith('your_') else '???芾身蝵?}")
        print(f"   Anthropic Model: {settings.anthropic.model}")
        
        if settings.anthropic.api_key and not settings.anthropic.api_key.startswith('your_'):
            print("??閮剖?蝟餌絞靽桀儔??")
            return True
        else:
            print("??閮剖?蝟餌絞隞???")
            return False
            
    except Exception as e:
        print(f"??閮剖?蝟餌絞皜祈岫憭望?: {str(e)}")
        return False

def create_simple_test():
    """?萄遣蝪∪??Claude 皜祈岫"""
    print("\n?妒 ?萄遣蝪∪???Claude 皜祈岫...")
    
    try:
        # ?湔敺憓??貊??
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        
        if not api_key or api_key.startswith('your_'):
            print("???啣?霈銝剜????? API 撖")
            return False
        
        print(f"???啣?霈 API Key: {api_key[:20]}...")
        print(f"???啣?霈 Model: {model}")
        
        # ?湔皜祈岫 Anthropic
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model=model,
            max_tokens=20,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        print("???湔 Anthropic 皜祈岫??")
        print(f"   ??: {response.content[0].text}")
        
        return True
        
    except Exception as e:
        print(f"???湔皜祈岫憭望?: {str(e)}")
        return False

def main():
    """銝餃??""
    print("? Claude 閮剖?靽桀儔撌亙")
    print("=" * 50)
    
    # 1. 靽桀儔閮剖?
    settings_fixed = fix_claude_settings()
    
    # 2. ?湔皜祈岫
    direct_test = create_simple_test()
    
    print(f"\n?? 靽桀儔蝯?:")
    print(f"   閮剖?蝟餌絞: {'??靽桀儔??' if settings_fixed else '??隞???'}")
    print(f"   ?湔皜祈岫: {'????' if direct_test else '??憭望?'}")
    
    if direct_test:
        print(f"\n? 蝯?:")
        print(f"   Claude API ?祈澈?舀迤撣貊?")
        print(f"   ???航?冽蝟餌絞銝剔?閮剖?頛")
        print(f"   撱箄降?? Python ?啣????圈?銵?main.py")
        
        print(f"\n?? 撱箄降??:")
        print(f"   1. ?? Python ?啣?")
        print(f"   2. ??? python main.py")
        print(f"   3. 憒?隞???嚗頂蝯勗隞亙雿輻 GPT Agent")
    else:
        print(f"\n??  Claude API ??憿?雿頂蝯望敹??賭??舐")

if __name__ == "__main__":
    main()

