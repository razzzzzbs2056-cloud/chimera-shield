"""Character-count check for ad-copy.md. Run: python3 check_copy.py"""
H = [
"Free WISP Readiness Check",
"WISP Help for Tax Preparers",
"Before You Renew Your PTIN",
"Find 3 Gaps in Your WISP",
"FTC Safeguards Rule Check",
"Written Security Plan Check",
"For 5–50 Person Tax Firms",
"About 10 Minutes, No Cost",
"Plain-English Results",
"No Passwords or Client Data",
"Your 3 Gaps, Emailed to You",
"Structured on IRS Pub 5708",
"Not Affiliated With the IRS",
"W-12 Asks About Your WISP",
"Know Where Your Plan Stands",
]
D = [
"Answer 12 plain-English questions. Get the 3 gaps to close before you sign your W-12.",
"For tax and accounting firms with 5–50 staff. Free, no payment details, no client data.",
"Structured on IRS Pub 5708 and FTC Safeguards Rule. Not affiliated with the IRS or FTC.",
"PTINs expire Dec 31. Check your written security plan now, not in filing season.",
]
SL = ["How the Check Works","What You Get","Is It Really Free?","Who Sees My Results?"]
SLD = ["12 questions plus a domain check","Passive, with your written OK","3 ranked gaps in plain English","Plus your email-domain result","No payment details needed","One follow-up email, no more","Only you, at your work email","Stored encrypted, never shared"]
CO = ["Free, No Payment Details","About 10 Minutes","Passive Checks Only","No Client Data Needed","Plain English","Independent Company"]
RT_H = ["Finish Your Free Check","Want Help Closing the Gaps?","Done Before Filing Season"]
RT_L = ["Pick up your free WISP readiness check where you left off","Want help closing your 3 gaps? Get a WISP that fits your firm","Get your written security plan done before filing season"]
RT_D = [
"You started the free WISP readiness check. It takes about 10 minutes to finish.",
"A WISP that fits how your firm works, plus your top 5 fixes. About 2 hours of your time.",
"Last intake calls Dec 4, so your plan is done before the holidays. Book a 15-minute call.",
]
def show(name, items, lim):
    print(f"== {name} (limit {lim})")
    for i,s in enumerate(items,1):
        n=len(s); print(f"{i:2d}. {n:3d} {'OK ' if n<=lim else 'OVER'} {s}")
show("Headlines",H,30); show("Descriptions",D,90); show("Sitelink text",SL,25); show("Sitelink desc",SLD,35); show("Callouts",CO,25)
show("Retarget short headline",RT_H,30); show("Retarget description",RT_D,90); show("Retarget long headline",RT_L,90)
LI = [
("Renewing your PTIN this fall? Form W-12 asks you to confirm you know you need a written information security plan. Our free readiness check shows the 3 gaps to close first, in plain English. About 10 minutes, no payment details, no client data.",
 "Find the 3 gaps in your security plan before you renew"),
("A WISP template gives you the structure. It doesn't tell you what's true at your firm today. Answer 12 plain-English questions, and with your OK we read your email domain's public settings. You get 3 gaps, ranked, with a first step for each.",
 "Free WISP & Safeguards Readiness Check for tax firms"),
("Fewer than 5,000 clients? Four FTC Safeguards Rule items don't apply to you. The rest, like multi-factor login, encryption and staff training, still do. Our free check tells you which is which and the 3 gaps to close first.",
 "Which Safeguards items apply to your firm? Check free"),
]
RT_LI = [
("You started the free WISP & Safeguards Readiness Check. It takes about 10 minutes to finish, and your 3 gaps arrive by email within one business day.",
 "Pick up where you left off"),
("Got your 3 gaps? If you'd like help, we build a written security plan around how your firm actually works, mark what's verified, and rank your top 5 fixes. About two hours of your time.",
 "Want help closing your gaps before Dec 31?"),
("Our last intake calls are Dec 4, so plans are delivered before the holidays and you're not thinking about this in filing season. Book a 15-minute call to see if it fits.",
 "Get your WISP done before filing season"),
]
for label,arr in (("LinkedIn",LI),("Retarget LinkedIn",RT_LI)):
    print("==",label)
    for i,(t,h) in enumerate(arr,1):
        print(f"{i}. intro {len(t)} (first-150 cut ok? {len(t)<=150}) | headline {len(h)} {'OK' if len(h)<=70 else 'OVER'}")

for t,h in LI+RT_LI: print("CUT@150:", t[:150])
