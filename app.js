const $ = id => document.getElementById(id);
function show(el, html){el.innerHTML=html;el.classList.remove('hidden')}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
$('imageForm').addEventListener('submit', async e=>{
 e.preventDefault(); const out=$('imageResult'); show(out,'Analyzing image…');
 const fd=new FormData(); fd.append('image',$('imageInput').files[0]);
 try{const r=await fetch('/analyze-image',{method:'POST',body:fd});const d=await r.json();if(!r.ok)throw Error(d.error);
 show(out,`<strong>${esc(d.summary)}</strong><br><img src="${esc(d.image_url)}" alt="Uploaded construction image"><div class="metric-grid"><div class="metric"><small>Image size</small><strong>${esc(d.dimensions)}</strong></div><div class="metric"><small>Brightness / contrast</small><strong>${d.brightness} / ${d.contrast}</strong></div></div><ul>${d.findings.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`);
 }catch(err){show(out,esc(err.message))}
});
$('estimateForm').addEventListener('submit',async e=>{
 e.preventDefault();const out=$('estimateResult');show(out,'Calculating…');
 try{const r=await fetch('/estimate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({area:$('area').value,floors:$('floors').value,kind:$('kind').value})});const d=await r.json();if(!r.ok)throw Error(d.error);
 const money=n=>'₹'+Number(n).toLocaleString('en-IN');
 show(out,`<strong>Estimated project cost: ${money(d.total)}</strong><div class="metric-grid"><div class="metric"><small>Total built-up area</small><strong>${Number(d.total_area).toLocaleString('en-IN')} sq ft</strong></div><div class="metric"><small>Contingency</small><strong>${money(d.contingency)}</strong></div><div class="metric"><small>Foundation allowance</small><strong>${money(d.foundation)}</strong></div><div class="metric"><small>Structure</small><strong>${money(d.structure)}</strong></div><div class="metric"><small>Finishing</small><strong>${money(d.finishing)}</strong></div></div><small>${esc(d.note)}</small>`);
 }catch(err){show(out,esc(err.message))}
});
$('planForm').addEventListener('submit',async e=>{
 e.preventDefault();const out=$('planResult');show(out,'Building schedule…');
 try{const r=await fetch('/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({duration:$('duration').value,floors:$('planFloors').value,start:$('startDate').value})});const d=await r.json();if(!r.ok)throw Error(d.error);
 show(out,`<strong>Draft schedule · ${d.duration} days</strong><ul>${d.tasks.map(t=>`<li><strong>${esc(t.task)}</strong><br>Day ${t.start_day}–${t.end_day} · ${t.days} days</li>`).join('')}</ul><small>${esc(d.note)}</small>`);
 }catch(err){show(out,esc(err.message))}
});
async function sendMessage(message){if(!message.trim())return;const box=$('chatBox');box.insertAdjacentHTML('beforeend',`<div class="user-message">${esc(message)}</div>`);$('message').value='';box.scrollTop=box.scrollHeight;
 try{const r=await fetch('/assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const d=await r.json();box.insertAdjacentHTML('beforeend',`<div class="bot-message">${esc(d.reply)}</div>`)}catch(e){box.insertAdjacentHTML('beforeend','<div class="bot-message">Could not reach the assistant. Please try again.</div>')}box.scrollTop=box.scrollHeight}
$('chatForm').addEventListener('submit',e=>{e.preventDefault();sendMessage($('message').value)});
document.querySelectorAll('.quick-questions button').forEach(b=>b.addEventListener('click',()=>sendMessage(b.textContent)));
$('startDate').value=new Date().toISOString().slice(0,10);
