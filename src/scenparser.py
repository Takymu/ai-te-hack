import re
from typing import Dict


def parse_scenario(text: str) -> Dict:
    result = {
        'charLdesc': [],
        'charRdesc': [], 
        'scenes': [],
        'charLaction': [],
        'charRaction': []
    }
    
    patterns = {
        'charL_desc': r'\[charLdescStart\](.*?)\[charLdecEnd\]',
        'charR_desc': r'\[charRdescStart\](.*?)\[charRdescEnd\]',
        'scene': r'\[scene\](.*?)\[endscene\]',
        'charL_dialogue': r'\[charL\](.*?)\[charLend\]',
        'charR_dialogue': r'\[charR\](.*?)\[charRend\]',
    }
    
    char_l_desc = re.search(patterns['charL_desc'], text, re.DOTALL)
    if char_l_desc:
        content = char_l_desc.group(1).strip()
        result['charLdesc'].append(content if content else None)
    
    char_r_desc = re.search(patterns['charR_desc'], text, re.DOTALL)
    if char_r_desc:
        content = char_r_desc.group(1).strip()
        result['charRdesc'].append(content if content else None)
    
    scenes = re.findall(patterns['scene'], text, re.DOTALL)
    result['scenes'] = [scene.strip() if scene.strip() else None for scene in scenes]
    
    charL_dialogues = re.findall(patterns['charL_dialogue'], text, re.DOTALL)
    result['charLaction'] = [
        dialogue.strip() if dialogue.strip() and dialogue.strip() != '[placeholder]' else None 
        for dialogue in charL_dialogues
    ]
    
    charR_dialogues = re.findall(patterns['charR_dialogue'], text, re.DOTALL)
    result['charRaction'] = [
        dialogue.strip() if dialogue.strip() and dialogue.strip() != '[placeholder]' else None 
        for dialogue in charR_dialogues
    ]
    
    return result

    
