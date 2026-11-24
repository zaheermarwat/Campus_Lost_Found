from flask import Flask, render_template_string, request, redirect, session
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
from database import save_report, get_all_reports, search_reports, update_status, init_db
from utils import generate_report_id, validate_roll_no, get_current_date
from charts import plot_category_chart, plot_status_chart

app = Flask(__name__)
app.secret_key = "campus-lost-found-secret"
init_db()

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return img

BASE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
body{font-family:Segoe UI,sans-serif;background:#F8FAFC;margin:0;color:#0F172A}
.sidebar{background:#111827;color:white;padding:18px;min-height:100vh;width:240px;position:fixed;top:0;left:0;z-index:10}
.sidebar a{color:white;text-decoration:none;display:block;padding:12px;border-radius:10px;margin:4px 0;font-size:15px}
.sidebar a.active{background:#FF4B4B}
.sidebar a:hover{background:#374151}
.main{margin-left:240px;padding:22px;max-width:1200px;width:calc(100% - 240px)}
.card{background:white;padding:20px;border-radius:14px;border:1px solid #E2E8F0;margin-bottom:16px;overflow:hidden}
input,select,textarea{width:100%;padding:11px;border-radius:10px;border:1px solid #E2E8F0;margin:6px 0}
button{background:#FF4B4B;color:white;border:none;padding:12px 20px;border-radius:10px;font-weight:700;width:100%;cursor:pointer}
/* DASHBOARD - BEST GRID */
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}
.metric{background:white;border:1px solid #E2E8F0;border-radius:14px;padding:18px;text-align:center}
.metric small{color:#64748B;font-weight:700;letter-spacing:1px}
.metric h2{margin:6px 0 0;font-size:28px}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.charts img{width:100%;height:auto;display:block}
/* TABLE - NEVER GO OUT OF SCREEN */
.table-wrap{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid #E2E8F0;border-radius:10px}
.table-wrap table{width:100%;min-width:650px;border-collapse:collapse;background:white}
th,td{padding:10px;border-bottom:1px solid #E2E8F0;text-align:left;font-size:14px;white-space:nowrap}
th{background:#F8FAFC}
.msg{background:#DCFCE7;padding:12px;border-radius:10px;margin:10px 0}
.err{background:#FEE2E2;padding:12px;border-radius:10px;margin:10px 0}
/* LAPTOP */
@media(max-width:1000px){.charts{grid-template-columns:1fr}}
/* MOBILE - BEST VIEW */
@media(max-width:700px){
.sidebar{position:relative;width:100%;min-height:auto;padding:14px}
.sidebar h2{margin:0 0 8px}
.sidebar a{display:inline-block;padding:9px 12px;margin:2px;font-size:13px}
.main{margin:0;width:100%;padding:14px}
.metrics{grid-template-columns:1fr 1fr;gap:10px}
.metric{padding:14px}
.metric h2{font-size:22px}
.card{padding:14px}
.charts{grid-template-columns:1fr}
.table-wrap table{min-width:600px}
}
</style></head><body>
{% if session.get('user_name') %}
<div class="sidebar"><h2>🎒 Lost & Found</h2><p style="color:#9CA3AF;margin:4px 0 12px">Campus Portal</p>
<div style="background:#1F2937;padding:12px;border-radius:12px;margin-bottom:12px">👋 {{session['user_name']}}<br><small>Roll: {{session['user_roll']}}</small></div>
<a href="/" class="{{'active' if page=='dash' else ''}}">📊 Dashboard</a>
<a href="/report" class="{{'active' if page=='report' else ''}}">📝 Report Item</a>
<a href="/lost" class="{{'active' if page=='lost' else ''}}">📝 Report Lost Item</a>
<a href="/found" class="{{'active' if page=='found' else ''}}">✅ Report Found Item</a>
<a href="/search" class="{{'active' if page=='search' else ''}}">🔍 Search & Claim</a>
<a href="/logout">🚪 Logout</a></div><div class="main">{{content|safe}}</div>
{% else %}<div style="max-width:480px;margin:40px auto;padding:20px">{{content|safe}}</div>{% endif %}
</body></html>
"""

def render(page, content):
    return render_template_string(BASE, page=page, content=content)

@app.route("/", methods=["GET","POST"])
def index():
    if "user_name" not in session:
        msg=""
        if request.method=="POST":
            name=request.form.get("name",""); roll=request.form.get("roll","")
            if validate_roll_no(name, roll):
                session["user_name"]=name.strip(); session["user_roll"]=roll.strip().upper()
                return redirect("/")
            else: msg="<div class='err'>Please enter both Name and Roll No.</div>"
        c=f"""<div style="text-align:center"><h1 style="font-size:42px">🎒 Campus Lost & Found</h1><p style="color:#64748B">Lost something? Found something? Report it here in 30 seconds.</p></div>
        <div class="card" style="text-align:center"><div style="font-size:50px">🔐</div><h3>Student Login</h3><p style="color:#64748B">No password needed.</p>{msg}
        <form method="post"><input name="name" placeholder="e.g. Ahmad Ali"><input name="roll" placeholder="e.g. CS-2023-045"><button>Login →</button></form>
        <p>💡 Example: Ahmad Ali, CS-2023-045</p></div>"""
        return render("login", c)
    df=get_all_reports()
    total=len(df); lost=len(df[df["type"]=="Lost"]) if total else 0; found=len(df[df["type"]=="Found"]) if total else 0; claimed=len(df[df["status"]=="Claimed"]) if total else 0
    charts=""
    if total>0:
        img1=fig_to_base64(plot_category_chart(df)); img2=fig_to_base64(plot_status_chart(df))
        table_html=df.tail(5).sort_values("report_id",ascending=False).to_html(index=False)
        charts=f"""<div class="charts"><div class="card"><h3>Items by Category</h3><img src="data:image/png;base64,{img1}"></div>
        <div class="card"><h3>Lost vs Found vs Claimed</h3><img src="data:image/png;base64,{img2}"></div></div>
        <div class="card"><h3>🕒 Recent 5 Reports</h3><p style="color:#64748B;font-size:13px">↔ Swipe table left / right on mobile</p><div class="table-wrap">{table_html}</div></div>"""
    else:
        charts="""<div class="card"><h3>👋 How it works?</h3><p><b>1.</b> Lost? Go to Report Lost Item<br><b>2.</b> Found? Go to Report Found Item<br><b>3.</b> Search in Search & Claim to claim it.</p></div>"""
    c=f"""<h2>📊 Dashboard</h2><p>Welcome back, <b>{session['user_name']}</b>!</p>
    <div class="metrics"><div class="metric"><small>TOTAL</small><h2>{total}</h2></div><div class="metric"><small>LOST</small><h2>{lost}</h2></div><div class="metric"><small>FOUND</small><h2>{found}</h2></div><div class="metric"><small>CLAIMED</small><h2>{claimed}</h2></div></div>{charts}"""
    return render("dash", c)

def report_form(kind):
    msg=""
    if request.method=="POST":
        item=request.form.get("item","").strip(); loc=request.form.get("location","").strip()
        if not item or not loc: msg="<div class='err'>Please fill Item Name and Location.</div>"
        else:
            rid=generate_report_id()
            save_report(report_id=rid, reporter_name=session["user_name"], roll_no=session["user_roll"], item_name=item, category=request.form.get("category"), type=kind, location=loc, date=request.form.get("date"), description=request.form.get("description","").strip(), contact=request.form.get("contact","").strip(), status="Open")
            msg=f"<div class='msg'>✅ {kind} Report Saved! Your Report ID is <b>{rid}</b>. Keep it safe.</div>"
    title="Report Lost Item" if kind=="Lost" else "Report Found Item"
    emoji="📝" if kind=="Lost" else "✅"
    cats="".join([f"<option>{c}</option>" for c in ["Wallet","Phone","ID Card","Keys","Bag","Laptop","Book","Other"]])
    c=f"""<h2>{emoji} {title}</h2><div class="card">{msg}<form method="post">
    <input name="item" placeholder="e.g. Black Wallet" required><select name="category">{cats}</select>
    <input name="location" placeholder="e.g. Main Canteen, Library" required>
    <input type="date" name="date" value="{get_current_date()}">
    <textarea name="description" placeholder="Color, Brand, etc."></textarea>
    <input name="contact" placeholder="e.g. 0300-1234567"><button>Submit {kind} Report →</button></form></div>
    <p><a href="/">← Back to Dashboard</a></p>"""
    return render("lost" if kind=="Lost" else "found", c)

@app.route("/report")
def report():
    if "user_name" not in session: return redirect("/")
    c="""<h2>📝 Report Item</h2><div class="card" style="text-align:center"><p>Did you LOSE something or FIND something?</p><p><a href="/lost" style="display:inline-block;background:#FF4B4B;color:white;text-decoration:none;padding:14px 20px;border-radius:12px;font-weight:700;margin:5px">📝 I LOST Something</a><a href="/found" style="display:inline-block;background:#22C55E;color:white;text-decoration:none;padding:14px 20px;border-radius:12px;font-weight:700;margin:5px">✅ I FOUND Something</a></p></div>"""
    return render("report", c)

@app.route("/lost", methods=["GET","POST"])
def lost():
    if "user_name" not in session: return redirect("/")
    return report_form("Lost")

@app.route("/found", methods=["GET","POST"])
def found():
    if "user_name" not in session: return redirect("/")
    return report_form("Found")

@app.route("/search", methods=["GET","POST"])
def search():
    if "user_name" not in session: return redirect("/")
    df=get_all_reports(); msg=""
    keyword=request.form.get("keyword","") if request.method=="POST" else request.args.get("keyword","")
    ftype=request.form.get("filter","All") if request.method=="POST" else request.args.get("filter","All")
    claim=request.form.get("claim_id","").strip()
    if request.method=="POST" and claim:
        ok=update_status(claim.upper(),"Claimed")
        msg=f"<div class='msg'>Item {claim.upper()} marked as Claimed!</div>" if ok else "<div class='err'>Report ID not found.</div>"
    results=search_reports(keyword.strip()) if keyword.strip() else df
    if ftype in ["Lost","Found"]: results=results[results["type"]==ftype]
    elif ftype in ["Open","Claimed"]: results=results[results["status"]==ftype]
    table=results.to_html(index=False) if len(results)>0 else "<p>No matching items found.</p>"
    c=f"""<h2>🔍 Search & Claim</h2>{msg}<div class="card"><form method="post">
    <input name="keyword" placeholder="e.g. Wallet, Library, iPhone" value="{keyword}">
    <select name="filter"><option {'selected' if ftype=='All' else ''}>All</option><option {'selected' if ftype=='Lost' else ''}>Lost</option><option {'selected' if ftype=='Found' else ''}>Found</option><option {'selected' if ftype=='Open' else ''}>Open</option><option {'selected' if ftype=='Claimed' else ''}>Claimed</option></select>
    <button>Search</button></form></div>
    <div class="card"><p>Found <b>{len(results)}</b> item(s) — ↔ Swipe table on mobile</p><div class="table-wrap">{table}</div></div>
    <div class="card"><h3>🎯 Claim an Item</h3><form method="post"><input name="claim_id" placeholder="LF-001"><button>Claim This Item</button></form></div>"""
    return render("search", c)

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
