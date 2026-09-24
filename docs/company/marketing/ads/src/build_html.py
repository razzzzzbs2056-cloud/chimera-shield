"""Regenerates the 6 self-contained ad HTML files. Edit copy here, then run render.mjs."""
import os
OUT=os.path.dirname(os.path.abspath(__file__))  # writes the 6 HTML files next to this script
SHIELD = '''<svg class="mark" viewBox="0 0 64 72" aria-hidden="true"><path d="M32 3 L59 13 V35 C59 52 47 64 32 69 C17 64 5 52 5 35 V13 Z" fill="none" stroke="var(--teal)" stroke-width="5" stroke-linejoin="round"/><path d="M20 36 L29 45 L45 27" fill="none" stroke="var(--white)" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
BIGSHIELD = '''<svg class="bgmark" viewBox="0 0 64 72" aria-hidden="true"><path d="M32 3 L59 13 V35 C59 52 47 64 32 69 C17 64 5 52 5 35 V13 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M32 12 L51 19 V35 C51 47 43 56 32 60 C21 56 13 47 13 35 V19 Z" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>'''
BASE = '''
:root{--navy:#0B1F3A;--navy2:#08172C;--navy3:#12305A;--teal:#2EC4B6;--teal2:#1FA89B;--white:#FFFFFF;--ink:#E8EEF5;--muted:#A9BCD0;--line:rgba(255,255,255,.12)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:var(--navy)}
body{font-family:"Helvetica Neue",Helvetica,Arial,"Liberation Sans","DejaVu Sans",sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
.ad{position:relative;width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:radial-gradient(120%% 90%% at 100%% 0%%,var(--navy3) 0%%,var(--navy) 55%%,var(--navy2) 100%%)}
.bgmark{position:absolute;color:rgba(46,196,182,.07)}
.brand{display:flex;align-items:center;gap:14px}
.mark{width:40px;height:45px;flex:none}
.name{font-weight:700;font-size:26px;letter-spacing:.2px;color:var(--white)}
.eyebrow{display:inline-block;font-size:18px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:var(--teal)}
h1{color:var(--white);font-weight:800;letter-spacing:-.5px;line-height:1.08}
h1 em{font-style:normal;color:var(--teal);white-space:nowrap}
.sub{color:var(--muted);line-height:1.35}
.cta{display:inline-flex;align-items:center;gap:12px;background:var(--teal);color:var(--navy2);font-weight:800;border-radius:999px;white-space:nowrap}
.cta .arr{font-size:1.1em;line-height:1}
.foot{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--line);color:var(--muted);font-size:15px}
.accent{position:absolute;left:0;top:0;bottom:0;width:10px;background:linear-gradient(var(--teal),var(--teal2))}
'''
def page(w,h,css,body,title):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width={w},height={h}">
<!-- ChimeraShield ad creative. Self-contained: no external fonts, images or scripts. Render with render.mjs. -->
<style>{BASE % {"w":w,"h":h}}{css}</style></head>
<body><div class="ad">{body}</div></body></html>
'''
FOOT_LI='<div class="foot" style="padding:16px 64px 18px 74px"><span>Free readiness check · [DOMAIN]/check</span><span>Not affiliated with the IRS or the FTC.</span></div>'
FOOT_SQ='<div class="foot" style="padding:22px 72px 26px 82px;flex-direction:column;align-items:flex-start;gap:6px;font-size:18px"><span>Free readiness check · [DOMAIN]/check</span><span>Not affiliated with the IRS or the FTC. Not legal advice.</span></div>'
files={}

# LI-1 deadline
files["li-1-deadline.html"]=page(1200,627,'''
.wrap{position:absolute;left:74px;top:52px;right:64px;bottom:70px;display:flex;flex-direction:column}
.bgmark{width:430px;right:-40px;top:40px}
h1{font-size:56px;margin:26px 0 20px;max-width:1070px}
.sub{font-size:25px;max-width:760px}
.cta{font-size:24px;padding:16px 30px;margin-top:auto;align-self:flex-start}
''',f'''<div class="accent"></div>{BIGSHIELD}
<div class="wrap"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<h1>Before you renew your PTIN, find the <em>3 gaps</em> in your security plan.</h1>
<p class="sub">Free WISP &amp; Safeguards Readiness Check for tax and accounting firms. About 10 minutes, in plain English.</p>
<span class="cta">Start the free check <span class="arr">&rarr;</span></span></div>{FOOT_LI}''',"LI-1 Deadline")

# LI-2 template vs reality
files["li-2-template.html"]=page(1200,627,'''
.left{position:absolute;left:74px;top:52px;width:560px;bottom:70px;display:flex;flex-direction:column}
h1{font-size:50px;margin:26px 0 18px}
.sub{font-size:23px}
.cta{font-size:22px;padding:14px 26px;margin-top:auto;align-self:flex-start}
.card{position:absolute;right:64px;top:70px;width:440px;background:#FFFFFF;color:var(--navy);border-radius:18px;padding:26px 28px 24px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
.tag{display:inline-block;font-size:13px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#5B6B7F;background:#EEF2F6;border-radius:6px;padding:5px 9px}
.card h2{font-size:26px;margin:14px 0 16px;color:var(--navy)}
.row{display:flex;gap:14px;align-items:flex-start;padding:13px 0;border-top:1px solid #E3E9EF}
.num{flex:none;width:32px;height:32px;border-radius:50%;background:var(--teal);color:var(--navy2);font-weight:800;font-size:17px;display:flex;align-items:center;justify-content:center}
.row b{display:block;font-size:18px;color:var(--navy);margin-bottom:3px}
.row span{font-size:15px;color:#4A5A6E;line-height:1.3}
''',f'''<div class="accent"></div>
<div class="left"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<h1>A template gives you structure. The check shows <em>what&rsquo;s true</em> at your firm.</h1>
<p class="sub">12 questions plus a passive check of your email domain, with your OK.</p>
<span class="cta">Start the free check <span class="arr">&rarr;</span></span></div>
<div class="card"><span class="tag">Illustrative example</span><h2>Your 3 gaps</h2>
<div class="row"><div class="num">1</div><div><b>Name your Qualified Individual</b><span>The one person in charge of your security plan.</span></div></div>
<div class="row"><div class="num">2</div><div><b>Second login step on email</b><span>Multi-factor login for every staff account.</span></div></div>
<div class="row"><div class="num">3</div><div><b>Email domain settings</b><span>Make it harder to send fake email as your firm.</span></div></div>
</div>{FOOT_LI}''',"LI-2 Template")

# LI-3 steps
files["li-3-steps.html"]=page(1200,627,'''
.wrap{position:absolute;left:74px;top:52px;right:64px;bottom:70px;display:flex;flex-direction:column}
h1{font-size:52px;margin:24px 0 0}
.steps{display:flex;gap:22px;margin-top:auto}
.step{flex:1;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:16px;padding:20px 22px}
.step .n{color:var(--teal);font-weight:800;font-size:18px;letter-spacing:1px}
.step b{display:block;color:var(--white);font-size:23px;margin:8px 0 6px}
.step span{color:var(--muted);font-size:17px;line-height:1.3}
.bgmark{width:300px;right:40px;top:-30px}
''',f'''<div class="accent"></div>{BIGSHIELD}
<div class="wrap"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<h1>12 questions. About 10 minutes.<br><em>3 gaps, in plain English.</em></h1>
<p class="sub" style="font-size:25px;margin-top:18px">The free WISP &amp; Safeguards Readiness Check for tax and accounting firms.</p>
<div class="steps">
<div class="step"><div class="n">STEP 1</div><b>Answer 12 questions</b><span>About your firm, not about technology.</span></div>
<div class="step"><div class="n">STEP 2</div><b>We read public records</b><span>Your email domain&rsquo;s settings, only with your OK.</span></div>
<div class="step"><div class="n">STEP 3</div><b>Get your 3 gaps</b><span>Ranked, each with a first step, sent to your email.</span></div>
</div></div>{FOOT_LI}''',"LI-3 Steps")

SQCSS='''
.wrap{position:absolute;left:82px;top:78px;right:72px;bottom:130px;display:flex;flex-direction:column}
.name{font-size:30px}.mark{width:46px;height:52px}
.cta{font-size:30px;padding:20px 36px;align-self:flex-start;margin-top:auto}
'''
# SQ-1 deadline
files["sq-1-deadline.html"]=page(1080,1080,SQCSS+'''
.bgmark{width:620px;right:-150px;top:120px}
.eyebrow{margin-top:120px;font-size:22px}
h1{font-size:104px;margin:22px 0 30px}
.sub{font-size:40px;color:var(--ink);line-height:1.25;max-width:820px}
.note{font-size:24px;color:var(--muted);margin-top:22px}
''',f'''<div class="accent"></div>{BIGSHIELD}
<div class="wrap"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<span class="eyebrow">For tax &amp; accounting firms</span>
<h1>PTINs expire <em>Dec&nbsp;31.</em></h1>
<p class="sub">Know the 3 gaps in your security plan before you renew.</p>
<p class="note">Free WISP &amp; Safeguards Readiness Check. About 10 minutes.</p>
<span class="cta">Start the free check <span class="arr">&rarr;</span></span></div>{FOOT_SQ}''',"SQ-1 Deadline")

# SQ-2 W-12
files["sq-2-w12.html"]=page(1080,1080,SQCSS+'''
.form{margin-top:70px;background:#FFFFFF;border-radius:18px;padding:30px 34px;display:flex;gap:22px;align-items:center;box-shadow:0 24px 60px rgba(0,0,0,.35)}
.box{flex:none;width:52px;height:52px;border:4px solid var(--navy);border-radius:8px;position:relative}
.box:after{content:"";position:absolute;left:14px;top:4px;width:14px;height:28px;border:solid var(--teal2);border-width:0 6px 6px 0;transform:rotate(45deg)}
.form p{color:var(--navy);font-size:28px;line-height:1.3;font-weight:600}
.form small{display:block;color:#5B6B7F;font-size:18px;font-weight:400;margin-top:6px}
h1{font-size:74px;margin:56px 0 24px}
.sub{font-size:32px;max-width:860px}
''',f'''<div class="accent"></div>
<div class="wrap"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<div class="form"><div class="box"></div><p>Confirm you know you&rsquo;re required to have a written information security plan.<small>Our summary of the WISP item on Form W-12. Not an IRS image.</small></p></div>
<h1>Your W-12 asks about your security plan. <em>Can you show it?</em></h1>
<p class="sub">Free readiness check: 3 gaps to close before you sign, in plain English.</p>
<span class="cta">Start the free check <span class="arr">&rarr;</span></span></div>{FOOT_SQ}''',"SQ-2 W-12")

# SQ-3 trust
files["sq-3-trust.html"]=page(1080,1080,SQCSS+'''
.bgmark{width:560px;right:-120px;top:-60px}
h1{font-size:88px;margin:110px 0 40px;line-height:1.1}
.list{display:flex;flex-direction:column;gap:18px}
.li{display:flex;align-items:center;gap:18px;font-size:32px;color:var(--ink)}
.dot{flex:none;width:36px;height:36px;border-radius:50%;background:var(--teal);position:relative}
.dot:after{content:"";position:absolute;left:12px;top:6px;width:9px;height:17px;border:solid var(--navy2);border-width:0 4px 4px 0;transform:rotate(45deg)}
''',f'''<div class="accent"></div>{BIGSHIELD}
<div class="wrap"><div class="brand">{SHIELD}<span class="name">ChimeraShield</span></div>
<h1>No passwords.<br>No client data.<br><em>No cost.</em></h1>
<div class="list">
<div class="li"><span class="dot"></span>12 plain-English questions</div>
<div class="li"><span class="dot"></span>Passive check of public records, with your OK</div>
<div class="li"><span class="dot"></span>Your 3 gaps, emailed within a business day</div>
</div>
<span class="cta">Start the free check <span class="arr">&rarr;</span></span></div>{FOOT_SQ}''',"SQ-3 Trust")

for n,c in files.items():
    open(os.path.join(OUT,n),"w").write(c)
print("wrote",len(files))
