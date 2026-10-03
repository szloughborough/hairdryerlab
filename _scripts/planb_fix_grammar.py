"""修方案 B 剩余 4 处语法错误（drafts 里，改完需重建）。"""
import io

FIXES = {
    'deliverables/drafts/under-150.mdx': [
        ('but the about C$80 Slopehill Brushless carries',
         'but the Slopehill Brushless at about C$80 carries'),
    ],
    'deliverables/drafts/shark-vs-dyson.mdx': [
        ('the case for Shark over a about C$100 Laifen Air rests',
         'the case for Shark over a Laifen Air at about C$100 rests'),
    ],
    'deliverables/drafts/damaged-hair.mdx': [
        ("its rating is 4.5★ against a about C$100 dryer's 4.6★",
         "its rating is 4.5★ against 4.6★ for a dryer at about C$100"),
        ('its rating is 4.5★ against a about C$100 dryer’s 4.6★',
         'its rating is 4.5★ against 4.6★ for a dryer at about C$100'),
    ],
    'deliverables/drafts/revlon.mdx': [
        ('The about C$19 price is the deciding factor',
         'The price of about C$19 is the deciding factor'),
    ],
}

for path, pairs in FIXES.items():
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new, 1)
            n += 1
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{path.split("/")[-1]:<28} 修了 {n} 处')
