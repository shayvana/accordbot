import bot
from discord.ext import commands
import sqlite3
from datetime import datetime
import os

# Database setup
conn = sqlite3.connect('microblogs.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, blog_name TEXT, theme TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, content TEXT, timestamp TEXT)''')
conn.commit()

# Bot setup
intents = bot.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def create_blog(ctx, blog_name: str, theme: str = 'light'):
    user_id = ctx.author.id
    username = ctx.author.name
    theme = theme if theme in ['light', 'dark'] else 'light'
    
    c.execute('INSERT INTO users (id, username, blog_name, theme) VALUES (?, ?, ?, ?)', (user_id, username, blog_name, theme))
    conn.commit()
    
    generate_blog_page(blog_name, username, theme)
    await ctx.send(f'Blog "{blog_name}" created with {theme} theme for {username}. URL: http://accord.shayvana.com/{blog_name}')

@bot.command()
async def add_entry(ctx, title: str, *, content: str):
    user_id = ctx.author.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('INSERT INTO posts (user_id, title, content, timestamp) VALUES (?, ?, ?, ?)', (user_id, title, content, timestamp))
    conn.commit()
    
    c.execute('SELECT blog_name FROM users WHERE id = ?', (user_id,))
    blog_name = c.fetchone()[0]
    
    append_blog_entry(blog_name, title, content, timestamp)
    await ctx.send(f'New entry "{title}" added to your blog.')

@bot.command()
async def update_theme(ctx, theme: str):
    user_id = ctx.author.id
    theme = theme if theme in ['light', 'dark'] else 'light'
    
    c.execute('UPDATE users SET theme = ? WHERE id = ?', (theme, user_id))
    conn.commit()
    
    c.execute('SELECT blog_name FROM users WHERE id = ?', (user_id,))
    blog_name = c.fetchone()[0]
    
    update_blog_theme(blog_name, theme)
    await ctx.send(f'Theme updated to {theme}.')

@bot.command()
async def get_blog_url(ctx):
    user_id = ctx.author.id
    c.execute('SELECT blog_name FROM users WHERE id = ?', (user_id,))
    blog_name = c.fetchone()
    
    if blog_name:
        await ctx.send(f'Your blog URL is: http://accord.shayvana.com/{blog_name[0]}')
    else:
        await ctx.send('You do not have a blog yet. Use !create_blog to create one.')

def generate_blog_page(blog_name, username, theme):
    page_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{blog_name}</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body class="{theme}">
        <h1>{username}'s Microblog - {blog_name}</h1>
        <div id="entries"></div>
    </body>
    </html>
    '''
    file_path = f'static/{blog_name}.html'
    with open(file_path, 'w') as f:
        f.write(page_content)

def append_blog_entry(blog_name, title, content, timestamp):
    file_path = f'static/{blog_name}.html'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if '<div id="entries">' in line:
                lines.insert(i + 1, f'<div class="post"><h2>{title}</h2><p>{content}</p><p><small>{timestamp}</small></p></div>\n')
                break
        
        with open(file_path, 'w') as f:
            f.writelines(lines)

def update_blog_theme(blog_name, theme):
    file_path = f'static/{blog_name}.html'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        content = content.replace('class="light"', f'class="{theme}"').replace('class="dark"', f'class="{theme}"')
        
        with open(file_path, 'w') as f:
            f.write(content)

bot_token = os.getenv('DISCORD_BOT_TOKEN')
bot.run(bot_token)
