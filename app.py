from flask import Flask, Response
import os

app = Flask(__name__)

HTML = r"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>MapReduce Animation: Word Count</title>
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
    body { margin: 0; padding: 24px; background:#fafafa; }
    h1 { margin: 0 0 12px; }
    .subtitle { color:#555; margin-bottom:16px; }
    .row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 12px;}
    .card { background:#fff; border:1px solid #e5e7eb; border-radius:14px; padding:14px; box-shadow:0 2px 6px rgba(0,0,0,.04);}
    .card h3{ margin:0 0 8px; font-size:16px;}
    .list { min-height: 120px; border:1px dashed #d1d5db; border-radius:10px; padding:8px; display:flex; flex-wrap:wrap; gap:8px;}
    .kv { display:inline-flex; align-items:center; gap:4px; padding:6px 8px; border-radius:999px; border:1px solid #d1d5db; background:#f8fafc; }
    .kv .k { font-weight:600; }
    .kv .v { background:#e2e8f0; padding:0 6px; border-radius:6px; }
    .bucket { padding:8px; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:12px; min-width:120px; }
    .bucket h4 { margin:0 0 6px; font-size:13px; color:#0f172a;}
    .controls { display:flex; gap:8px; margin-top:10px; }
    textarea { width:100%; height:90px; font:inherit; padding:10px; border-radius:10px; border:1px solid #d1d5db;}
    button { padding:8px 12px; border-radius:10px; border:1px solid #111827; background:#111827; color:#fff; cursor:pointer;}
    button.secondary{ background:#fff; color:#111; border-color:#d1d5db;}
    .stage { margin-top:8px; font-weight:600; color:#0ea5e9;}
    .footer { margin-top:16px; color:#6b7280; font-size:13px;}
  </style>
</head>
<body>
  <h1>MapReduce: Word Count (Animated)</h1>
  <div class="subtitle">Shows <b>Map</b> → <b>Shuffle/Sort</b> → <b>Reduce</b> on your text. No database; all in-browser JS.</div>

  <div class="card">
    <h3>Input text</h3>
    <textarea id="input"></textarea>
    <div class="controls">
      <button id="run">▶ Run animation</button>
      <button id="reset" class="secondary">↺ Reset</button>
    </div>
    <div class="stage" id="stage">Stage: —</div>
  </div>

  <div class="row">
    <div class="card">
      <h3>Map (tokenize → emit &lt;word, 1&gt;)</h3>
      <div class="list" id="mapList"></div>
    </div>
    <div class="card">
      <h3>Shuffle / Group by key</h3>
      <div class="list" id="shuffleList" style="gap:12px;"></div>
    </div>
    <div class="card">
      <h3>Reduce (sum counts)</h3>
      <div class="list" id="reduceList"></div>
    </div>
  </div>

  <div class="footer">Tip: try editing the text and re-run. Example keys are normalized to lowercase and non-letters are ignored.</div>

<script>
(function(){
  const defaultText = `%DEFAULT_TEXT%`;
  const input = document.getElementById('input');
  const stageEl = document.getElementById('stage');
  const mapList = document.getElementById('mapList');
  const shuffleList = document.getElementById('shuffleList');
  const reduceList = document.getElementById('reduceList');
  const runBtn = document.getElementById('run');
  const resetBtn = document.getElementById('reset');

  input.value = defaultText;

  function clearAll(){
    mapList.innerHTML = '';
    shuffleList.innerHTML = '';
    reduceList.innerHTML = '';
    setStage('—');
  }
  function setStage(t){ stageEl.textContent = 'Stage: ' + t; }

  function tokenise(txt){
    return txt
      .toLowerCase()
      .replace(/[^a-z0-9\s]+/g,' ')
      .split(/\s+/)
      .filter(Boolean);
  }

  function chipKV(k,v){
    const el = document.createElement('div');
    el.className = 'kv';
    el.innerHTML = `<span class="k">${k}</span><span class="v">${v}</span>`;
    return el;
  }

  function bucket(title){
    const b = document.createElement('div');
    b.className = 'bucket';
    b.innerHTML = `<h4>${title}</h4><div class="list"></div>`;
    return b;
  }

  async function animate(){
    clearAll();
    runBtn.disabled = true;

    // MAP
    setStage('Map: emit ⟨word, 1⟩');
    const words = tokenise(input.value);
    const pairs = words.map(w => [w,1]);

    for (const [i,p] of pairs.entries()){
      await new Promise(r=>setTimeout(r, 150));
      mapList.appendChild(chipKV(p[0], p[1]));
    }

    // SHUFFLE / GROUP
    setStage('Shuffle/Sort: group by key');
    const groups = {};
    for (const [w,one] of pairs){
      groups[w] = groups[w] || [];
      groups[w].push(one);
    }

    await new Promise(r=>setTimeout(r, 400));
    Object.keys(groups).sort().forEach(k=>{
      const b = bucket(k);
      shuffleList.appendChild(b);
      const inner = b.querySelector('.list');
      groups[k].forEach((v,idx)=>{
        setTimeout(()=> inner.appendChild(chipKV(k, v)), 120*idx);
      });
    });

    // wait a moment before reduce
    await new Promise(r=>setTimeout(r, 120 * words.length + 400));

    // REDUCE
    setStage('Reduce: sum values per key');
    const results = {};
    Object.entries(groups).forEach(([k,arr])=>{
      const sum = arr.reduce((a,b)=>a+b,0);
      results[k] = sum;
    });

    Object.keys(results).sort((a,b)=>results[b]-results[a] || a.localeCompare(b))
      .forEach((k,i)=>{
        setTimeout(()=> reduceList.appendChild(chipKV(k, results[k])), 120*i);
      });

    await new Promise(r=>setTimeout(r, 120 * Object.keys(results).length + 400));
    setStage('Done ✅');
    runBtn.disabled = false;
  }

  runBtn.addEventListener('click', animate);
  resetBtn.addEventListener('click', clearAll);
})();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    sample = os.environ.get("MR_TEXT", "to be or not to be that is the question.\n"
                                      "to be yourself in a world that is constantly trying to make you something else "
                                      "is the greatest accomplishment.")
    # keep it single-line safely embedded
    sample = sample.replace("\\", "\\\\").replace("`", "\\`").replace("\n", " ").replace('"', '\\"')
    page = HTML.replace("%DEFAULT_TEXT%", sample)
    return Response(page, mimetype="text/html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
