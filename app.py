from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # нужен для сессий

VPS_IP = os.getenv("VPS_IP", "127.0.0.1")
USERNAME = os.getenv("ASIC_USER", "admin")
PASSWORD = os.getenv("ASIC_PASS", "1234")

devices = [
    {"name": "RPi1 ASIC100", "url": f"http://{VPS_IP}:18081"},
    {"name": "RPi1 ASIC101", "url": f"http://{VPS_IP}:18080"},
    {"name": "RPi2 ASIC100", "url": f"http://{VPS_IP}:28080"},
    {"name": "RPi2 ASIC101", "url": f"http://{VPS_IP}:28081"},
    {"name": "RPi2 ASIC102", "url": f"http://{VPS_IP}:28082"},
    {"name": "RPi2 ASIC104", "url": f"http://{VPS_IP}:28083"},
]

def check_online(url):
    try:
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except:
        return False

# --- Страница логина с красивым минималистичным дизайном ---
login_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - ASIC Hub</title>
<style>
:root{
  --bg: #0e0f12;
  --card: rgba(255,255,255,0.06);
  --text: #e9eef7;
  --muted: rgba(233,238,247,0.52);
  --accentA: #2a8bf2;
  --accentGrad: linear-gradient(135deg,var(--accentA),#8b5cff);
  --radius: 20px;
  --transition: 280ms cubic-bezier(.2,.9,.3,1);
}
*{box-sizing:border-box}
body{
  margin:0;
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  background:
    radial-gradient(1200px 600px at 10% 10%, rgba(42,139,242,0.06), transparent 6%),
    radial-gradient(900px 400px at 90% 90%, rgba(139,92,255,0.04), transparent 6%),
    var(--bg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color: var(--text);
}
.login-card{
  background: var(--card);
  padding: 40px 36px;
  border-radius: var(--radius);
  display:flex;
  flex-direction:column;
  gap:20px;
  min-width:320px;
  box-shadow:0 12px 28px rgba(0,0,0,0.5);
  backdrop-filter: blur(12px) saturate(150%);
  animation: fadeUp 0.32s var(--transition) both;
}
@keyframes fadeUp{
  from {opacity:0; transform:translateY(12px);}
  to {opacity:1; transform:translateY(0);}
}
h2{
  margin:0;
  font-weight:800;
  font-size:22px;
  text-align:center;
  color: var(--accentA);
}
input{
  padding:14px 16px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  color: var(--text);
  font-size:15px;
  outline:none;
  transition: box-shadow 0.2s, transform 0.2s;
}
input:focus{
  box-shadow:0 8px 20px rgba(42,139,242,0.2);
  transform: translateY(-2px);
}
button{
  padding:14px;
  border-radius:16px;
  border:none;
  background: var(--accentGrad);
  color:#fff;
  font-weight:700;
  font-size:16px;
  cursor:pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
button:hover{
  transform: translateY(-2px);
  box-shadow:0 8px 20px rgba(42,139,242,0.2);
}
.error{
  color:#ff4d4f;
  font-size:14px;
  text-align:center;
}
</style>
</head>
<body>
<div class="login-card">
  <h2>ASIC Hub Login</h2>
  {% if error %}
  <div class="error">{{ error }}</div>
  {% endif %}
  <form method="post" class="actions" style="display:flex; flex-direction:column; gap:16px;">
  <input type="text" name="username" placeholder="Username" required autofocus>
  <input type="password" name="password" placeholder="Password" required>
  <button type="submit">Войти</button>
</form>
</div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Неверный логин или пароль"
    return render_template_string(login_html, error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# --- Главная страница ---
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    for d in devices:
        d['online'] = check_online(d['url'])

    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASIC Hub</title>
<style>
:root{
  --bg: #0e0f12;
  --card: rgba(255,255,255,0.04);
  --text: #e9eef7;
  --muted: rgba(233,238,247,0.5);
  --accentA: #2a8bf2;
  --accentB: #8b5cff;
  --accentGrad: linear-gradient(135deg,var(--accentA),var(--accentB));
  --radius: 16px;
  --online: #28a745;
  --offline: #dc3545;
  --transition: 280ms cubic-bezier(.2,.9,.3,1);
}
*{box-sizing:border-box}
body{
  margin:0;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--text);
  background: var(--bg);
  display:flex;
  flex-direction:column;
  align-items:center;
  min-height:100vh;
  padding:20px;
}
h1{
  font-weight:800;
  text-align:center;
  margin-bottom:20px;
  color: var(--accentA);
}
.container{
  width:100%;
  max-width:500px;
  display:flex;
  flex-direction:column;
  gap:12px;
}
.device-link{
  display:flex;
  justify-content:space-between;
  align-items:center;
  background: var(--card);
  border-radius: var(--radius);
  padding:14px;
  text-decoration:none;
  color: var(--text);
  transition: transform var(--transition), box-shadow var(--transition);
  border:1px solid rgba(255,255,255,0.06);
}
.device-link:hover{
  transform: translateY(-2px);
  box-shadow:0 8px 24px rgba(42,139,242,0.15);
}
.device-info{
  display:flex;
  flex-direction:column;
}
.device-name{
  font-weight:700;
  font-size:15px;
}
.device-url{
  font-size:12px;
  color: var(--muted);
  word-break: break-all;
}
.status-badge{
  padding: 4px 10px;
  border-radius: 12px;
  font-size:12px;
  font-weight:700;
  color:#fff;
  white-space:nowrap;
}
.online{ background-color: var(--online); }
.offline{ background-color: var(--offline); }
.logout{
  margin-top:20px;
  text-decoration:none;
  color:var(--accentB);
  font-weight:700;
}
</style>
</head>
<body>
<h1>ASIC Hub</h1>
<div class="container">
{% for d in devices %}
<a href="{{ d.url }}" target="_blank" class="device-link">
  <div class="device-info">
    <div class="device-name">{{ d.name }}</div>
    <div class="device-url">{{ d.url }}</div>
  </div>
  <span class="status-badge {% if d.online %}online{% else %}offline{% endif %}">
    {% if d.online %}Online{% else %}Offline{% endif %}
  </span>
</a>
{% endfor %}
</div>
<a href="{{ url_for('logout') }}" class="logout">Выйти</a>
</body>
</html>
"""
    return render_template_string(html, devices=devices)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
