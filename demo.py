import hashlib
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '123456789'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)


# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


# 文章模型
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('articles', lazy=True))
    category = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    publish_date = db.Column(db.DateTime, server_default=db.func.now())
    # 新增字段，用于存储文章封面的图片路径
    thumbnail = db.Column(db.String(200))


# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    article = db.relationship('Article', backref=db.backref('comments', lazy=True))
    publish_date = db.Column(db.DateTime, server_default=db.func.now())


# Myblog/demo.py
@app.route('/')
def index():
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('index.html', articles=articles, categories=categories, tags=tags)


@app.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    # 获取当前页码，默认为第一页
    page = request.args.get('page', 1, type=int)
    # 每页显示10条评论
    comments = Comment.query.filter_by(article_id=article_id).paginate(page=page, per_page=10)
    return render_template('article.html', article=article, comments=comments)


@app.route('/category/<category_name>')
def category(category_name):
    articles = Article.query.filter_by(category=category_name).all()
    # 获取所有分类
    all_articles = Article.query.all()
    categories = [article.category for article in all_articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in all_articles:
        if article.tags:
            tags.extend(article.tags.split(','))
    tags = list(set(tags))  # 去重
    return render_template('category.html', articles=articles, category=category_name, categories=categories, tags=tags)


@app.route('/tag/<tag_name>')
def tag(tag_name):
    articles = Article.query.filter(Article.tags.contains(tag_name)).all()
    # 获取所有分类
    all_articles = Article.query.all()
    categories = [article.category for article in all_articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in all_articles:
        if article.tags:
            tags.extend(article.tags.split(','))
    tags = list(set(tags))  # 去重
    return render_template('tag.html', articles=articles, tag=tag_name, categories=categories, tags=tags)


@app.route('/about')
def about():
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('about.html', articles=articles, categories=categories, tags=tags)


@app.route('/contact')
def contact():
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('contact.html', articles=articles, categories=categories, tags=tags)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password=hashed_password, email=email)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except:
            flash('注册失败，用户名或邮箱已存在', 'error')
            return render_template('register.html')
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('register.html', articles=articles, categories=categories, tags=tags)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(username=username, password=hashed_password).first()
        if user:
            session['user_id'] = user.id
            flash('登录成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('登录失败，用户名或密码错误', 'error')
            return render_template('login.html')
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('login.html', articles=articles, categories=categories, tags=tags)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录', 'success')
    return redirect(url_for('index'))


@app.route('/admin/article/new', methods=['GET', 'POST'])
def new_article():
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        tags = request.form['tags']
        author_id = session['user_id']

        # 处理文件上传
        thumbnail = request.files.get('thumbnail')
        if thumbnail:
            # 确保文件名安全
            filename = secure_filename(thumbnail.filename)
            # 保存文件到指定目录，这里假设保存到 static/uploads 目录下
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            thumbnail.save(file_path)
            # 生成图片的 URL
            thumbnail_url = f'/static/uploads/{filename}'
        else:
            thumbnail_url = None

        new_article = Article(title=title, content=content, author_id=author_id, category=category, tags=tags,
                              thumbnail=thumbnail_url)
        db.session.add(new_article)
        db.session.commit()
        flash('文章创建成功', 'success')
        return redirect(url_for('index'))
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('new_article.html', articles=articles, categories=categories, tags=tags)


@app.route('/admin/article/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        article.category = request.form['category']
        article.tags = request.form['tags']

        # 处理文件上传
        thumbnail = request.files.get('thumbnail')
        if thumbnail:
            # 确保文件名安全
            filename = secure_filename(thumbnail.filename)
            # 保存文件到指定目录，这里假设保存到 static/uploads 目录下
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            thumbnail.save(file_path)
            # 生成图片的 URL
            thumbnail_url = f'/static/uploads/{filename}'
            article.thumbnail = thumbnail_url

        db.session.commit()
        flash('文章编辑成功', 'success')
        return redirect(url_for('article', article_id=article_id))
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    # 将 article 变量传递给模板
    return render_template('edit_article.html', article=article, articles=articles, categories=categories, tags=tags)

@app.route('/admin/article/delete/<int:article_id>')
def delete_article(article_id):
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('文章删除成功', 'success')
    return redirect(url_for('index'))


@app.route('/article/<int:article_id>/comment', methods=['POST'])
def add_comment(article_id):
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    content = request.form['content']
    author_id = session['user_id']
    new_comment = Comment(content=content, author_id=author_id, article_id=article_id)
    db.session.add(new_comment)
    db.session.commit()
    flash('评论添加成功', 'success')
    return redirect(url_for('article', article_id=article_id))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # 验证旧密码
        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
        if user.password != hashed_old_password:
            flash('旧密码错误', 'error')
            return render_template('profile.html', user=user)

        # 验证新密码和确认密码是否一致
        if new_password != confirm_password:
            flash('新密码和确认密码不一致', 'error')
            return render_template('profile.html', user=user)

        # 更新密码
        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
        user.password = hashed_new_password
        db.session.commit()
        flash('密码修改成功', 'success')
        return render_template('profile.html', user=user)
    articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('profile.html', articles=articles, categories=categories, tags=tags)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        # 在标题和内容中搜索包含关键字的文章
        articles = Article.query.filter(
            Article.title.contains(query) | Article.content.contains(query)).all()
    else:
        articles = []
    all_articles = Article.query.all()
    # 获取所有分类
    categories = [article.category for article in all_articles if article.category]
    categories = list(set(categories))  # 去重
    # 获取所有标签
    tags = []
    for article in all_articles:
        if article.tags:
            tags.extend(article.tags.split(','))
            tags = list(set(tags))  # 去重
    return render_template('search_results.html', all_articles=all_articles, categories=categories, tags=tags, articles=articles)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
