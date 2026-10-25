"""Mobile regression check; see README.md for dependencies and server startup."""
import os, shutil
from playwright.sync_api import sync_playwright
import json
sizes=[(800,360),(915,412),(873,393),(960,432),(640,360),(568,320),(1024,600),(1280,720)]
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 context=b.new_context(viewport={'width':800,'height':360},is_mobile=True,has_touch=True,device_scale_factor=2)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/cordova.js',lambda route:route.fulfill(status=200,body='// layout test'))
 page.add_init_script('localStorage.setItem("sn_save",JSON.stringify({story:"timofey",node:"t_bed",ts:1}));localStorage.setItem("sn_cfg",JSON.stringify({speed:5,vol:20,auto:3,muted:true}));')
 page.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8765/www/index.html'));page.wait_for_selector('#loader',state='detached');page.keyboard.press('Enter');page.wait_for_selector('#s-disclaimer.active');page.keyboard.press('Enter');page.wait_for_selector('#s-main.active')
 def fits(selector,w,h):
  for box in page.locator(selector).evaluate_all('(els)=>els.filter(e=>e.getClientRects().length).map(e=>{let b=e.getBoundingClientRect();return {name:e.id||e.dataset.act||e.className,x:b.x,y:b.y,right:b.right,bottom:b.bottom,w:b.width,h:b.height}})'):
   assert box['x']>=-1 and box['y']>=-1 and box['right']<=w+1 and box['bottom']<=h+1,(w,h,selector,box)
 for w,h in sizes:
  page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(500)
  fits('#s-main .menu-btns>button:not([hidden])',w,h)
  assert page.locator('#s-main .menu-btns').evaluate('(e)=>e.scrollHeight<=e.clientHeight+1')
  if w==800:page.screenshot(path='/tmp/nowell-landscape-main.png')
  page.locator('#s-main [data-act="start"]').tap();page.wait_for_timeout(500)
  fits('#s-variants .header-img,#s-variants .card,#s-variants .back-btn',w,h)
  assert page.locator('#s-variants .next-btn').count()==0
  if w==800:page.screenshot(path='/tmp/nowell-landscape-variants.png')
  page.locator('#s-variants [data-story="timofey"]').tap();page.wait_for_timeout(1100)
  fits('#dlg,#bMenu',w,h)
  if h<=600:
   assert page.locator('#dlg').bounding_box()['height']<=h*.35,(w,h,page.locator('#dlg').bounding_box())
   assert page.locator('.ctl button:visible').count()==1
  if w==800:page.screenshot(path='/tmp/nowell-landscape-scene.png')
  page.locator('#bMenu').tap();page.wait_for_timeout(350)
  fits('#pause .p-row',w,h)
  if h<=600:assert page.locator('#pause .panel').evaluate('(e)=>e.scrollHeight<=e.clientHeight+1'),(w,h,'pause scroll')
  if w==800:page.screenshot(path='/tmp/nowell-landscape-pause.png')
  page.locator('#pause [data-act="settings"]').tap();page.wait_for_timeout(350)
  if h>=360 and h<=600:
   assert page.locator('#settings .panel').evaluate('(e)=>e.scrollHeight<=e.clientHeight+1'),(w,h,'settings scroll')
   fits('#settings input,#settings button',w,h)
  if w==800:page.screenshot(path='/tmp/nowell-landscape-settings.png')
  page.locator('[data-act="close-settings"]').tap();page.locator('#pause [data-act="main-menu"]').tap();page.wait_for_timeout(1000)
  results.append({'size':[w,h],'menus_fit':True})
 assert not errors,errors
 b.close()
print(json.dumps({'layouts':results,'errors':errors}))
open('/tmp/nowell-landscape-results.json','w').write(json.dumps(results,indent=2))
