from flask import Flask, render_template_string, request
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('microblogs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/<blog_name>')
def blog(blog_name):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE blog_name = ?', (blog_name,)).fetchone()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ?', (user['id'],)).fetchall()
    conn.close()
    return render_template_string(generate_blog_template(user, posts), user=user, posts=posts)

@app.route('/<blog_name>/search')
def search(blog_name):
    query = request.args.get('q')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE blog_name = ?', (blog_name,)).fetchone()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ? AND content LIKE ?', (user['id'], f'%{query}%')).fetchall()
    conn.close()
    return render_template_string(generate_blog_template(user, posts, query), user=user, posts=posts)

def generate_blog_template(user, posts, query=None):
    entries_html = ''
    for post in posts:
        entries_html += f'<div class="post"><h2>{post["title"]}</h2><p>{post["content"]}</p><p><small>{post["timestamp"]}</small></p></div>'
    
    search_html = f'<form action="/{user["blog_name"]}/search" method="get"><input type="text" name="q" placeholder="Search..."><input type="submit" value="Search"></form>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{user["blog_name"]}</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body class="{user["theme"]}">
        <h1>{user["username"]}'s Microblog - {user["blog_name"]}</h1>
        {search_html}
        <div id="entries">{entries_html}</div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
