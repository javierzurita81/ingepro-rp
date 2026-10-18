/* Anotaciones táctiles: coordenadas normalizadas; la imagen original permanece intacta. */
function diagElegirFoto(input){
  const form=input.closest('form');
  form.querySelectorAll('input[type=file]').forEach(el=>{if(el!==input)el.value=''});
  const msg=document.getElementById('diag-foto-seleccionada');
  if(msg)msg.textContent=input.files.length?input.files[0].name:'Sin fotografía seleccionada';
}
document.querySelectorAll('.diag-photo-stage[data-hid]').forEach(stage=>{
  const canvas=stage.querySelector('canvas'); if(!canvas)return;
  const img=stage.querySelector('img'); const ctx=canvas.getContext('2d');
  let marks=JSON.parse(stage.dataset.marcas||'[]');let tool='circle',color='#e53935';
  const panel=stage.closest('.diag-photo-side');
  function draw(){
    const rect=stage.getBoundingClientRect();const ratio=window.devicePixelRatio||1;
    canvas.width=Math.max(1,Math.round(rect.width*ratio));canvas.height=Math.max(1,Math.round(rect.height*ratio));
    ctx.setTransform(ratio,0,0,ratio,0,0);ctx.lineWidth=3;ctx.lineCap='round';
    marks.forEach(m=>{const x=m.x*rect.width,y=m.y*rect.height;ctx.strokeStyle=m.color;ctx.fillStyle=m.color;ctx.beginPath();
      if(m.tipo==='circle')ctx.ellipse(x,y,26,22,0,0,Math.PI*2);
      else if(m.tipo==='square')ctx.rect(x-26,y-22,52,44);
      else{ctx.moveTo(x-28,y+23);ctx.lineTo(x+25,y-23);ctx.moveTo(x+25,y-23);ctx.lineTo(x+7,y-18);ctx.moveTo(x+25,y-23);ctx.lineTo(x+20,y-5)}ctx.stroke();});
  }
  canvas.addEventListener('pointerup',e=>{const r=canvas.getBoundingClientRect();marks.push({tipo:tool,color,x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))});draw();});
  panel.querySelectorAll('[data-tool]').forEach(b=>b.addEventListener('click',()=>{tool=b.dataset.tool;panel.querySelectorAll('[data-tool]').forEach(t=>t.classList.toggle('active',t===b));}));
  panel.querySelectorAll('[data-color]').forEach(b=>b.addEventListener('click',()=>{color=b.dataset.color;}));
  panel.querySelector('[data-undo]').addEventListener('click',()=>{marks.pop();draw();});
  panel.querySelector('[data-save-marks]').addEventListener('click',async e=>{
    const b=e.currentTarget;b.disabled=true;
    try{const r=await fetch(b.dataset.url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({marcas:marks})});if(!r.ok)throw Error('No se pudieron guardar las marcas');b.textContent='✓ Marcas guardadas';setTimeout(()=>b.textContent='Guardar marcas',2200)}catch(err){alert(err.message)}finally{b.disabled=false}
  });
  if(img&&!img.complete)img.addEventListener('load',draw);new ResizeObserver(draw).observe(stage);draw();
});
