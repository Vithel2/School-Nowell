"""Walk every new Serega frame and verify decoded images in the actual game."""
import os,shutil,json
from pathlib import Path
from playwright.sync_api import sync_playwright
keys=['yard','peek','crawl','sit','reach','bone','inside','bite','leave','car','window','depart','entrance','stairs','chips','visitor','caught']
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
  assert src.endswith('/oct_'+key+'.jpg'),(key,src)
  if key in ['yard','stairs','caught']:
   page.wait_for_timeout(700)
   page.screenshot(path='/tmp/nowell-014-'+key+'.png')
  for _ in range(10):
   page.keyboard.press('Space');page.wait_for_timeout(130)
   if page.evaluate('JSON.parse(localStorage.sn_save).node')!=node:break
  else:raise AssertionError('Scene stuck: '+node)
 assert page.evaluate('JSON.parse(localStorage.sn_save).node')=='s1'
 assert not errors,errors
 browser.close()
print('All 17 new Serega frames load in sequence and return to the existing story.')
