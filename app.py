from flask import Flask, request, redirect, render_template_string, session
import json, os
from datetime import datetime
from core.wallet import get_balance

app = Flask(__name__)
app.secret_key = "secret123"

FILE = "data/airdrops.json"

USER = "alwantra"
PASS = "alwantra"

# ================= LOGIN =================
def is_login():
    return "user" in session

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["u"] == USER and request.form["p"] == PASS:
            session["user"] = USER
            return redirect("/")

    return """
    <style>
    body{background:#0d1117;color:#0f0;font-family:monospace;text-align:center}
    input,button{padding:10px;margin:5px;background:#111;color:#0f0;border:1px solid #0f0}
    </style>

    <h1>🔐 LOGIN</h1>
    <form method=post>
    <input name=u placeholder=username><br>
    <input name=p type=password placeholder=password><br>
    <button>Login</button>
    </form>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= DATA =================
def load():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))

def save(data):
    json.dump(data, open(FILE, "w"), indent=4)

# ================= DASHBOARD =================
@app.route("/")
def home():
    if not is_login():
        return redirect("/login")

    data = load()

    # ================= SEARCH =================
    keyword = request.args.get("q", "").lower()

    if keyword:
        data = [
            a for a in data
            if keyword in a["name"].lower()
            or keyword in a["type"].lower()
            or keyword in a["network"].lower()
            or keyword in a["chain"].lower()
            or keyword in a["wallet"].lower()
            or keyword in a["status"].lower()
            or keyword in a["note"].lower()
        ]

    # ================= STATS =================
    total = len(data)
    done = sum(1 for a in data if a["status"] == "done")
    total_usd = 0

    for a in data:
        bal, usd = get_balance(a["chain"], a["wallet"])
        a["balance"] = bal
        a["usd"] = usd
        total_usd += usd

    html = """
    <style>
    body{background:#0d1117;color:#0f0;font-family:monospace}
    .container{width:90%;margin:auto}
    .card{border:1px solid #0f0;padding:15px;margin:10px;background:#111;border-radius:10px}
    .top{display:flex;justify-content:space-between;align-items:center}
    .btn{padding:5px 10px;border:1px solid #0f0;margin:5px;display:inline-block}
    .btn:hover{background:#0f0;color:#000}
    .stats{display:flex;gap:20px;margin:20px}
    .box{border:1px solid #0f0;padding:10px;border-radius:10px}
    a{color:#0ff;text-decoration:none}
    input{padding:6px;background:#111;color:#0f0;border:1px solid #0f0}
    </style>

    <h1>🚀 AIRDROP DASHBOARD ALWANTRA</h1>

    <div class='container'>

    <div class='top'>
        <div>
        <a href='/'>All</a>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">

            <!-- SEARCH -->
            <form method="get" action="/">
                <input type="text" name="q" placeholder="search..."
                       value="{{request.args.get('q','')}}">
            </form>

            <!-- MENU -->
            <a href='/add'>➕ Add</a> |
            <a href='/logout'>Logout</a>

        </div>
    </div>

    <div class='stats'>
        <div class='box'>Total: {{total}}</div>
        <div class='box'>Done: {{done}}</div>
        <div class='box'>USD: ${{usd}}</div>
    </div>

    {% for i,a in data %}
    <div class='card'>
        <b>{{a.name}}</b><br>
        Type: {{a.type}}<br>
        Network: {{a.network}}<br>
        Chain: {{a.chain}}<br>
        Wallet: {{a.wallet}}<br>
        Balance: {{a.balance}} (${{a.usd}})<br>
        Date: {{a.date}}<br>
        Status: {{a.status}}<br>
        Note: {{a.note}}<br><br>

        <a class='btn' href='/done/{{i}}'>DONE</a>
        <a class='btn' href='/delete/{{i}}'>DELETE</a>
    </div>
    {% endfor %}

    </div>
    """

    return render_template_string(html,
        data=list(enumerate(data)),
        total=total,
        done=done,
        usd=round(total_usd,2),
        request=request
    )

# ================= ADD =================
@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        data = load()

        data.append({
            "name": request.form["name"],
            "type": request.form["type"],
            "network": request.form["network"],
            "chain": request.form["chain"],
            "wallet": request.form["wallet"],
            "date": request.form.get("date") or datetime.now().strftime("%Y-%m-%d"),
            "note": request.form["note"],
            "status": "pending"
        })

        save(data)
        return redirect("/")

    return """
    <style>
    body{background:#0d1117;color:#0f0;font-family:monospace}
    input,select,button{padding:10px;margin:5px;background:#111;color:#0f0;border:1px solid #0f0}
    </style>

    <h2>Tambah Airdrop</h2>

    <form method=post>

    Nama:<br>
    <input name=name><br>

    Type:<br>
    <select name=type>
        <option value=telegram>Telegram</option>
        <option value=twitter>Twitter</option>
        <option value=waitlist>Waitlist</option>
        <option value=form>Form</option>
        <option value=testnet>Testnet</option>
    </select><br>

    Network:<br>
    <select name=network id="network" onchange="updateChain()">
        <option value=evm>EVM</option>
        <option value=sol>Solana</option>
        <option value=sui>Sui</option>
        <option value=aptos>Aptos</option>
        <option value=ton>TON</option>
    </select><br>

    Chain:<br>
    <select name=chain id="chain"></select><br>

    Wallet:<br>
    <input name=wallet><br>

    Date:<br>
    <input type=date name=date><br>

    Note:<br>
    <input name=note><br><br>

    <button>Save</button>

    </form>

    <script>
    function updateChain() {
        let network = document.getElementById("network").value;
        let chain = document.getElementById("chain");

        let options = {
            "evm": ["eth","bsc","polygon","base","arbitrum","optimism"],
            "sol": ["solana"],
            "sui": ["sui"],
            "aptos": ["aptos"],
            "ton": ["ton"]
        };

        chain.innerHTML = "";

        options[network].forEach(c => {
            let opt = document.createElement("option");
            opt.value = c;
            opt.innerHTML = c.toUpperCase();
            chain.appendChild(opt);
        });
    }

    updateChain();
    </script>
    """

# ================= DONE =================
@app.route("/done/<int:i>")
def done(i):
    data = load()
    if i < len(data):
        data[i]["status"] = "done"
        save(data)
    return redirect("/")

# ================= DELETE =================
@app.route("/delete/<int:i>")
def delete(i):
    data = load()
    if i < len(data):
        data.pop(i)
        save(data)
    return redirect("/")

# ================= EDIT NAMA =================
@app.route("/edit/<int:i>", methods=["GET","POST"])
def edit(i):
    data = load()

    if i >= len(data):
        return redirect("/")

    # kalau klik save
    if request.method == "POST":
        data[i]["name"] = request.form["name"]
        save(data)
        return redirect("/")

    # tampil form edit
    a = data[i]

    return f"""
    <style>
    body{{background:#0d1117;color:#0f0;font-family:monospace;text-align:center}}
    input,button{{padding:10px;margin:5px;background:#111;color:#0f0;border:1px solid #0f0}}
    </style>

    <h2>Edit Nama Airdrop</h2>

    <form method="post">
        <input name="name" value="{a['name']}" required>
        <br>
        <button>Simpan</button>
    </form>

    <br>
    <a href="/">Kembali</a>
    """
    
# ================= RUN =================
if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")

    if not os.path.exists(FILE):
        save([])

    import os
    port = int(os.environ.get("PORT", 5001))

    app.run(host="0.0.0.0", port=port)