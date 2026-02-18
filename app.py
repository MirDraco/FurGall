from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3 # sqlite 추가했음 
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    """서버 시작 전, 회원 명부가 없으면 만드는 함수"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # User 테이블 생성 (아이디, 비밀번호, 관리자여부)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            user_pw TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()
# ==========================================
# 1. 서버 설정 구역 (Configuration)
# - 서버가 작동하는 데 필요한 기본 규칙을 정합니다.
# ==========================================
app = Flask(__name__)
app.secret_key = 'mir_secret'

app.config['UPLOAD_FOLDER'] = 'static/uploads' # 사진 저장 경로
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 최대 파일 크기 (100MB)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'} # 허용하는 사진 확장자

def allowed_file(filename):
    """파일 확장자가 사진인지 검사하는 도구"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# 2. 페이지 이동 구역 (Routing)
# - 사용자가 주소창에 친 주소에 따라 HTML 화면을 보여줍니다.
# ==========================================
@app.route('/')
@app.route('/<page>')
def render_page(page='index'):
    """주소창의 이름과 똑같은 HTML 파일을 templates 폴더에서 찾아 보여줌"""
    template_file = f'{page}.html'
    template_path = os.path.join('templates', template_file)
    
    if os.path.exists(template_path):
        return render_template(template_file)
    
    return "페이지를 찾을 수 없습니다!", 404


# ==========================================
# 3. 사진 업로드 기능 (Photo Upload)
# - 사용자가 올린 사진을 서버 컴퓨터에 저장합니다.
# ==========================================
@app.route('/upload', methods=['POST'])
def upload_file():
    # 관리자가 아닐 경우 알림창을 띄우고 다시 사진 페이지로 보냄
    if session.get('is_admin') != 1:
        return redirect(url_for('render_page', page='photo'))
    
    if 'file' not in request.files:
        return redirect(url_for('render_page', page='photo'))
    
    files = request.files.getlist('file')
    year = request.form.get('year', '2026')
    
    # 연도 폴더 생성
    year_folder = os.path.join(app.config['UPLOAD_FOLDER'], year)
    os.makedirs(year_folder, exist_ok=True)
    
    uploaded_count = 0
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            # 이름 중복 방지를 위해 현재 시간을 이름에 붙임
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{timestamp}_{original_filename}"
            
            save_path = os.path.join(year_folder, filename)
            file.save(save_path)
            uploaded_count += 1
    
    print(f"✅ {uploaded_count}개 파일 업로드 완료!")
    return redirect(url_for('render_page', page='photo'))


# ==========================================
# 4. 데이터 API 구역 (Data API)
# - 화면이 아니라 '데이터'만 주고받는 창구입니다. (사진 목록 가져오기, 삭제)
# ==========================================
# [사진 목록 가져오기]
@app.route('/api/photos/<year>')
def get_photos(year):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], year)
    if not os.path.exists(folder_path):
        return jsonify([])
    
    files = []
    all_files = os.listdir(folder_path)
    for filename in sorted(all_files, reverse=True):
        if allowed_file(filename):
            files.append({
                'filename': filename,
                'url': f'/static/uploads/{year}/{filename}'
            })
    return jsonify(files)

# [사진 삭제하기]
@app.route('/api/photos/<year>/<filename>', methods=['DELETE'])
def delete_photo(year, filename):
    if session.get('is_admin') != 1:
        return jsonify({'error': '관리자만 삭제할 수 있습니다.'}), 403
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], year, safe_filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
        
        os.remove(file_path)
        return jsonify({'success': True, 'message': '삭제되었습니다'}), 200
    except Exception as e:
        return jsonify({'error': '삭제 실패'}), 500

# ==========================================
# 5. 서버 회원가입 구역 (Run)
# - 서버에 회원가입하는 부분입니다.
# ==========================================
@app.route('/register', methods=['POST'])
def register_action():
    new_id = request.form.get('user_id')
    new_pw = request.form.get('user_pw')
    pw_confirm = request.form.get('user_pw_confirm')

    if len(new_pw) < 8:
        flash("비밀번호는 8자 이상이여야 합니다.")
        return redirect(url_for('render_page', page='register'))
    # 2. [추가] 비밀번호와 확인용 비밀번호가 일치하는지 체크!

    if new_pw != pw_confirm:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for('render_page', page='register'))
    
    hashed_pw = generate_password_hash(new_pw)
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # user_id가 중복이면 에러 
        cursor.execute("INSERT INTO User (user_id, user_pw) VALUES (?, ?)", (new_id, hashed_pw))
        conn.commit()
        conn.close()
        flash("회원가입 성공! 로그인 해주세요.")
        return redirect(url_for('render_page', page='login'))
    except sqlite3.IntegrityError:
        # 이 에러는 아이디 중복
        flash("이미 존재하는 아이디 입니다.")
        return redirect(url_for('render_page', page='register'))



# ==========================================
# 6. 서버 로그인 구역 (Run)
# - 서버에 로그인하는 부분입니다.
# ==========================================
@app.route('/login', methods=['POST'])
def login_action():
    # 사용자가 입력한 데이터 가져오기
    typed_id = request.form.get('user_id')
    typed_pw = request.form.get('user_pw')

    # DB 냉장고 열어서 일치하는지 확인하기
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 입력한 아이디와 비번 일치하는 유저가 있는지 확인
    cursor.execute("SELECT * FROM User WHERE user_id = ?", (typed_id,))
    user = cursor.fetchone() # 결과가 있으면 데이터가 나오고 아니면 none이 나옴
    conn.close()

    if user and check_password_hash(user[2], typed_pw):
        session['user_id'] = user[1]
        session['is_admin'] = user[3]
        return redirect(url_for('render_page', page='index'))
    else:
        flash("아이디 또는 비밀번호가 틀렸습니다.")
        return redirect(url_for('render_page', page='login'))

@app.route('/logout')
def logout():
    session.clear() # 세션에 저장된 모든 정보를 삭제 (로그아웃)
    return redirect(url_for('render_page', page='index'))
# ==========================================
# 7. 서버 실행 구역 (Run)
# - 전원을 켜는 부분입니다.
# ==========================================
if __name__ == '__main__':
    # debug=True: 코드를 수정하면 서버가 자동으로 재시작됨
    app.run(debug=True, port=3000)