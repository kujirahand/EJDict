"""
SQLiteのdockudbテーブルのvalueを手動修正するFlask Webアプリ
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import time
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション管理用

# HTMLベーステンプレート（共通部分）
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQLite dockudb テーブル Value 修正ツール</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #333;
        }
        .menu {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .menu a {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .menu a:hover {
            background-color: #0056b3;
        }
        .menu a.active {
            background-color: #28a745;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
        }
        .json-valid {
            color: #28a745;
            font-weight: bold;
        }
        .json-invalid {
            color: #dc3545;
            font-weight: bold;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 150px;
            font-family: monospace;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .alert-success {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .alert-danger {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .alert-info {
            background-color: #cce7ff;
            border-color: #b8daff;
            color: #004085;
        }
        .record-detail {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .json-preview {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            white-space: pre-wrap;
            border-left: 4px solid #007bff;
            margin: 10px 0;
        }
        .value-preview {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SQLite dockudb テーブル Value 修正ツール</h1>
        
        <div class="menu">
            <a href="{{ url_for('index') }}" {% if active_page == 'index' %}class="active"{% endif %}>レコード一覧</a>
            <a href="{{ url_for('edit_form') }}" {% if active_page == 'edit' %}class="active"{% endif %}>レコード修正</a>
            <a href="{{ url_for('invalid_json') }}" {% if active_page == 'invalid' %}class="active"{% endif %}>無効JSON一覧</a>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        CONTENT_PLACEHOLDER
    </div>
</body>
</html>
"""

def connect_database():
    """データベースに接続"""
    db_path = "ai_reporter.db"
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error:
        return None

def validate_json(value):
    """JSONの妥当性をチェック"""
    if not value or not value.strip():
        return True, "空の値です"
    
    try:
        json.loads(value)
        return True, "有効なJSONです"
    except json.JSONDecodeError as e:
        return False, f"無効なJSON: {str(e)}"

def format_json(value):
    """JSONを整形して返す"""
    if not value or not value.strip():
        return ""
    
    try:
        parsed = json.loads(value)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return value

def render_page(content, active_page='index', **kwargs):
    """ページをレンダリングする共通関数"""
    full_html = BASE_TEMPLATE.replace('CONTENT_PLACEHOLDER', content)
    return render_template_string(full_html, active_page=active_page, **kwargs)

@app.route('/')
def index():
    """レコード一覧ページ"""
    # ページネーション設定
    page = request.args.get('page', 1, type=int)
    per_page = 30  # 1ページあたりのレコード数
    offset = (page - 1) * per_page
    
    conn = connect_database()
    if not conn:
        flash('データベースに接続できません。', 'danger')
        content = "<p>データベースファイル 'ai_reporter.db' が見つかりません。</p>"
        return render_page(content, 'index')
    
    try:
        cursor = conn.cursor()
        
        # 総レコード数を取得
        cursor.execute("SELECT COUNT(*) FROM dockudb")
        total_records = cursor.fetchone()[0]
        
        # ページング対応でレコードを取得
        cursor.execute("SELECT id, tag, value, ctime, mtime FROM dockudb ORDER BY id LIMIT ? OFFSET ?", 
                      (per_page, offset))
        records = cursor.fetchall()
        
        # レコードにJSONバリデーション情報を追加
        processed_records = []
        for record in records:
            is_valid, validation_msg = validate_json(record[2])
            value_preview = record[2] if record[2] else "(空)"
            if len(value_preview) > 50:
                value_preview = value_preview[:47] + "..."
            
            processed_records.append({
                'id': record[0],
                'tag': record[1],
                'value': record[2],
                'value_preview': value_preview,
                'is_valid_json': is_valid,
                'validation_msg': validation_msg,
                'ctime': time.ctime(record[3]) if record[3] > 0 else 'N/A',
                'mtime': time.ctime(record[4]) if record[4] > 0 else 'N/A'
            })
        
        # ページネーション情報を計算
        total_pages = (total_records + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
    except sqlite3.Error as e:
        flash(f'データベースエラー: {e}', 'danger')
        processed_records = []
        total_records = 0
        total_pages = 0
        has_prev = False
        has_next = False
    finally:
        conn.close()
    
    content = """
        <h2>全レコード一覧</h2>
        <div class="alert alert-info">
            総レコード数: {{ total_records }}件 ({{ page }}/{{ total_pages }}ページ)
        </div>
        
        {% if records %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tag</th>
                    <th>JSON</th>
                    <th>Value (プレビュー)</th>
                    <th>作成日時</th>
                    <th>更新日時</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for record in records %}
                <tr>
                    <td>{{ record.id }}</td>
                    <td>{{ record.tag }}</td>
                    <td>
                        {% if record.is_valid_json %}
                            <span class="json-valid">✓</span>
                        {% else %}
                            <span class="json-invalid">✗</span>
                        {% endif %}
                    </td>
                    <td class="value-preview">{{ record.value_preview }}</td>
                    <td>{{ record.ctime }}</td>
                    <td>{{ record.mtime }}</td>
                    <td>
                        <a href="{{ url_for('edit_form', record_id=record.id) }}">編集</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- ページネーション -->
        <div style="margin-top: 20px; text-align: center;">
            {% if has_prev %}
                <a href="{{ url_for('index', page=page-1) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px;">← 前のページ</a>
            {% endif %}
            
            <!-- ページ番号表示 -->
            {% for p in range([1, page-2]|max, [total_pages, page+2]|min + 1) %}
                {% if p == page %}
                    <span style="margin: 0 5px; padding: 8px 16px; background-color: #28a745; color: white; border-radius: 4px;">{{ p }}</span>
                {% else %}
                    <a href="{{ url_for('index', page=p) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;">{{ p }}</a>
                {% endif %}
            {% endfor %}
            
            {% if has_next %}
                <a href="{{ url_for('index', page=page+1) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px;">次のページ →</a>
            {% endif %}
        </div>
        {% else %}
        <p>レコードが見つかりません。</p>
        {% endif %}
    """
    
    return render_page(content, 'index', 
                      records=processed_records, 
                      total_records=total_records,
                      total_pages=total_pages,
                      page=page,
                      has_prev=has_prev,
                      has_next=has_next)

@app.route('/edit', methods=['GET', 'POST'])
def edit_form():
    """レコード編集ページ"""
    if request.method == 'GET':
        record_id = request.args.get('record_id', type=int)
        current_record = None
        
        if record_id:
            conn = connect_database()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, tag, value, ctime, mtime FROM dockudb WHERE id = ?", (record_id,))
                    record = cursor.fetchone()
                    
                    if record:
                        is_valid, validation_msg = validate_json(record[2])
                        current_record = {
                            'id': record[0],
                            'tag': record[1],
                            'value': record[2],
                            'formatted_value': format_json(record[2]),
                            'is_valid_json': is_valid,
                            'validation_msg': validation_msg,
                            'ctime': time.ctime(record[3]) if record[3] > 0 else 'N/A',
                            'mtime': time.ctime(record[4]) if record[4] > 0 else 'N/A'
                        }
                    else:
                        flash(f'ID {record_id} のレコードが見つかりません。', 'danger')
                
                except sqlite3.Error as e:
                    flash(f'データベースエラー: {e}', 'danger')
                finally:
                    conn.close()
        
        content = """
            <h2>レコード修正</h2>
            
            <form method="GET" action="{{ url_for('edit_form') }}">
                <div class="form-group">
                    <label for="record_id">修正するレコードのID:</label>
                    <input type="number" id="record_id" name="record_id" value="{{ request.args.get('record_id', '') }}" required>
                    <button type="submit">レコード表示</button>
                </div>
            </form>
            
            {% if current_record %}
            <div class="record-detail">
                <h3>現在のレコード情報 (ID: {{ current_record.id }})</h3>
                <p><strong>Tag:</strong> {{ current_record.tag }}</p>
                <p><strong>JSON検証:</strong> 
                    {% if current_record.is_valid_json %}
                        <span class="json-valid">✓ {{ current_record.validation_msg }}</span>
                    {% else %}
                        <span class="json-invalid">✗ {{ current_record.validation_msg }}</span>
                    {% endif %}
                </p>
                
                {% if current_record.formatted_value %}
                <p><strong>現在のValue (整形版):</strong></p>
                <div class="json-preview">{{ current_record.formatted_value }}</div>
                {% else %}
                <p><strong>現在のValue:</strong> (空の値)</p>
                {% endif %}
                
                <p><strong>作成日時:</strong> {{ current_record.ctime }}</p>
                <p><strong>更新日時:</strong> {{ current_record.mtime }}</p>
            </div>
            
            <form method="POST" action="{{ url_for('edit_form') }}">
                <input type="hidden" name="record_id" value="{{ current_record.id }}">
                <div class="form-group">
                    <label for="new_value">新しいValue:</label>
                    <textarea id="new_value" name="new_value" placeholder="新しいJSONまたはテキストを入力してください...">{{ current_record.value }}</textarea>
                </div>
                <button type="submit">更新</button>
            </form>
            {% endif %}
        """
        
        return render_page(content, 'edit', current_record=current_record)
    
    else:  # POST
        record_id = request.form.get('record_id', type=int)
        new_value = request.form.get('new_value', '')
        
        if not record_id:
            flash('レコードIDが指定されていません。', 'danger')
            return redirect(url_for('edit_form'))
        
        # JSONバリデーション
        is_valid, validation_msg = validate_json(new_value)
        
        if not is_valid:
            flash(f'警告: {validation_msg}', 'danger')
        
        # データベース更新
        conn = connect_database()
        if not conn:
            flash('データベースに接続できません。', 'danger')
            return redirect(url_for('edit_form', record_id=record_id))
        
        try:
            cursor = conn.cursor()
            current_time = int(time.time())
            cursor.execute(
                "UPDATE dockudb SET value = ?, mtime = ? WHERE id = ?",
                (new_value, current_time, record_id)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                flash(f'ID {record_id} のvalueを正常に更新しました。', 'success')
            else:
                flash(f'ID {record_id} のレコードが見つからないため、更新できませんでした。', 'danger')
        
        except sqlite3.Error as e:
            flash(f'更新エラー: {e}', 'danger')
            conn.rollback()
        finally:
            conn.close()
        
        return redirect(url_for('edit_form', record_id=record_id))

@app.route('/invalid-json')
def invalid_json():
    """無効なJSONを持つレコード一覧"""
    # ページネーション設定
    page = request.args.get('page', 1, type=int)
    per_page = 30  # 1ページあたりのレコード数
    offset = (page - 1) * per_page
    
    conn = connect_database()
    if not conn:
        flash('データベースに接続できません。', 'danger')
        content = "<p>データベースファイル 'ai_reporter.db' が見つかりません。</p>"
        return render_page(content, 'invalid')
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tag, value FROM dockudb ORDER BY id")
        all_records = cursor.fetchall()
        
        # 全レコードから無効なJSONを抽出
        all_invalid_records = []
        for record in all_records:
            is_valid, validation_msg = validate_json(record[2])
            if not is_valid:
                value_preview = record[2] if record[2] else "(空)"
                if len(value_preview) > 100:
                    value_preview = value_preview[:97] + "..."
                
                all_invalid_records.append({
                    'id': record[0],
                    'tag': record[1],
                    'value': record[2],
                    'value_preview': value_preview,
                    'validation_msg': validation_msg
                })
        
        # ページング処理
        total_invalid = len(all_invalid_records)
        start_idx = offset
        end_idx = offset + per_page
        invalid_records = all_invalid_records[start_idx:end_idx]
        
        # ページネーション情報を計算
        total_pages = (total_invalid + per_page - 1) // per_page if total_invalid > 0 else 1
        has_prev = page > 1
        has_next = page < total_pages
    
    except sqlite3.Error as e:
        flash(f'データベースエラー: {e}', 'danger')
        invalid_records = []
        total_invalid = 0
        total_pages = 0
        has_prev = False
        has_next = False
    finally:
        conn.close()
    
    content = """
        <h2>無効なJSONを持つレコード一覧</h2>
        {% if total_invalid > 0 %}
        <div class="alert alert-info">
            無効なJSONレコード: {{ total_invalid }}件 ({{ page }}/{{ total_pages }}ページ)
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tag</th>
                    <th>エラー内容</th>
                    <th>Value (プレビュー)</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for record in invalid_records %}
                <tr>
                    <td>{{ record.id }}</td>
                    <td>{{ record.tag }}</td>
                    <td class="json-invalid">{{ record.validation_msg }}</td>
                    <td class="value-preview">{{ record.value_preview }}</td>
                    <td>
                        <a href="{{ url_for('edit_form', record_id=record.id) }}">修正</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- ページネーション -->
        <div style="margin-top: 20px; text-align: center;">
            {% if has_prev %}
                <a href="{{ url_for('invalid_json', page=page-1) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px;">← 前のページ</a>
            {% endif %}
            
            <!-- ページ番号表示 -->
            {% for p in range([1, page-2]|max, [total_pages, page+2]|min + 1) %}
                {% if p == page %}
                    <span style="margin: 0 5px; padding: 8px 16px; background-color: #28a745; color: white; border-radius: 4px;">{{ p }}</span>
                {% else %}
                    <a href="{{ url_for('invalid_json', page=p) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;">{{ p }}</a>
                {% endif %}
            {% endfor %}
            
            {% if has_next %}
                <a href="{{ url_for('invalid_json', page=page+1) }}" style="margin: 0 5px; padding: 8px 16px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px;">次のページ →</a>
            {% endif %}
        </div>
        {% else %}
        <div class="alert alert-success">
            無効なJSONを持つレコードはありません。
        </div>
        {% endif %}
    """
    
    return render_page(content, 'invalid', 
                      invalid_records=invalid_records,
                      total_invalid=total_invalid,
                      total_pages=total_pages,
                      page=page,
                      has_prev=has_prev,
                      has_next=has_next)

@app.route('/api/validate-json', methods=['POST'])
def validate_json_api():
    """JSON検証API（リアルタイム検証用）"""
    data = request.get_json()
    value = data.get('value', '')
    
    is_valid, validation_msg = validate_json(value)
    
    formatted_value = ""
    if is_valid and value.strip():
        formatted_value = format_json(value)
    
    return jsonify({
        'is_valid': is_valid,
        'message': validation_msg,
        'formatted_value': formatted_value
    })

if __name__ == "__main__":
    # 開発サーバーで実行
    print("=== SQLite dockudb テーブル Value 修正 Webアプリ ===")
    print("ブラウザで http://localhost:8080 にアクセスしてください")
    app.run(debug=True, host='0.0.0.0', port=8080)
