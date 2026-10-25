"""Dialogue pagination and silent action regression in the built mobile game."""
import os, shutil
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':800,'height':360},is_mobile=True,has_touch=True)
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.route('**/cordova.js',lambda route:route.fulfill(status=200,body=''))
 page.add_init_script("localStorage.setItem('sn_save',JSON.stringify({story:'timofey',node:'t_varya_reach',ts:Date.now()}))")
 page.goto(os.environ.get('NOWELL_TEST_URL','http://127.0.0.1:8765/www/index.html'))
 page.wait_for_selector('#loader',state='detached')
 page.keyboard.press('Enter');page.wait_for_selector('#s-disclaimer.active')
 page.keyboard.press('Enter');page.wait_for_selector('#s-main.active')
 page.locator('#btnResume').tap()
 page.wait_for_selector('#s-vn.cinematic')
 assert page.locator('#txtVis').inner_text()==''
 assert not page.locator('#dlg .body').is_visible()
 page.wait_for_function('JSON.parse(localStorage.sn_save).node==="t_varya_slap"',timeout=12000)
 page.wait_for_function('document.getElementById("txtVis").textContent==="ТИМОФЕЙ!"')
 assert not page.locator('#s-vn').evaluate('(el)=>el.classList.contains("cinematic")')
 # Check real pagination function with quoted dialogue at multiple viewport widths.
 script=page.locator('script').all_text_contents()[-1]
 start=script.index('function splitPages(text) {');end=script.index('\nfunction setBg(',start)
 function=script[start:end]
 for width in [568,640,800,960]:
  page.set_viewport_size({'width':width,'height':360})
  pages=page.evaluate('('+function+')', '«Кажется, кошмар приснился… Капец… Пойду умоюсь.»')
  assert all(p.strip() not in ['«','»','”','"'] for p in pages),pages
 assert not errors,errors
 browser.close()
print('Silent action advances to shout; no quote-only pages; no JavaScript errors.')
