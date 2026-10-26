"""Walk every new Serega frame and verify decoded images in the actual game."""
import os,shutil,json
from pathlib import Path
from playwright.sync_api import sync_playwright
keys=['yard','peek','crawl','sit','inside','bite','reach','bone','leave','window','car','depart','entrance','stairs','food','visitor','caught']
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':800,'height':360},has_touch=True,is_mobile=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/cordova.js',lambda r:r.fulfill(status=200,body=''))
 page.add_init_script('localStorage.sn_cfg=JSON.stringify({speed:5,vol:20,auto:3,muted:true})')
 page.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8767/www/index.html'))
 page.wait_for_selector('#loader',state='detached')
 page.keyboard.press('Enter');page.wait_for_selector('#s-disclaimer.active')
 page.keyboard.press('Enter');page.wait_for_selector('#s-main.active')
 page.locator('[data-act="start"]').tap()
 page.locator('[data-story="serega"]').tap()
 for key in keys:
  node='s_intro_'+key
  page.wait_for_function('(n)=>JSON.parse(localStorage.sn_save).node===n',arg=node)
  page.wait_for_function('document.querySelector(".layer.on img")?.naturalWidth>0')
  src=page.locator('.layer.on img').get_attribute('src')
  assert src.endswith('/oct_'+('chips' if key=='food' else key)+'.jpg'),(key,src)
  text=page.locator('#txtGhost').text_content()
  assert 'чипс' not in text.lower(),text
  if key=='car':assert 'украл' in text and 'собачьего корма' in text
  if key=='reach':assert 'из будки' in text
  if key in ['yard','stairs','caught']:
   page.wait_for_timeout(700)
   page.screenshot(path='/tmp/nowell-014-'+key+'.png')
  for _ in range(10):
   page.keyboard.press('Space');page.wait_for_timeout(130)
   if page.evaluate('JSON.parse(localStorage.sn_save).node')!=node:break
  else:raise AssertionError('Scene stuck: '+node)
 assert page.evaluate('JSON.parse(localStorage.sn_save).node')=='s_end'
 page.wait_for_function('document.querySelectorAll("#choices .choice").length===2')
 for old,expected in [('s1','s_intro_yard'),('s4h','s_intro_yard'),('s_intro_chips','s_intro_food'),('s_intro_bone','s_intro_bone')]:
  page.evaluate('(node)=>localStorage.sn_save=JSON.stringify({story:"serega",node,ts:1})',old)
  page.reload();page.wait_for_selector('#loader',state='detached')
  assert page.evaluate('JSON.parse(localStorage.sn_save).node')==expected
 assert not errors,errors
 browser.close()
print('All 17 new Serega frames load in sequence and end without entering the placeholder story; legacy saves migrate.')
