L, SL, DR = 18.47, 9.84, 16.00
W = 0.35 * L + 0.55 * SL + 0.10 * DR
print('weighted =', round(W, 4))
mixes = {'pure Laifen': (1, 0, 0), 'Laifen-heavy': (.6, .35, .05),
         'balanced': (.35, .55, .10), 'slope-heavy': (.15, .75, .10),
         'pure slopehill': (0, 1, 0)}
for name, (a, b, c) in mixes.items():
    w = a * L + b * SL + c * DR
    print(f'{name:<16} w={w:6.2f}  visits_for_1000={1000/(0.18*0.08*w):8,.0f}  '
          f'base4503_rev={4503*0.18*0.08*w:7,.0f}')
