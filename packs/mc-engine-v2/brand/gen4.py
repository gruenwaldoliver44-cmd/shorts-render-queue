import asyncio, os
exec(open('gen2.py').read().split("V = {")[0])
Y='#FFD21F'; Y2='#FFE45C'
DEFS2 = DEFS + f"<linearGradient id='yb' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{Y2}'/><stop offset='1' stop-color='#FFC400'/></linearGradient>"
def svg2(w,h,inner): return f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg'><defs>{DEFS2}</defs>{inner}</svg>"
def ybg(w,h): return f"<rect width='{w}' height='{h}' fill='url(#yb)'/><rect width='{w}' height='{h}' fill='url(#dots)' opacity='.0'/>"
# icons parameterised by colours: fg = main shape colour, cut = colour of cut-outs
def play(fg,cut,s=1): return f"<g transform='scale({s})'><circle r='170' fill='{fg}'/><circle r='138' fill='none' stroke='{cut}' stroke-width='6' opacity='.25'/><path d='M-50 -78 L86 0 L-50 78 Z' fill='{cut}' stroke='{cut}' stroke-width='26' stroke-linejoin='round'/></g>"
def lens(fg,cut,dl,s=1): return f"<g transform='scale({s})'><circle cx='-25' cy='-25' r='135' fill='{cut}' stroke='{fg}' stroke-width='36'/><line x1='72' y1='72' x2='165' y2='165' stroke='{fg}' stroke-width='50' stroke-linecap='round'/><text x='-25' y='60' font-family='AB' font-size='230' fill='{dl}' text-anchor='middle'>$</text></g>"
def mono(fg,cut,s=1): return f"<g transform='scale({s})'><rect x='-175' y='-175' width='350' height='350' rx='80' fill='{fg}'/><text x='0' y='70' font-family='AB' font-size='200' fill='{cut}' text-anchor='middle' letter-spacing='-8'>MC</text></g>"
V = {
 '5c-mono-weiss': (lambda s: mono('#FFFFFF', NAVY, s), 'n', 'MONEY STORIES · EXPLAINED'),
 '5b-mono-navy':  (lambda s: mono(Y, NAVY, s), 'n', 'MONEY STORIES · EXPLAINED'),
}
V_old = {
 '2a-play-gelb':  (lambda s: play(NAVY, Y, s), 'y', 'THE MONEY STORY BEHIND THE HEADLINES'),
 '2b-play-navy':  (lambda s: play(Y, NAVY, s), 'n', 'THE MONEY STORY BEHIND THE HEADLINES'),
 '4a-lupe-gelb':  (lambda s: lens(NAVY, Y, NAVY, s), 'y', 'EVERY VIDEO OPENS ONE MONEY CASE'),
 '4b-lupe-navy':  (lambda s: lens(CREAM, NAVY2, Y, s), 'n', 'EVERY VIDEO OPENS ONE MONEY CASE'),
 '5a-mono-gelb':  (lambda s: mono(NAVY, Y, s), 'y', 'MONEY STORIES · EXPLAINED'),
 '5b-mono-navy':  (lambda s: mono(Y, NAVY, s), 'n', 'MONEY STORIES · EXPLAINED'),
}
def ban(ic, mode, tag):
    if mode=='y':
        base=ybg(2560,1440)+chart(0,300,2560,900,NAVY,7,.10); tc=NAVY; ac=NAVY; bar=NAVY
    else:
        base=bg(2560,1440)+chart(0,300,2560,900,Y,7,.16); tc=CREAM; ac=Y; bar=Y
    return svg2(2560,1440, base+f"<g transform='translate(740 712)'>{ic(.44)}</g>"+T('MONEY CLASSICS',870,735,100,tc,ls=2)+T(tag,874,805,38,ac,'SG',ls=8,w='700')+f"<rect x='874' y='624' width='96' height='9' rx='4' fill='{bar}'/>")
def av(ic,mode): return svg2(800,800,(ybg(800,800) if mode=='y' else bg(800,800))+f"<g transform='translate(400 400)'>{ic(1.45)}</g>")
async def main():
    os.makedirs('out4',exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page()
        for k,(ic,mode,tag) in V.items():
            for kind,(w,h),body in (('avatar',(800,800),av(ic,mode)),('banner',(2560,1440),ban(ic,mode,tag))):
                await pg.set_viewport_size({'width':w,'height':h});await pg.set_content(page(w,h,body));await pg.wait_for_timeout(200)
                await pg.screenshot(path=f'out4/{k}_{kind}.png')
        await b.close()
asyncio.run(main());print('ok')
