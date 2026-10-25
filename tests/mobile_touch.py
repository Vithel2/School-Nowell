"""Mobile regression check; see README.md for dependencies and server startup."""
import os, shutil
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),headless=True,args=['--no-sandbox']);context=b.new_context(viewport={'width':800,'height':360},is_mobile=True,has_touch=True)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/cordova.js',lambda r:r.fulfill(status=200,body='// touch test'))
 page.add_init_script('window.testAudio=[];const NativeAudio=Audio;window.Audio=class extends NativeAudio {constructor(src){super(src);window.testAudio.push(this);}};localStorage.setItem("sn_cfg",JSON.stringify({speed:1,vol:30,auto:3,muted:false}));localStorage.setItem("sn_save",JSON.stringify({story:"timofey",node:"t_bed",ts:1}));')
 page.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8765/www/index.html'));page.wait_for_selector('#loader',state='detached');page.keyboard.press('Enter');page.wait_for_selector('#s-disclaimer.active');page.keyboard.press('Enter');page.wait_for_selector('#s-main.active');page.locator('#btnResume').tap();page.wait_for_timeout(1100)
 cdp=context.new_cdp_session(page)
 def swipe(x1,y1,x2,y2):
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x1,'y':y1}]})
  for n in range(1,5):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x1+(x2-x1)*n/4,'y':y1+(y2-y1)*n/4}]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 swipe(160,100,300,100)
 page.wait_for_function('document.getElementById("txtVis").textContent===document.getElementById("txtGhost").textContent')
 assert page.evaluate('JSON.parse(localStorage.sn_save).node')=='t_bed'
 # A delayed independent tap advances exactly once.
 page.wait_for_timeout(550);page.touchscreen.tap(250,100);page.wait_for_function('JSON.parse(localStorage.sn_save).node==="t_bath"')
 swipe(250,180,250,70);page.wait_for_selector('#pause.open')
 assert page.evaluate('JSON.parse(localStorage.sn_save).node')=='t_bath'
 page.locator('#pause [data-act="close-pause"]').tap();page.wait_for_timeout(550)
 page.locator('#bMenu').tap();page.wait_for_selector('#pause.open');page.locator('#pause [data-act="hide-ui"]').tap();assert page.locator('#frame').evaluate('(e)=>e.classList.contains("hide-ui")')
 page.touchscreen.tap(250,100);assert not page.locator('#frame').evaluate('(e)=>e.classList.contains("hide-ui")');assert page.evaluate('JSON.parse(localStorage.sn_save).node')=='t_bath'
 page.evaluate('document.dispatchEvent(new Event("pause"))');assert page.evaluate('window.testAudio.every(a=>a.paused)')
 page.evaluate('document.dispatchEvent(new Event("resume"))');page.wait_for_function('window.testAudio.some(a=>a.dataset.track==="morning"&&!a.paused)')
 page.evaluate('document.dispatchEvent(new Event("backbutton"))');page.wait_for_selector('#pause.open')
 page.evaluate('document.dispatchEvent(new Event("backbutton"))');page.wait_for_selector('#pause',state='hidden')
 page.evaluate('window.cordova={};window.exitCalls=0;navigator.app={exitApp:()=>window.exitCalls++};')
 page.evaluate('document.dispatchEvent(new Event("backbutton"))');page.locator('#pause [data-act="main-menu"]').tap();page.evaluate('document.dispatchEvent(new Event("backbutton"))');page.wait_for_selector('#s-exit.active');page.locator('[data-act="quit"]').tap();assert page.evaluate('exitCalls')==1
 assert not errors,errors;b.close();print(json.dumps({'swipe_no_double_advance':True,'pause_swipe':True,'buttons_and_hide_panel':True,'native_back_and_lifecycle':True,'native_exit_dispatch':True,'errors':errors}))
