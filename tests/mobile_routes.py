"""Touch regression through every story branch in a 20:9 viewport."""
import os, shutil
import json,itertools
from playwright.sync_api import sync_playwright
results={'routes':[],'errors':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':800,'height':360},is_mobile=True,has_touch=True)
 page.route('**/cordova.js',lambda route:route.fulfill(status=200,body='// Browser validation of the offline game'))
 page.on('pageerror',lambda e:results['errors'].append(str(e)))
 page.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8765/www/index.html'))
 page.wait_for_selector('#loader',state='detached')
 page.keyboard.press('Enter');page.wait_for_selector('#s-disclaimer.active')
 page.keyboard.press('Enter');page.wait_for_selector('#s-main.active')
 page.locator('#s-main [data-act="settings"]').tap()
 page.locator('#setSpeed').fill('5');page.locator('#setVol').fill('35')
 page.locator('[data-act="close-settings"]').tap()
 cfg=page.evaluate('JSON.parse(localStorage.getItem("sn_cfg"))')
 assert cfg['speed']==5 and cfg['vol']==35
 results['settings']=True
 page.locator('[data-act="start"]').tap()
 for story in ['timofey','serega']:
  for branch in ([(0,0),(1,0),(0,1,0),(0,1,1),(1,1,0),(1,1,1)] if story=='timofey' else list(itertools.product([0,1],repeat=2))):
   page.locator('#s-variants [data-story="'+story+'"]').tap()
   for choice in branch:
    if page.locator('#clipPlayer').is_visible(): page.locator('#closeClip').tap()
    page.wait_for_function('!document.getElementById("s-vn").classList.contains("is-transitioning")')
    page.keyboard.press('s')
    page.wait_for_function('document.querySelectorAll("#choices .choice").length===2')
    page.locator('#choices .choice').nth(choice).tap()
    page.wait_for_function('document.querySelectorAll("#choices .choice").length===0')
   if page.locator('#clipPlayer').is_visible(): page.locator('#closeClip').tap()
   page.wait_for_function('!document.getElementById("s-vn").classList.contains("is-transitioning")')
   page.keyboard.press('s')
   page.wait_for_function('document.querySelectorAll("#choices .choice").length===2')
   saved=page.evaluate('JSON.parse(localStorage.getItem("sn_save"))')
   expected='t_end' if story=='timofey' else ('s4' if branch[1]==0 else 's4h')
   assert saved['node']==expected,(saved,expected)
   page.keyboard.press('l');page.wait_for_selector('#history.open')
   assert page.locator('#histList .h').count()>=4
   page.locator('[data-act="close-history"]').tap()
   page.locator('#choices .choice').first.tap()
   page.wait_for_selector('#s-variants.active')
   results['routes'].append({'story':story,'choices':branch,'ending':expected})
 page.locator('#s-variants [data-act="to-main"]').tap()
 page.locator('#btnResume').tap();page.wait_for_selector('#s-vn.active')
 assert page.evaluate('JSON.parse(localStorage.getItem("sn_save")).node')=='s4h'
 page.reload();page.wait_for_selector('#loader',state='detached')
 page.keyboard.press('Enter');page.keyboard.press('Enter')
 page.wait_for_selector('#s-main.active');page.locator('#btnResume').tap()
 page.wait_for_selector('#s-vn.active');page.wait_for_function('JSON.parse(localStorage.sn_save).story==="serega"')
 results['resume_after_reload']=True
 page.keyboard.press('Escape');page.wait_for_selector('#pause.open')
 page.locator('[data-act="save"]').tap();page.wait_for_selector('#pause',state='hidden')
 results['manual_save']=True
 mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 mobile.route('**/cordova.js',lambda route:route.fulfill(status=200,body='// Browser validation'))
 mobile.on('pageerror',lambda e:results['errors'].append(str(e)))
 mobile.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8765/www/index.html'));mobile.wait_for_selector('#loader',state='detached')
 mobile.locator('#s-splash').tap(position={'x':10,'y':10})
 mobile.locator('[data-act="disclaimer-next"]').tap()
 mobile.locator('#s-main [data-act="start"]').tap()
 mobile.locator('#s-variants [data-story="timofey"]').tap()
 mobile.wait_for_selector('#s-vn.active')
 results['mobile_start']=True
 browser.close()
assert not results['errors'],results['errors']
open('/tmp/nowell-mobile-touch-routes.json','w').write(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
