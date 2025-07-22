#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100件ずつに分割された辞書データファイルを結合するスクリプト

使用方法:
    python join100.py

機能:
- srcフォルダ内のサブディレクトリ（a/, b/, c/, ...）を処理
- 各サブディレクトリ内の分割ファイル（a001.txt, a002.txt, ...）を結合
- 結合後のファイルを元の場所に保存（a.txt, b.txt, ...）
"""

import os
import sys
import glob
from pathlib import Path


def join_files(input_dir, output_file):
    """
    分割されたファイルを結合する
    
    Args:
        input_dir (str): 分割ファイルがあるディレクトリパス
        output_file (str): 出力ファイルパス
    """
    # ディレクトリ名から文字を取得（例: /path/to/a -> a）
    dir_name = Path(input_dir).name
    
    print(f"処理中: {input_dir} -> {output_file}")
    
    if not os.path.exists(input_dir):
        print(f"  警告: {input_dir} が存在しません")
        return
    
    # 分割ファイルのパターンを作成（例: a001.txt, a002.txt, ...）
    pattern = os.path.join(input_dir, f"{dir_name}*.txt")
    input_files = sorted(glob.glob(pattern))
    
    if not input_files:
        print(f"  警告: {input_dir} に {dir_name}*.txt のファイルが見つかりません")
        return
    
    print(f"  対象ファイル数: {len(input_files)}個")
    
    try:
        all_lines = []
        total_count = 0
        
        # 各分割ファイルを読み込み
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 空行を除去
            lines = [line.strip() for line in lines if line.strip()]
            all_lines.extend(lines)
            total_count += len(lines)
            
            print(f"    読込: {os.path.basename(input_file)} ({len(lines)}件)")
        
        # 結合されたデータをソート
        all_lines.sort()
        
        # 出力ファイルに保存
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in all_lines:
                f.write(line + '\n')
        
        print(f"  完了: {total_count}件を結合 -> {output_file}")
        
    except Exception as e:
        print(f"エラー: {input_dir} の処理中にエラーが発生しました: {e}")


def main():
    """メイン処理"""
    # スクリプトのディレクトリを基準にパスを設定
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src"
    
    print("=== 辞書データ結合ツール ===")
    print(f"プロジェクトルート: {project_root}")
    print(f"ソースディレクトリ: {src_dir}")
    
    # srcディレクトリが存在するかチェック
    if not src_dir.exists():
        print(f"エラー: {src_dir} が見つかりません")
        sys.exit(1)
    
    # a/～z/のサブディレクトリを取得
    subdirs = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        subdir = src_dir / letter
        if subdir.exists() and subdir.is_dir():
            subdirs.append(subdir)
    
    if not subdirs:
        print(f"エラー: {src_dir} にa/～z/のサブディレクトリが見つかりません")
        sys.exit(1)
    
    print(f"対象ディレクトリ数: {len(subdirs)}個")
    print()
    
    # 各サブディレクトリを処理
    for subdir in subdirs:
        # ディレクトリ名から文字を取得（例: a/ -> a）
        letter = subdir.name
        
        # 出力ファイルパスを設定（例: src/a.txt）
        output_file = src_dir / f"{letter}.txt"
        
        # ファイルを結合
        join_files(subdir, output_file)
        print()
    
    print("=== すべての処理が完了しました ===")


if __name__ == "__main__":
    main()
