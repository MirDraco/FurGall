from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
@app.route('/<page>')
def render_page(page='index'):
    """동적 라우팅 - 모든 페이지를 한 번에 처리"""
    template_file = f'{page}.html'
    template_path = os.path.join('templates', template_file)
    
    if os.path.exists(template_path):
        return render_template(template_file)
    
    return "페이지를 찾을 수 없습니다!", 404

if __name__ == '__main__':
    app.run(debug=True, port=3000)