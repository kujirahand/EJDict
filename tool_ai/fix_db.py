#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLiteデータベース内で重複するtagを検索するスクリプト
"""

import sqlite3
import os

def find_duplicate_tags(db_path):
    """重複するtagを持つレコードを検索する"""
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return
    
    try:
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 重複するtagを検索するクエリ
        query = """
        SELECT tag, COUNT(*) as count
        FROM dockudb
        WHERE tag != ''
        GROUP BY tag
        HAVING COUNT(*) >= 2
        ORDER BY count DESC, tag
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("重複するtagは見つかりませんでした。")
            return
        
        print(f"重複するtagが見つかりました（{len(results)}件）:")
        print("-" * 50)
        
        for tag, count in results:
            print(f"Tag: '{tag}' - 出現回数: {count}")
            
            # 各tagの詳細情報を表示
            detail_query = """
            SELECT id, value, ctime, mtime
            FROM dockudb
            WHERE tag = ?
            ORDER BY id
            """
            cursor.execute(detail_query, (tag,))
            records = cursor.fetchall()
            
            for record in records:
                id_val, value, ctime, mtime = record
                value_preview = value[:50] + "..." if len(value) > 50 else value
                print(f"  ID: {id_val}, Value: '{value_preview}', CTime: {ctime}, MTime: {mtime}")
            print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLiteエラー: {e}")
    except (OSError, IOError) as e:
        print(f"ファイルアクセスエラー: {e}")

def remove_duplicate_tags(db_path):
    """重複するtagを削除する（最新のレコードを残す）"""
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return
    
    conn = None
    try:
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 重複するtagを検索
        duplicate_query = """
        SELECT tag, COUNT(*) as count
        FROM dockudb
        WHERE tag != ''
        GROUP BY tag
        HAVING COUNT(*) >= 2
        ORDER BY count DESC, tag
        """
        
        cursor.execute(duplicate_query)
        duplicate_tags = cursor.fetchall()
        
        if not duplicate_tags:
            print("重複するtagは見つかりませんでした。")
            return
        
        print(f"重複するtagが{len(duplicate_tags)}件見つかりました。削除を開始します...")
        print("-" * 60)
        
        total_deleted = 0
        
        for tag, count in duplicate_tags:
            print(f"Tag: '{tag}' - {count}件の重複")
            
            # 各tagで最新のレコード（最大ID）以外を削除
            delete_query = """
            DELETE FROM dockudb
            WHERE tag = ? AND id NOT IN (
                SELECT MAX(id) FROM dockudb WHERE tag = ?
            )
            """
            
            cursor.execute(delete_query, (tag, tag))
            deleted_count = cursor.rowcount
            total_deleted += deleted_count
            
            print(f"  → {deleted_count}件のレコードを削除しました")
        
        # 変更をコミット
        conn.commit()
        print("-" * 60)
        print(f"削除完了: 合計{total_deleted}件のレコードを削除しました")
        
        # 削除後の状況を確認
        print("\n削除後の確認:")
        remaining_query = """
        SELECT tag, COUNT(*) as count
        FROM dockudb
        WHERE tag != ''
        GROUP BY tag
        HAVING COUNT(*) >= 2
        """
        cursor.execute(remaining_query)
        remaining_duplicates = cursor.fetchall()
        
        if remaining_duplicates:
            print(f"まだ{len(remaining_duplicates)}件の重複が残っています:")
            for tag, count in remaining_duplicates:
                print(f"  Tag: '{tag}' - {count}件")
        else:
            print("すべての重複が削除されました。")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLiteエラー: {e}")
        if conn is not None:
            conn.rollback()
    except (OSError, IOError) as e:
        print(f"ファイルアクセスエラー: {e}")
    finally:
        if conn is not None:
            conn.close()

def main():
    """メイン関数"""
    db_path = "ai_reporter.db"
    print(f"データベース: {db_path}")
    print("=" * 60)
    
    # まず重複を確認
    print("1. 重複するtagを検索中...")
    print()
    find_duplicate_tags(db_path)
    
    print("\n" + "=" * 60)
    
    # ユーザーに削除の確認を求める
    response = input("重複するtagを削除しますか？ (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        print("\n2. 重複するtagを削除中...")
        remove_duplicate_tags(db_path)
    else:
        print("削除をキャンセルしました。")

if __name__ == "__main__":
    main()