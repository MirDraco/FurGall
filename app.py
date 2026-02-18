from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# 동적 라우팅 
@app.route('/')
@app.route('/<page>')
def render_page(page='index'):
    """동적 라우팅 - 모든 페이지를 한 번에 처리"""
    template_file = f'{page}.html'
    template_path = os.path.join('templates', template_file)
    
    if os.path.exists(template_path):
        return render_template(template_file)
    
    return "페이지를 찾을 수 없습니다!", 404

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 처리"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    files = request.files.getlist('file')
    year = request.form.get('year', '2026')
    
    # 연도 폴더가 없으면 생성
    year_folder = os.path.join(app.config['UPLOAD_FOLDER'], year)
    os.makedirs(year_folder, exist_ok=True)
    
    uploaded_count = 0
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # 파일명 안전하게 처리
            original_filename = secure_filename(file.filename)
            
            # 중복 방지를 위해 타임스탬프 추가
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # 마이크로초 추가
            filename = f"{timestamp}_{original_filename}"
            
            # 저장
            save_path = os.path.join(year_folder, filename)
            file.save(save_path)
            uploaded_count += 1
    
    print(f"✅ {uploaded_count}개 파일 업로드 완료!")
    return redirect(url_for('render_page', page='photo'))

# 특정 연도의 사진 목록 가져오기
@app.route('/api/photos/<year>')
def get_photos(year):
    """연도별 사진 목록 반환 (JSON)"""
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], year)
    
    # 폴더가 없으면 빈 배열 반환
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
# 삭제 기능
@app.route('/api/photos/<year>/<filename>', methods=['DELETE'])
def delete_photo(year, filename):
    """사진 삭제 API"""
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], year, safe_filename)

        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
        
        os.remove(file_path)
        print(f"파일 삭제 완료: {file_path}")

        return jsonify({'success': True, 'message': '삭제되었습니다'}), 200

    except Exception as e:
        print(f"삭제 오류: {e}")
        return jsonify({'error': '삭제 실패'}), 500
    


# 실행
if __name__ == '__main__':
    app.run(debug=True, port=3000)