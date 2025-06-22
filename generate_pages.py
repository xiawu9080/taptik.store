import csv
import os
import random
from datetime import datetime

# 基础站点 URL（用于 sitemap）
BASE_URL = "https://taptik.store"

# ----------- 分类推断函数 -----------
def infer_category(title, description=""):
    """根据游戏标题和描述推断分类"""
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # 模拟类游戏
    simulation_keywords = ['cleaning', 'cooking', 'dress', 'makeup', 'beauty', 'house', 'home', 'simulator', 'factory']
    if any(keyword in title_lower for keyword in simulation_keywords):
        return "simulation"
    
    # 换装类游戏
    dress_up_keywords = ['dress', 'fashion', 'style', 'outfit', 'clothes', 'makeup', 'beauty']
    if any(keyword in title_lower for keyword in dress_up_keywords):
        return "dress-up"
    
    # 解谜类游戏
    puzzle_keywords = ['puzzle', 'block', 'match', 'connect', 'word', 'search', 'hexa', 'gummy']
    if any(keyword in title_lower for keyword in puzzle_keywords):
        return "puzzle"
    
    # 默认分类
    return "simulation"

# ----------- 模板定义区 -----------

# 游戏推荐卡片模板
recommend_card = """
<div class="card" onclick="location.href='{filename}'">
  <img src="{thumbnail}" alt="{title}" />
  <h4>{title}</h4>
</div>
"""

# 单个游戏页面 HTML 模板
game_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title} | Taptik Store</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="Play {title} and other free online games on Taptik Store. No downloads, just fun." />
  <link rel="stylesheet" href="game-page.css">
</head>
<body>
  <a href="index.html" class="back-button">&larr; Back to Home</a>

  <h1 class="game-title">{title}</h1>

  <div class="game-container">
    <iframe src="{url}" allowfullscreen></iframe>
  </div>

  <div class="details-section">
    <div class="info-card">
        <h2>Game Description</h2>
        <p>{description}</p>
    </div>
    <div class="info-card">
        <h2>How to Play</h2>
        <p>Follow the in-game instructions to play. Typically uses mouse, keyboard, or touch controls.</p>
    </div>
    <div class="info-card">
        <h2>Rating</h2>
        <div class="rating">
            {rating_stars}
            ({rating} / 5)
        </div>
    </div>
  </div>

  <div class="recommendations">
    <h2>You Might Also Like</h2>
    <div class="recommend-grid">
      {recommend_cards}
    </div>
  </div>
</body>
</html>
"""

# 首页游戏卡片模板
card_template = """
<div class="game-card" data-category="auto">
  <a href="{filename}">
    <img class="game-thumb" src="{thumbnail}" alt="{title} Thumbnail">
    <div class="game-title">{title}</div>
  </a>
</div>
"""


# ----------- 数据读取与页面生成 -----------

cards_html = ""
games_data = []

with open("games.csv",newline='',encoding='latin1') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        games_data.append(row)

# 存放 sitemap 中的页面 URL 项
sitemap_entries = []

# 遍历每个游戏数据生成独立页面
for current_game in games_data:
    current_id = current_game['id']
    title = current_game['title']
    url = current_game['url']
    description = current_game['description']
    rating = current_game['rating']
    thumbnail = current_game['thumbnail']
    filename = f"{current_id}.html"

    # 生成评分星星
    rating_float = float(rating)
    stars_filled = '★' * int(rating_float)
    stars_empty = '☆' * (5 - int(rating_float))
    rating_stars = f'<span class="stars">{stars_filled}</span>{stars_empty}'

    # 推荐其他游戏（排除自己）
    other_games = [g for g in games_data if g['id'] != current_id]
    recommended = random.sample(other_games, min(3, len(other_games)))
    recommend_cards = ""
    for g in recommended:
        recommend_cards += f"""
        <a href="{g['id']}.html" class="recommend-card">
          <img src="{g['thumbnail']}" alt="{g['title']}" />
          <div class="title">{g['title']}</div>
        </a>"""

    # 写入每个游戏的 HTML 页面
    with open(filename, "w", encoding="utf-8") as f:
        f.write(game_template.format(
            title=title,
            url=url,
            description=description,
            rating=rating,
            rating_stars=rating_stars,
            recommend_cards=recommend_cards
        ))

    # 首页卡片拼接
    category = infer_category(title, description)
    cards_html += card_template.format(filename=filename, thumbnail=thumbnail, title=title, category=category)

    # 添加 sitemap 条目
    sitemap_entries.append(f"""
  <url>
    <loc>{BASE_URL}/{filename}</loc>
    <priority>0.8</priority>
    <changefreq>weekly</changefreq>
    <lastmod>{datetime.utcnow().date()}</lastmod>
  </url>""")

# ----------- 生成首页 HTML -----------

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Game Portal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h1>🎮 HTML5 Game Portal</h1>
  <div class="grid">
    {cards_html}
  </div>
</body>
</html>
"""

# 写入首页文件
# 1. 读取原始 index.html
with open("index.html", "r", encoding="utf-8") as f:
    index_content = f.read()

# 2. 替换插入区（标记处）
new_index = index_content.replace(
    "<!-- GAME_CARD_INSERT -->",
    cards_html + "\n<!-- GAME_CARD_INSERT -->"
)

# 3. 写回 index.html（保留其它内容）
with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_index)

# ----------- 生成 sitemap.xml -----------

sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- 自动生成的站点地图 -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <!-- 首页 -->
  <url>
    <loc>{BASE_URL}/</loc>
    <priority>1.0</priority>
    <changefreq>daily</changefreq>
    <lastmod>{datetime.utcnow().date()}</lastmod>
  </url>
  {''.join(sitemap_entries)}
</urlset>
"""

# 写入 sitemap.xml 文件
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print("✅ 所有页面已生成，并自动创建 sitemap.xml")
