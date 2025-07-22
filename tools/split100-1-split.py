#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辞書データファイルを100件ずつに分割するスクリプト

使用方法:
    python split100.py

機能:
- srcフォルダ内のa.txt～z.txtを処理
- 各ファイルの内容をソート
- 100件ずつに分割してサブフォルダに保存
  例: src/a/a001.txt, src/a/a002.txt, ...
"""

import os
import sys
import glob
from pathlib import Path


def split_file_by_100(input_file, output_dir):
    """
    ファイルを100件ずつに分割する
    
    Args:
        input_file (str): 入力ファイルパス
        output_dir (str): 出力ディレクトリパス
    """
    # ファイル名から文字を取得（例: a.txt -> a）
    file_stem = Path(input_file).stem
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"処理中: {input_file}")
    
    try:
        # ファイルを読み込み
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 空行を除去してソート
        lines = [line.strip() for line in lines if line.strip()]
        lines.sort()
        
        print(f"  総件数: {len(lines)}件")
        
        # 100件ずつに分割
        chunk_size = 100
        chunk_count = 0
        
        for i in range(0, len(lines), chunk_size):
            chunk_count += 1
            chunk = lines[i:i + chunk_size]
            
            # 出力ファイル名を生成（例: a001.txt）
            output_filename = f"{file_stem}{chunk_count:03d}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            # チャンクを保存
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in chunk:
                    f.write(line + '\n')
            
            print(f"    作成: {output_path} ({len(chunk)}件)")
        
        print(f"  完了: {chunk_count}個のファイルに分割")
        
    except Exception as e:
        print(f"エラー: {input_file} の処理中にエラーが発生しました: {e}")


def main():
    """メイン処理"""
    # スクリプトのディレクトリを基準にパスを設定
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src"
    
    print("=== 辞書データ分割ツール ===")
    print(f"プロジェクトルート: {project_root}")
    print(f"ソースディレクトリ: {src_dir}")
    
    # srcディレクトリが存在するかチェック
    if not src_dir.exists():
        print(f"エラー: {src_dir} が見つかりません")
        sys.exit(1)
    
    # a.txt～z.txtのファイルを取得
    pattern = str(src_dir / "[a-z].txt")
    input_files = sorted(glob.glob(pattern))
    
    if not input_files:
        print(f"エラー: {src_dir} にa.txt～z.txtのファイルが見つかりません")
        sys.exit(1)
    
    print(f"対象ファイル数: {len(input_files)}個")
    print()
    
    # 各ファイルを処理
    for input_file in input_files:
        # ファイル名から文字を取得（例: a.txt -> a）
        file_stem = Path(input_file).stem
        
        # 出力ディレクトリを設定（例: src/a/）
        output_dir = src_dir / file_stem
        
        # ファイルを分割
        split_file_by_100(input_file, output_dir)
        print()
    
    print("=== すべての処理が完了しました ===")


if __name__ == "__main__":
    main()
