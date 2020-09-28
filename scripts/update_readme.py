import re

FILEN='FireSim.nlogo'
README='README.md'
RX='@#\$#@#\$#@'
rx=re.compile(RX)

readme_data=None
with open(FILEN,'r') as f:
    g=f.read()
    h=rx.split(g)
    readme_data=h[2]

with open(README,'w') as f:
    f.write(readme_data)
