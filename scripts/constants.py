from pathlib import Path


# FILEN, RX,BEHAVIOR_SPACE,EXTRACT,INSERT,RX0,RX1,RX2,XML_TEMPLATE


filen = Path("/home/smitty/proj/css600transp/css600transp/FireSim.nlogo")
RX = "@#\$#@#\$#@"  # Netlogo file section delimiter
BEHAVIOR_SPACE = 7  # Netlogo file Behavior Space section

EXTRACT = "(.*?)"
INSERT = "%(__KEY__)s"

RX0 = (
    '<experiment name="__VALUE__" repetitions="__VALUE__" runMetricsEveryStep="__VALUE__">',
    ["name", "repetitions", "runMetricsEveryStep"],
)
RX1 = (
    """<setup>__VALUE__</setup>
    <go>__VALUE__</go>
    <metric>__VALUE__</metric>""",
    ["setup", "go", "metric"],
)
RX2 = (
    """<enumeratedValueSet variable="__VALUE__">
      <value value="__VALUE__"/>
    </enumeratedValueSet>""",
    ["enumeratedValueSet", "value"],
)

XML_TEMPLATE = """<experiments>
  <experiment name="FireSim" repetitions="1" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles</metric>
    <enumeratedValueSet variable="map-file">
      <value value="&quot;blank.map&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="person_path_weight">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Medium">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="add-person-spacing?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="equal-diagonal-weight?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="display-path-cost?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Fire_Speed">
      <value value="50"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Fast-Speed">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Slow">
      <value value="33"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="people-wait?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="set-fire?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Slow-Speed">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="People">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Fast">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Medium-Speed">
      <value value="0.4"/>
    </enumeratedValueSet>
  </experiment>
</experiments>"""
# <experiments>
#  <experiment name="FireSim" repetitions="1" runMetricsEveryStep="true">
#    <setup>setup</setup>
#    <go>go</go>
#    <metric>count turtles</metric>
#    <enumeratedValueSet variable="map-file">
#      <value value="&quot;blank.map&quot;"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="person_path_weight">
#      <value value="2"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Medium">
#      <value value="0"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="add-person-spacing?">
#      <value value="true"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="equal-diagonal-weight?">
#      <value value="true"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="display-path-cost?">
#      <value value="true"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Fire_Speed">
#      <value value="50"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Fast-Speed">
#      <value value="0.8"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Slow">
#      <value value="33"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="people-wait?">
#      <value value="true"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="set-fire?">
#      <value value="false"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Slow-Speed">
#      <value value="0.1"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="People">
#      <value value="500"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Fast">
#      <value value="0"/>
#    </enumeratedValueSet>
#    <enumeratedValueSet variable="Medium-Speed">
#      <value value="0.4"/>
#    </enumeratedValueSet>
#  </experiment>
# </experiments>
