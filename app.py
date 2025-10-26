import os
import shutil
import sys
import platform
import psutil
from pathlib import Path
from datetime import datetime

from flask import Flask, request, send_file, redirect, url_for, render_template_string, session, abort

# =============== CONFIG ===============
STORAGE_DIR = Path("cloudfiles_storage").resolve()
STORAGE_DIR.mkdir(exist_ok=True)

# ============ LOGIN CREDENTIALS =====================
VALID_USERNAME = "changeme"
VALID_PASSWORD = "CHANGEME"
# ====================================================

app = Flask(__name__)
app.secret_key = "CloudFiles-10/26/25-2:53PM"

# =============== HELPERS ===============
def ensure_logged_in():
    if not session.get('logged_in'):
        return abort(403)

def resolve_path(path_str):
    if not path_str:
        return STORAGE_DIR
    path_str = path_str.replace('\\', '/').lstrip('/')
    target = (STORAGE_DIR / path_str).resolve()
    if not str(target).startswith(str(STORAGE_DIR)):
        abort(403)
    return target

def get_relative_path(full_path):
    try:
        return full_path.relative_to(STORAGE_DIR).as_posix()
    except ValueError:
        return ""

def get_items(path):
    items = []
    try:
        for p in sorted(path.iterdir()):
            stat = p.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d, %Y · %H:%M")
            items.append({
                'name': p.name,
                'is_dir': p.is_dir(),
                'timestamp': timestamp,
                'size': stat.st_size if not p.is_dir() else None
            })
    except Exception:
        pass
    return items

# =============== TEMPLATES ===============
def base_template(content, current_path_name="Home", show_fab=True):
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudFiles.lol</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --bg: #0a0a12;
            --surface: rgba(18, 18, 32, 0.88);
            --surface-solid: #121220;
            --text: #f5f5ff;
            --text-secondary: #c0c0e6;
            --accent: #a0c0ff;
            --accent-hover: #8ab0ff;
            --success: #b0ffb0;
            --warning: #ffd199;
            --error: #ff99aa;
            --border-radius: 22px;
            --shadow: 0 12px 50px rgba(0, 0, 0, 0.5);
            --transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            padding: 20px 16px;
            min-height: 100vh;
            background: 
                radial-gradient(circle at 20% 25%, rgba(160, 192, 255, 0.12) 0%, transparent 35%),
                radial-gradient(circle at 80% 75%, rgba(176, 255, 176, 0.12) 0%, transparent 35%),
                linear-gradient(135deg, #0a0a12 0%, #10101c 100%);
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 1px solid rgba(160, 192, 255, 0.3);
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(120deg, #a0c0ff, #d0a0ff, #a0ffc0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            background-size: 300% 300%;
            animation: gradientShift 8s ease infinite;
        }}

        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .path-bar {{
            background: var(--surface);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: var(--border-radius);
            padding: 18px 26px;
            margin: 26px 0;
            font-size: 1.2rem;
            border: 1px solid rgba(160, 192, 255, 0.25);
            box-shadow: var(--shadow);
            word-break: break-all;
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 26px;
            margin: 26px 0;
        }}

        .item {{
            background: var(--surface);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: var(--border-radius);
            padding: 24px;
            cursor: pointer;
            transition: var(--transition);
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: var(--shadow);
            display: flex;
            gap: 20px;
            align-items: flex-start;
            position: relative;
            overflow: hidden;
        }}

        .item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, var(--accent), #d0a0ff);
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .item:hover {{
            transform: translateY(-6px);
            border-color: rgba(160, 192, 255, 0.45);
            box-shadow: 0 16px 60px rgba(0, 0, 0, 0.55);
        }}

        .item:hover::before {{
            opacity: 1;
        }}

        .item-icon {{
            font-size: 2.2rem;
            width: 44px;
            text-align: center;
        }}

        .item-info {{
            flex: 1;
            min-width: 0;
        }}

        .item-name {{
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 1.1rem;
            word-break: break-word;
        }}

        .item-meta {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .btn {{
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: #0a0a12;
            border: none;
            padding: 14px 28px;
            border-radius: 50px;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            font-size: 1.08rem;
            box-shadow: 0 7px 28px rgba(160, 192, 255, 0.45);
        }}

        .btn:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 35px rgba(160, 192, 255, 0.55);
        }}

        .btn-outline {{
            background: transparent;
            border: 2px solid var(--accent);
            color: var(--accent);
            box-shadow: none;
        }}

        .btn-outline:hover {{
            background: rgba(160, 192, 255, 0.12);
        }}

        .actions-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 30px 0;
            justify-content: center;
        }}

        .upload-area {{
            background: var(--surface);
            border: 2px dashed rgba(160, 192, 255, 0.4);
            border-radius: var(--border-radius);
            padding: 32px;
            text-align: center;
            cursor: pointer;
            transition: var(--transition);
            flex: 1;
            min-width: 240px;
            position: relative;
        }}

        .upload-area:hover {{
            border-color: var(--accent);
            background: rgba(160, 192, 255, 0.1);
        }}

        .fab {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: #0a0a12;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.7rem;
            box-shadow: 0 10px 30px rgba(160, 192, 255, 0.65);
            cursor: pointer;
            z-index: 100;
            transition: var(--transition);
        }}

        .fab:hover {{
            transform: scale(1.15) rotate(150deg);
        }}

        .modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(10, 10, 18, 0.94);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease;
        }}

        .modal.active {{
            opacity: 1;
            pointer-events: all;
        }}

        .modal-content {{
            background: var(--surface-solid);
            border-radius: 28px;
            padding: 36px;
            width: 94%;
            max-width: 540px;
            transform: translateY(30px);
            transition: transform 0.4s ease;
        }}

        .modal.active .modal-content {{
            transform: translateY(0);
        }}

        input, textarea {{
            width: 100%;
            padding: 16px;
            margin: 16px 0;
            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(8, 8, 16, 0.8);
            color: var(--text);
            font-size: 1.05rem;
        }}

        textarea {{
            min-height: 240px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 1.02rem;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 24px;
            color: var(--text-secondary);
            font-size: 1.05rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* Status Page */
        .metric-card {{
            background: var(--surface);
            backdrop-filter: blur(16px);
            border-radius: var(--border-radius);
            padding: 28px;
            margin: 26px 0;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }}

        .metric-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 16px;
            font-weight: 700;
            font-size: 1.15rem;
        }}

        .progress-bar {{
            height: 16px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent), #d0a0ff);
            border-radius: 8px;
            transition: width 0.7s ease;
        }}

        .specs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 24px;
            margin-top: 24px;
        }}

        .spec-item {{
            background: rgba(18, 18, 32, 0.7);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
        }}

        .spec-value {{
            font-weight: 700;
            margin-top: 12px;
            color: var(--accent);
            word-break: break-word;
            font-size: 1rem;
        }}

        /* Login Page */
        .login-container {{
            max-width: 480px;
            margin: 80px auto;
            text-align: center;
        }}

        .login-card {{
            background: var(--surface);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 28px;
            padding: 40px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(160, 192, 255, 0.3);
        }}

        .login-logo {{
            font-size: 2.5rem;
            margin-bottom: 20px;
            background: linear-gradient(120deg, #a0c0ff, #d0a0ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .login-input {{
            width: 100%;
            padding: 18px;
            margin: 18px 0;
            border-radius: 18px;
            border: 1px solid rgba(160, 192, 255, 0.3);
            background: rgba(8, 8, 16, 0.85);
            color: var(--text);
            font-size: 1.1rem;
        }}

        .login-btn {{
            width: 100%;
            padding: 16px;
            font-size: 1.2rem;
            margin-top: 10px;
        }}

        /* Responsive */
        @media (max-width: 700px) {{
            .items-grid {{
                grid-template-columns: 1fr;
            }}
            header {{
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }}
            .actions-bar {{
                flex-direction: column;
            }}
            .btn {{
                width: 100%;
                justify-content: center;
            }}
            .logo {{
                font-size: 1.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    
    {"<div class='fab' onclick='showActionMenu()'><i class='fas fa-plus'></i></div>" if show_fab else ""}
    
    <div id="actionModal" class="modal">
        <div class="modal-content">
            <h3 style="margin-bottom:24px; color:var(--accent); text-align:center; font-size:1.5rem;">
                <i class="fas fa-sparkles"></i> Create New Item
            </h3>
            <button class="btn" style="width:100%; margin:12px 0;" onclick="createItem('folder')">
                <i class="fas fa-folder-plus"></i> New Folder
            </button>
            <button class="btn" style="width:100%; margin:12px 0;" onclick="createItem('file')">
                <i class="fas fa-file-code"></i> New Text File
            </button>
            <button class="btn btn-outline" style="width:100%; margin-top:24px;" onclick="closeModal()">
                <i class="fas fa-times"></i> Cancel
            </button>
        </div>
    </div>

    <script>
        function showActionMenu() {{
            document.getElementById('actionModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('actionModal').classList.remove('active');
        }}

        function createItem(type) {{
            closeModal();
            const name = prompt(type === 'folder' ? 'Enter folder name:' : 'Enter file name (e.g. notes.txt):');
            if (!name) return;
            
            const path = "{get_relative_path(Path(current_path_name)) if 'current_path_name' in globals() else ''}";
            const url = type === 'folder' 
                ? "/create-folder" + (path ? "?path=" + encodeURIComponent(path) : "") 
                : "/create-file" + (path ? "?path=" + encodeURIComponent(path) : "");
            
            if (type === 'file') {{
                const content = prompt("Optional content (leave blank for empty):") || "";
                fetch(url, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
                    body: "name=" + encodeURIComponent(name) + "&content=" + encodeURIComponent(content)
                }}).then(() => window.location.reload());
            }} else {{
                fetch(url, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
                    body: "name=" + encodeURIComponent(name)
                }}).then(() => window.location.reload());
            }}
        }}

        function deleteItem(path) {{
            if (!confirm("⚠️ Delete permanently? This cannot be undone.")) return;
            fetch("/delete?path=" + encodeURIComponent(path), {{ method: "POST" }})
                .then(() => window.location.reload());
        }}

        document.getElementById('actionModal')?.addEventListener('click', (e) => {{
            if (e.target === document.getElementById('actionModal')) {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>
    '''

def render_login(error=False):
    error_js = '<script>document.querySelectorAll(".login-input")[0].style.borderColor="#ff6677";</script>' if error else ''
    content = f'''
    <div class="login-container">
        <div class="login-card">
            <div class="login-logo">
                <i class="fas fa-cloud"></i> CloudFiles.lol
            </div>
            <p style="color:var(--text-secondary); margin:20px 0;">The Best Open Sourced Cloud On Python</p>
            <form method="POST">
                <input type="text" name="username" class="login-input" placeholder="Username" autocomplete="username" required>
                <input type="password" name="password" class="login-input" placeholder="Password" autocomplete="current-password" required>
                <button type="submit" class="btn login-btn">
                    <i class="fas fa-lock-open"></i> Login
                </button>
            </form>
            <div style="margin-top:25px; color:var(--text-secondary); font-size:0.95rem;">
                💡 By: <strong>The Great SYZDARK</strong> | <strong>CloudFiles OpenSoured On Github.</strong>
            </div>
        </div>
    </div>
    {error_js}
    '''
    return base_template(content, show_fab=False)

def render_main(current_path, items, rel_path=""):
    path_display = "Home" if current_path == STORAGE_DIR else current_path.relative_to(STORAGE_DIR).as_posix()
    
    items_html = ""
    if current_path != STORAGE_DIR:
        parent_path = get_relative_path(current_path.parent)
        items_html += f'''
        <div class="item" onclick="location.href='{url_for("browse", path=parent_path)}'">
            <div class="item-icon">📁</div>
            <div class="item-info">
                <div class="item-name">.. (Parent Directory)</div>
            </div>
        </div>
        '''
    
    for item in items:
        item_rel = (rel_path + '/' + item['name']).lstrip('/') if rel_path else item['name']
        icon = "📁" if item['is_dir'] else "📄"
        size_info = f" · {item['size']} bytes" if item['size'] is not None else ""
        
        click_action = f"window.location.href='{url_for('edit', path=item_rel)}'" if not item['is_dir'] else f"location.href='{url_for('browse', path=item_rel)}'"
        
        items_html += f'''
        <div class="item" onclick="{click_action}">
            <div class="item-icon">{icon}</div>
            <div class="item-info">
                <div class="item-name">{item['name']}</div>
                <div class="item-meta">
                    <span>{item['timestamp']}</span>
                    <span>{size_info}</span>
                </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px; align-items:flex-end;">
                {'<a href="' + url_for("download", path=item_rel) + '" class="btn" style="padding:10px; border-radius:16px; font-size:0.9rem; width:44px; height:44px; justify-content:center; background:#8affb0;">⬇️</a>' if not item['is_dir'] else ''}
                <button class="btn" style="padding:10px; border-radius:16px; font-size:0.9rem; width:44px; height:44px; justify-content:center; background:#ff6677;" 
                        onclick="event.stopPropagation(); deleteItem('{item_rel}')">🗑️</button>
            </div>
        </div>
        '''
    
    upload_action = url_for('upload')
    if rel_path:
        upload_action += f"?path={rel_path}"
    
    content = f'''
    <header>
        <div class="logo">
            <i class="fas fa-cloud"></i>
            CloudFiles.lol
        </div>
        <a href="{url_for('status')}" class="btn" style="padding:12px 22px; font-size:1.05rem;">
            <i class="fas fa-chart-line"></i> Status
        </a>
    </header>
    
    <div class="path-bar">
        <i class="fas fa-folder-tree"></i> {path_display}
    </div>
    
    <div class="actions-bar">
        <form method="POST" enctype="multipart/form-data" action="{upload_action}" style="flex:1; min-width:250px;">
            <div class="upload-area">
                <i class="fas fa-cloud-upload-alt" style="font-size:2.4rem; margin-bottom:16px; color:var(--accent);"></i>
                <div><strong>📤 Upload Files</strong></div>
                <div style="font-size:0.95rem; color:var(--text-secondary); margin-top:10px;">Click to select</div>
                <input type="file" name="files" multiple onchange="this.form.submit()" 
                       style="position:absolute; opacity:0; width:100%; height:100%; top:0; left:0; cursor:pointer;">
            </div>
        </form>
        
        {f'<a href="{url_for("browse", path=get_relative_path(current_path.parent))}" class="btn" style="background:var(--warning);">'
          f'<i class="fas fa-arrow-up"></i> Go Up</a>' if current_path != STORAGE_DIR else ''}
    </div>
    
    <div class="items-grid">
        {items_html}
    </div>
    
    <footer>
        🌐 CloudFiles.lol • The Best OpenSourced CloudStorage On Python •
    </footer>
    '''
    return base_template(content, str(current_path))

def render_editor(file_path, content, rel_path):
    content_html = f'''
    <header>
        <div class="logo">
            <i class="fas fa-edit"></i>
            Editing: {file_path.name}
        </div>
        <a href="{url_for('browse', path=rel_path)}" class="btn" style="background:var(--warning);">
            <i class="fas fa-arrow-left"></i> Back
        </a>
    </header>
    
    <form method="POST">
        <textarea name="content" spellcheck="false">{content}</textarea>
        <button class="btn" type="submit" style="width:100%; margin:26px 0; font-size:1.15rem;">
            <i class="fas fa-save"></i> Save Changes
        </button>
    </form>
    '''
    return base_template(content_html, show_fab=False)

def render_status():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage(STORAGE_DIR.anchor)
    
    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)
    disk_used = disk.used / (1024**3)
    disk_total = disk.total / (1024**3)
    
    specs = {
        "Operating System": f"{platform.system()} {platform.release()}",
        "Architecture": platform.machine(),
        "Processor": platform.processor() or "Unknown",
        "Python Version": sys.version.split()[0],
        "Storage Path": str(STORAGE_DIR),
    }

    content = f'''
    <header>
        <div class="logo">
            <i class="fas fa-server"></i>
            System Dashboard
        </div>
        <a href="{url_for('browse')}" class="btn">
            <i class="fas fa-cloud"></i> Files
        </a>
    </header>
    
    <div class="metric-card">
        <div class="metric-header">
            <span>🖥️ CPU Usage</span>
            <span>{cpu:.1f}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {min(cpu, 100)}%"></div>
        </div>
    </div>
    
    <div class="metric-card">
        <div class="metric-header">
            <span>🧠 RAM</span>
            <span>{ram_used:.1f} GB / {ram_total:.1f} GB ({ram.percent}%)</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {ram.percent}%"></div>
        </div>
    </div>
    
    <div class="metric-card">
        <div class="metric-header">
            <span>💾 Disk</span>
            <span>{disk_used:.1f} GB / {disk_total:.1f} GB ({disk.percent}%)</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {disk.percent}%"></div>
        </div>
    </div>
    
    <div class="metric-card">
        <div class="metric-header">⚙️ System Info</div>
        <div class="specs-grid">
            {''.join(f'<div class="spec-item"><div>{k}</div><div class="spec-value">{v}</div></div>' for k, v in specs.items())}
        </div>
    </div>
    
    <footer>
        💫 Live metrics • Refresh to update • All data from your server
    </footer>
    '''
    return base_template(content, show_fab=False)

# =============== ROUTES ===============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('browse'))
        return render_login(error=True)
    return render_login()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('browse'))

@app.route('/browse')
def browse():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    current_path = resolve_path(path_str)
    
    if current_path.is_file():
        return redirect(url_for('edit', path=get_relative_path(current_path)))
        
    items = get_items(current_path)
    rel_path = get_relative_path(current_path)
    return render_main(current_path, items, rel_path)

@app.route('/upload', methods=['POST'])
def upload():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    target_dir = resolve_path(path_str)
    if not target_dir.is_dir():
        abort(400)
    
    files = request.files.getlist('files')
    for file in files:
        if file.filename:
            safe_name = os.path.basename(file.filename)
            (target_dir / safe_name).write_bytes(file.read())
    return redirect(url_for('browse', path=path_str))

@app.route('/create-folder', methods=['POST'])
def create_folder():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    target_dir = resolve_path(path_str)
    name = request.form.get('name', '').strip()
    if name:
        (target_dir / name).mkdir(exist_ok=True)
    return redirect(url_for('browse', path=path_str))

@app.route('/create-file', methods=['POST'])
def create_file():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    target_dir = resolve_path(path_str)
    name = request.form.get('name', '').strip()
    content = request.form.get('content', '')
    if name:
        (target_dir / name).write_text(content, encoding='utf-8')
    return redirect(url_for('browse', path=path_str))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    file_path = resolve_path(path_str)
    rel_path = get_relative_path(file_path.parent)
    
    if request.method == 'POST':
        file_path.write_text(request.form.get('content', ''), encoding='utf-8')
        return redirect(url_for('browse', path=rel_path))
    
    content = file_path.read_text(encoding='utf-8') if file_path.exists() else ""
    return render_editor(file_path, content, rel_path)

@app.route('/download')
def download():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    file_path = resolve_path(path_str)
    if not file_path.is_file():
        abort(404)
    return send_file(file_path, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete():
    ensure_logged_in()
    path_str = request.args.get('path', '').strip('/')
    target = resolve_path(path_str)
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    return '', 204

@app.route('/status')
def status():
    ensure_logged_in()
    return render_status()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# =============== RUN ===============
if __name__ == '__main__':
    print(f"🚀 CloudFiles.lol starting...")
    print(f"📁 Storage: {STORAGE_DIR}")
    print(f"🌐 Access at: https://cloud.pc-remoto.tk")
    print(f"🚨 CloudFiles Has Successfully Started")
    print(f"🟩 Running Python Version 3.12.12")
    app.run(host='0.0.0.0', port=808-, debug=True)
