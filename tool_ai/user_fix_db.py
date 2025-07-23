"""
SQLiteのdockudbテーブルのvalueを手動修正するスクリプト
"""

import sqlite3
import os
import time
import json

def connect_database():
    """データベースに接続"""
    db_path = "ai_reporter.db"
    if not os.path.exists(db_path):
        print(f"エラー: データベースファイル '{db_path}' が見つかりません。")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}")
        return None

def validate_json(value):
    """JSONの妥当性をチェック"""
    if not value.strip():
        return True, "空の値です"
    
    try:
        json.loads(value)
        return True, "有効なJSONです"
    except json.JSONDecodeError as e:
        return False, f"無効なJSON: {str(e)}"

def show_record(conn, record_id):
    """指定されたIDのレコードを表示"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tag, value, ctime, mtime FROM dockudb WHERE id = ?", (record_id,))
        record = cursor.fetchone()
        
        if record:
            print(f"\n--- レコード情報 (ID: {record_id}) ---")
            print(f"ID: {record[0]}")
            print(f"Tag: {record[1]}")
            
            # JSONバリデーション情報を表示
            is_valid, validation_msg = validate_json(record[2])
            status_icon = "✓" if is_valid else "✗"
            print(f"JSON検証: {status_icon} {validation_msg}")
            
            # Valueの表示（JSONの場合はインデントして表示）
            print("Value:")
            if is_valid and record[2].strip():
                try:
                    # JSONとしてパースして整形表示
                    parsed_json = json.loads(record[2])
                    
                    # インデントありの整形版
                    formatted_json = json.dumps(parsed_json, ensure_ascii=False, indent=2)
                    print("  [整形版 (インデント有り)]")
                    indented_lines = ["    " + line for line in formatted_json.split('\n')]
                    print('\n'.join(indented_lines))
                    
                    # インデントなしの圧縮版
                    compact_json = json.dumps(parsed_json, ensure_ascii=False, separators=(',', ':'))
                    print("\n  [圧縮版 (インデント無し)]")
                    print(f"    {compact_json}")
                    
                except json.JSONDecodeError:
                    # JSONパースに失敗した場合は生の値を表示
                    print(f"  {record[2]}")
            else:
                # 空の値または無効なJSONの場合
                if record[2]:
                    print(f"  {record[2]}")
                else:
                    print("  (空の値)")
            
            print(f"作成日時: {time.ctime(record[3]) if record[3] > 0 else 'N/A'}")
            print(f"更新日時: {time.ctime(record[4]) if record[4] > 0 else 'N/A'}")
            return record[2]  # 現在のvalue値を返す
        else:
            print(f"ID {record_id} のレコードが見つかりません。")
            return None
    except sqlite3.Error as e:
        print(f"レコード取得エラー: {e}")
        return None

def update_value(conn, record_id, new_value):
    """指定されたIDのvalueを更新"""
    try:
        cursor = conn.cursor()
        current_time = int(time.time())
        cursor.execute(
            "UPDATE dockudb SET value = ?, mtime = ? WHERE id = ?",
            (new_value, current_time, record_id)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ ID {record_id} のvalueを正常に更新しました。")
            return True
        else:
            print(f"エラー: ID {record_id} のレコードが見つからないため、更新できませんでした。")
            return False
    except sqlite3.Error as e:
        print(f"更新エラー: {e}")
        conn.rollback()
        return False

def list_invalid_json_records(conn):
    """無効なJSONを持つレコードの一覧を表示"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tag, value FROM dockudb ORDER BY id")
        records = cursor.fetchall()
        
        invalid_records = []
        for record in records:
            is_valid, validation_msg = validate_json(record[2])
            if not is_valid:
                invalid_records.append((record[0], record[1], record[2], validation_msg))
        
        if invalid_records:
            print(f"\n--- 無効なJSONを持つレコード ({len(invalid_records)}件) ---")
            print("ID\tTag\t\tエラー内容")
            print("-" * 70)
            for record in invalid_records:
                print(f"{record[0]}\t{record[1][:10]}\t{record[3]}")
        else:
            print("\n無効なJSONを持つレコードはありません。")
    except sqlite3.Error as e:
        print(f"一覧取得エラー: {e}")

def list_all_records(conn):
    """全レコードの一覧を表示"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tag, value FROM dockudb ORDER BY id")
        records = cursor.fetchall()
        
        if records:
            print("\n--- 全レコード一覧 ---")
            print("ID\tTag\t\tJSON\tValue (プレビュー)")
            print("-" * 70)
            for record in records:
                value_preview = record[2] if record[2] else "(空)"
                if len(value_preview) > 40:
                    value_preview = value_preview[:37] + "..."
                
                # JSONバリデーション
                is_valid, _ = validate_json(record[2])
                json_status = "✓" if is_valid else "✗"
                
                print(f"{record[0]}\t{record[1][:10]}\t{json_status}\t{value_preview}")
        else:
            print("レコードが見つかりません。")
    except sqlite3.Error as e:
        print(f"一覧取得エラー: {e}")

def main():
    """メイン処理"""
    print("=== SQLite dockudb テーブル Value 修正ツール ===")
    
    # データベース接続
    conn = connect_database()
    if not conn:
        return
    
    try:
        while True:
            print("\n--- メニュー ---")
            print("1. レコード一覧表示")
            print("2. 特定IDのvalue修正")
            print("3. 無効なJSONを持つレコード一覧")
            print("4. 終了")
            
            choice = input("\n選択してください (1-4): ").strip()
            
            if choice == "1":
                list_all_records(conn)
            
            elif choice == "2":
                # ID入力
                try:
                    record_id = int(input("\n修正するレコードのIDを入力してください: "))
                except ValueError:
                    print("エラー: 有効な数値を入力してください。")
                    continue
                
                # 現在のレコード表示
                current_value = show_record(conn, record_id)
                if current_value is None:
                    continue
                
                # 新しいvalue入力
                new_value = input("\n新しいvalueを入力してください (空白のままでキャンセル): ")
                
                if new_value.strip() == "":
                    print("キャンセルしました。")
                    continue
                
                # 新しいvalueのJSONバリデーション
                is_valid, validation_msg = validate_json(new_value)
                status_icon = "✓" if is_valid else "✗"
                print(f"\n新しいvalueのJSON検証: {status_icon} {validation_msg}")
                
                # 新しいvalueをインデント表示
                if is_valid and new_value.strip():
                    try:
                        parsed_new = json.loads(new_value)
                        
                        # インデントありの整形版
                        formatted_new = json.dumps(parsed_new, ensure_ascii=False, indent=2)
                        print("\n新しいvalue [整形版 (インデント有り)]:")
                        indented_lines = ["  " + line for line in formatted_new.split('\n')]
                        print('\n'.join(indented_lines))
                        
                        # インデントなしの圧縮版
                        compact_new = json.dumps(parsed_new, ensure_ascii=False, separators=(',', ':'))
                        print("\n新しいvalue [圧縮版 (インデント無し)]:")
                        print(f"  {compact_new}")
                        
                    except json.JSONDecodeError:
                        pass  # バリデーションで既にチェック済み
                
                # JSONが無効な場合の確認
                if not is_valid:
                    force_update = input("JSONが無効ですが、それでも更新しますか？ (y/N): ").strip().lower()
                    if force_update not in ['y', 'yes']:
                        print("更新をキャンセルしました。")
                        continue
                
                # 確認
                print("\n変更内容:")
                print(f"ID: {record_id}")
                print(f"変更前: {current_value}")
                print(f"変更後: {new_value}")
                
                confirm = input("\nこの内容で更新しますか？ (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    if update_value(conn, record_id, new_value):
                        # 更新後のレコード表示
                        print("\n--- 更新後のレコード ---")
                        show_record(conn, record_id)
                else:
                    print("更新をキャンセルしました。")
            
            elif choice == "3":
                list_invalid_json_records(conn)
            
            elif choice == "4":
                print("ツールを終了します。")
                break
            
            else:
                print("無効な選択です。1-4の数字を入力してください。")
    
    finally:
        conn.close()
        print("データベース接続を閉じました。")

if __name__ == "__main__":
    main()