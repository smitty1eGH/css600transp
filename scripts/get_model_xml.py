# https://github.com/NetLogo/NetLogo/blob/hexy/netlogo-headless/resources/main/system/behaviorspace.dtd
# https://github.com/smokedice/Gnosis/tree/master/gnosis/util

import re

from constants import (
    FILEN,
    RX,
    BEHAVIOR_SPACE,
    EXTRACT,
    INSERT,
    RX0,
    RX1,
    RX2,
    XML_TEMPLATE,
)

from functions import rxe, rxi

# print(f'{rxe}\n{rxi}')

h = None
with open(FILEN, "r") as f:
    rx = re.compile(RX)
    g = f.read()
    h = rx.split(g)

m = re.search(rxe[0], h[BEHAVIOR_SPACE])
print(f"{m[1]}\t{m[2]}\t{m[3]}")
m = re.search(rxe[1], h[BEHAVIOR_SPACE], re.M)
print(f"{m[1]}\t{m[2]}\t{m[3]}")
m = re.search(rxe[2], h[BEHAVIOR_SPACE], re.M)
print(f"{m[1]}\t{m[2]}")
