#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100件ずつに分割された辞書データファイルを削除するスクリプト

使用方法:
    python remove100.py

機能:
- srcフォルダ内のサブディレクトリ（a/, b/, c/, ...）を処理
- 各サブディレクトリ内の分割ファイル（a001.txt, a002.txt, ...）を削除
- 空になったサブディレクトリも削除
"""

import os
import sys
import glob
import shutil
from pathlib import Path


def remove_split_files(input_dir):
    """
    分割されたファイルを削除する
    
    Args:
        input_dir (str): 分割ファイルがあるディレクトリパス
    """
    # ディレクトリ名から文字を取得（例: /path/to/a -> a）
    dir_name = Path(input_dir).name
    
    print(f"処理中: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"  スキップ: {input_dir} が存在しません")
        return
    
    # 分割ファイルのパターンを作成（例: a001.txt, a002.txt, ...）
    pattern = os.path.join(input_dir, f"{dir_name}*.txt")
    split_files = sorted(glob.glob(pattern))
    
    if not split_files:
        print(f"  スキップ: {input_dir} に {dir_name}*.txt のファイルが見つかりません")
        return
    
    print(f"  対象ファイル数: {len(split_files)}個")
    
    try:
        # 各分割ファイルを削除
        for split_file in split_files:
            os.remove(split_file)
            print(f"    削除: {os.path.basename(split_file)}")
        
        # ディレクトリが空になったかチェック
        remaining_files = os.listdir(input_dir)
        if not remaining_files:
            # 空のディレクトリを削除
            os.rmdir(input_dir)
            print(f"  ディレクトリ削除: {input_dir}")
        else:
            print(f"  ディレクトリ保持: {input_dir} (他のファイルが残っています: {remaining_files})")
        
        print(f"  完了: {len(split_files)}個のファイルを削除")
        
    except Exception as e:
        print(f"エラー: {input_dir} の処理中にエラーが発生しました: {e}")


def main():
    """メイン処理"""
    # スクリプトのディレクトリを基準にパスを設定
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src"
    
    print("=== 分割ファイル削除ツール ===")
    print(f"プロジェクトルート: {project_root}")
    print(f"ソースディレクトリ: {src_dir}")
    print()
    
    # srcディレクトリが存在するかチェック
    if not src_dir.exists():
        print(f"エラー: {src_dir} が見つかりません")
        sys.exit(1)
    
    # 確認メッセージ
    print("⚠️  警告: この操作により分割ファイル（a001.txt, a002.txt, ...）が削除されます。")
    print("元のファイル（a.txt, b.txt, ...）は削除されません。")
    print()
    
    # ユーザーに確認を求める
    while True:
        confirmation = input("削除を実行しますか？ [y/N]: ").strip().lower()
        if confirmation in ['y', 'yes']:
            break
        elif confirmation in ['n', 'no', '']:
            print("操作がキャンセルされました。")
            sys.exit(0)
        else:
            print("'y' または 'n' で答えてください。")
    
    print()
    
    # a/～z/のサブディレクトリを取得
    subdirs = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        subdir = src_dir / letter
        if subdir.exists() and subdir.is_dir():
            subdirs.append(subdir)
    
    if not subdirs:
        print(f"情報: {src_dir} にa/～z/のサブディレクトリが見つかりません")
        print("削除する分割ファイルがありません。")
        sys.exit(0)
    
    print(f"対象ディレクトリ数: {len(subdirs)}個")
    print()
    
    # 各サブディレクトリを処理
    deleted_dirs = 0
    deleted_files = 0
    
    for subdir in subdirs:
        # 削除前のファイル数をカウント
        dir_name = subdir.name
        pattern = str(subdir / f"{dir_name}*.txt")
        files_before = len(glob.glob(pattern))
        
        # ファイルを削除
        remove_split_files(subdir)
        
        # 削除後の状態をチェック
        if not subdir.exists():
            deleted_dirs += 1
        deleted_files += files_before
        
        print()
    
    print("=== 削除完了 ===")
    print(f"削除されたファイル数: {deleted_files}個")
    print(f"削除されたディレクトリ数: {deleted_dirs}個")


if __name__ == "__main__":
    main()
