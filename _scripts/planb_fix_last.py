"""修最后一处 "a about" 语法错误。"""
import io

P = 'deliverables/drafts/under-150.mdx'
t = io.open(P, encoding='utf-8').read()
old = 'If you are choosing between a about C$80 dryer and a about C$100 one, the about C$100 option is closer to the band that actually performs differently'
new = ('If you are choosing between a dryer at about C$80 and one at about C$100, '
       'the C$100 option is closer to the band that actually performs differently')
if old in t:
    t = t.replace(old, new, 1)
    io.open(P, 'w', encoding='utf-8').write(t)
    print('under-150.mdx: 已修 "a about" 语法')
else:
    print('!! 未找到目标句子')
    import re
    for m in re.finditer(r'.{0,60}a about.{0,60}', t):
        print('   ', m.group(0))
