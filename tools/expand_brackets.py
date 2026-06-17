#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語キーに含まれるブラケット [...] を展開するスクリプト

例:
  adrenalin[e] -> adrenalin,adrenaline
  able [bodied] seaman -> able seaman,able bodied seaman
"""

import os
import re
from pathlib import Path

def expand_word(word):
    if '[' not in word or ']' not in word:
        return [word]
    
    pattern = re.compile(r'\[([^\]]+)\]')
    
    def recurse(text):
        match = pattern.search(text)
        if not match:
            # Replace multiple spaces with a single space and trim
            cleaned = re.sub(r'\s+', ' ', text).strip()
            return [cleaned]
        
        start, end = match.span()
        content = match.group(1)
        
        without_content = text[:start] + text[end:]
        with_content = text[:start] + content + text[end:]
        
        res = []
        for opt in [without_content, with_content]:
            for item in recurse(opt):
                if item not in res:
                    res.append(item)
        return res
    
    return recurse(word)

def process_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    modified = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue
        
        parts = line.split('\t', 1)
        if len(parts) != 2:
            new_lines.append(line)
            continue
        
        key, meaning = parts
        
        # We only expand brackets if they are in the key.
        if '[' in key and ']' in key:
            # Split the key by comma
            subkeys = [k.strip() for k in key.split(',')]
            expanded_subkeys = []
            for subkey in subkeys:
                expanded_subkeys.extend(expand_word(subkey))
            
            # Join the expanded subkeys
            new_key = ','.join(expanded_subkeys)
            new_line = f"{new_key}\t{meaning}"
            new_lines.append(new_line)
            print(f"  [EXPAND] {key} -> {new_key}")
            modified = True
        else:
            new_lines.append(line)
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  Saved {filepath}")
    return modified

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src"
    
    files = sorted(src_dir.glob("*.txt"))
    for file in files:
        process_file(file)

if __name__ == "__main__":
    main()
