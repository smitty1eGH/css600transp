extensions [array table]
turtles-own [speed ]
globals [
  xdim
  ydim
  map_table
  spawn_patch
  block_patch
  speed_table
  default_speed
  default_color
  speed_color_table
  safety_color

  ;mean ticks till escape metrics
  total-escaped
  total-ticks-till-escaped
  mean-escape-time
  max-escape-time

]

patches-own
[
  cost ; for brute force weight pathing


]

;TODO add model termination when agents are all gone

to setup-globals
  ; x and ydims are half the distance of the map e.g. 33 width = xdim  16
  set xdim  16
  set ydim  16
  set map_table table:make

  ;set person_path_weight 3
  ; set map table file values to patch colors
  ; grass
  table:put map_table 0 55
  ; floor
  table:put map_table 1 35
  ; wall
  table:put map_table 2 38
  ; safety
  table:put map_table 3 126

  set safety_color table:get map_table 3

  ; the color of patch that allows people to spawn on it
  set spawn_patch table:get map_table 1

  ; the color of patch that people cant move through
  set block_patch table:get map_table 2

  ; a mapping of speed settings to numerical speed
  set speed_table table:make
  table:put speed_table "slow" Slow-Speed
  table:put speed_table "medium" Medium-Speed
  table:put speed_table "fast" Fast-Speed ; if fast is over 1 they might jump over an exit patch


  ; mapping of speed to color
  set speed_color_table table:make
  table:put speed_color_table "slow" 13
  table:put speed_color_table "medium" 43
  table:put speed_color_table "fast" 63

  set default_speed table:get speed_table "medium"
  set default_color table:get speed_color_table "medium"
end

to setup
  clear-all
  setup-globals
  setup-patches
  setup-agents

  calc-weights
  ifelse display-path-cost?[
    display-weights
  ]
  [ remove-weights ]

  reset-ticks
end

to reset-defaults
  set person_path_weight  2.0
  set People 200
  set Slow  33
  set Medium  33
  set Fast  33

  set Slow-Speed .1
  set Medium-Speed .4
  set Fast-Speed .8

  set add-person-spacing? True
  set people-wait? True
  set equal-diagonal-weight? true
end
to display-weights
  ask patches [set plabel cost]
end
to remove-weights
  ask patches [set plabel ""]
end

; calc the distance weights for each path to the exit
; this is done each tick and determines where agents will move next
to calc-weights
  ; init
  ask patches [set cost -1 ]
  ask patches with [pcolor = safety_color] [set cost 0 ]
  ask patches with [pcolor = block_patch] [set cost -2]
  let current-patches patches with [cost = 0]
  let current-distance 0
  ;display-weights

  while [ any? current-patches]
  [
    ;show current-distance
    let next-patches no-patches
    ask current-patches [
      let patch_neighbors no-patches
      ifelse equal-diagonal-weight?[
        set patch_neighbors neighbors4 with [cost = -1]
      ][
        set patch_neighbors neighbors with [cost = -1]
      ]

      ask patch_neighbors [set cost (current-distance + 1)]
      set next-patches (patch-set patch_neighbors next-patches)
      ;set next-patches fput patch_neighbors next-patches
    ]

    set current-distance (current-distance + 1)
    set current-patches next-patches
  ]

  ; add person weights

  ask turtles [

    ask patch-here [set cost (cost + person_path_weight)]
    ; todo make this weight scaling factor variable
    if add-person-spacing? [
      ask neighbors4 with [cost != -2] [set cost (cost + (person_path_weight / 10 ) ) ] ; divide neighbor weights by scaling factor of person weight
    ]
  ]


end

to go
  move-turtles
  evac-turtles

  calc-weights ; fixes a bug where a patch misses being incremented/decremented
  ifelse display-path-cost?[
    display-weights
  ]
  [ remove-weights ]

  if set-fire?[

    burn-patches
  ]

  calc-mean-escape-time

  tick


end



to calc-mean-escape-time
  ifelse total-escaped = 0[
    set mean-escape-time 0
  ][
    set mean-escape-time (total-ticks-till-escaped / total-escaped )
  ]
end

to burn-patches

  ; how to start the fire?
end


to move-turtles
  ask turtles [


    ;ask patch-here [set cost (cost - person_path_weight)]

    ; move towards the least cost
    ; TODO switch neighbors4 to neighbors (8) but need to figure out how not to get stuck in wall corners
    ;TODO broaden the search get the min for a larger expanse (maybe 2 or 3 out)
    let patch_to_move one-of neighbors4 with [cost != -2 ] with-min [cost]

    ; this wont work because people can see past walls and the get stuck to walls
    ;let patch_to_move one-of  patches in-radius 2 with [cost != -2 ] with-min [cost]

    ;add a scaling factor for determining if a person should move
    ; reduce this patches cost by person path weight / by some scaling factor
    ; this is to reflect that it can be advantageous to stay still
    ;todo make this person path weight scalable
    let this-cost ( cost - ( person_path_weight / 2 ) )


    ; dont move if its more expensive
    if  (not people-wait? ) or ( [cost] of patch_to_move < this-cost) [


      set heading towards patch_to_move

      ;right random 360
      forward speed
      if pcolor = block_patch [
        back ( speed  )
      ]

    ]



  ]
end

to evac-turtles
  ask turtles [
    if pcolor = safety_color [ask patch-here [set cost 0]]
    if pcolor = safety_color [set total-escaped (total-escaped + 1) set total-ticks-till-escaped (total-ticks-till-escaped + ticks ) set max-escape-time ticks die  ]

  ]
end
to setup-agents

  ask n-of People patches with [pcolor = spawn_patch and not any? other turtles-here] [sprout 1]
  ask turtles [set shape "person"]

  assign-speeds
  ask turtles [ask patch-here [set cost (cost + person_path_weight)]]
end

; assign speeds to agents based on slider distribution
to assign-speeds
  let total_count  Slow + Medium + Fast

  let slow_people  floor  ((Slow / total_count) * People)
  let medium_people   floor ((Medium / total_count) * People)
  let fast_people  floor ((Fast / total_count) * People)


  ask turtles [ set speed default_speed set color default_color ]


  ask turtles with [ who < slow_people ] [ set speed table:get speed_table "slow" set color table:get speed_color_table "slow"]

  ask turtles with [ who >= slow_people ] [ set speed table:get speed_table "medium" set color table:get speed_color_table "medium"]
  ask turtles with [ who >= (slow_people + medium_people)] [ set speed table:get speed_table "fast" set color table:get speed_color_table "fast"]
end

to setup-patches
  ask patches [
    set pcolor green

  ]
  load-map
end

to load-map
  file-open map-file
  let row  ydim
  while [not file-at-end?]
  [
    let linestr file-read-line
    ;show linestr
    let line read-from-string linestr
    let col  0 - xdim
    foreach line [

      [x] ->
      ask patch col row [ set pcolor table:get map_table x  ]
      set col (col + 1)
    ]
  set row (row - 1)
  ]
  file-close
end
@#$#@#$#@
GRAPHICS-WINDOW
414
15
851
453
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
26
28
89
61
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
140
27
203
60
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
17
180
189
213
People
People
0
500
500.0
1
1
NIL
HORIZONTAL

SLIDER
870
422
1042
455
Fire_Speed
Fire_Speed
0
100
50.0
1
1
NIL
HORIZONTAL

CHOOSER
17
126
181
171
map-file
map-file
"exit_dims_2_a.map" "exit_dims_2_b.map" "exit_dims_2_c.map" "exit_dims_4_a.map" "exit_dims_4_b.map" "exit_dims_4_c.map" "exit_dims_6_a.map" "exit_dims_6_b.map" "exit_dims_6_c.map" "exit_dims_8_a.map" "exit_dims_8_b.map" "exit_dims_8_c.map" "chokepoint_1_a.map" "chokepoint_1_b.map" "chokepoint_1_c.map" "chokepoint_1_d.map" "chokepoint_1_e.map" "chokepoint_1_f.map" "chokepoint_2_a.map" "chokepoint_2_b.map" "chokepoint_2_c.map" "chokepoint_2_d.map" "chokepoint_2_e.map" "chokepoint_3_a.map" "chokepoint_3_b.map" "chokepoint_3_c.map" "chokepoint_3_d.map" "better_exit.map" "chokepoint.map" "a.map" "b.map" "c.map" "obstacles.map" "blank.map"
7

TEXTBOX
19
319
169
337
People Speed Distribution
11
0.0
1

SLIDER
15
338
187
371
Slow
Slow
0
100
33.0
1
1
NIL
HORIZONTAL

SLIDER
15
377
187
410
Medium
Medium
0
100
0.0
1
1
NIL
HORIZONTAL

SLIDER
15
415
187
448
Fast
Fast
0
100
0.0
1
1
NIL
HORIZONTAL

PLOT
872
21
1072
171
People
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"Slow People" 1.0 0 -8053223 true "" "plot count turtles with [ color = table:get speed_color_table \"slow\" ]"
"Medium People" 1.0 0 -7171555 true "" "plot count turtles with [ color = table:get speed_color_table \"medium\" ]"
"Fast People" 1.0 0 -15040220 true "" "plot count turtles with [ color = table:get speed_color_table \"fast\" ]"

SWITCH
229
124
400
157
add-person-spacing?
add-person-spacing?
0
1
-1000

TEXTBOX
230
93
380
121
People try to give each other space
11
0.0
1

SWITCH
229
52
401
85
display-path-cost?
display-path-cost?
1
1
-1000

TEXTBOX
234
23
384
51
Show distance to escape patches
11
0.0
1

SLIDER
16
266
190
299
person_path_weight
person_path_weight
0
3
2.0
.1
1
NIL
HORIZONTAL

TEXTBOX
17
234
167
262
How much a person blocks a patch
11
0.0
1

SWITCH
872
380
975
413
set-fire?
set-fire?
1
1
-1000

BUTTON
16
85
126
118
NIL
reset-defaults
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
229
316
379
334
People Speeds
11
0.0
1

SLIDER
223
337
395
370
Slow-Speed
Slow-Speed
0.01
.99
0.1
.01
1
NIL
HORIZONTAL

SLIDER
223
377
395
410
Medium-Speed
Medium-Speed
.01
.99
0.4
.01
1
NIL
HORIZONTAL

SLIDER
223
416
395
449
Fast-Speed
Fast-Speed
.01
.99
0.8
.01
1
NIL
HORIZONTAL

SWITCH
228
199
399
232
people-wait?
people-wait?
0
1
-1000

TEXTBOX
231
166
381
194
People will try to wait for a better path
11
0.0
1

MONITOR
872
195
986
240
NIL
mean-escape-time
17
1
11

SWITCH
227
271
397
304
equal-diagonal-weight?
equal-diagonal-weight?
0
1
-1000

TEXTBOX
228
241
378
269
Treat diagonals as the same distance as 4 main directions
11
0.0
1

MONITOR
871
247
979
292
NIL
max-escape-time
17
1
11

@#$#@#$#@
## WHAT IS IT?

This is the Fall 2020 CSS600 Group Ten project,

by Justin Downes and Chris Smith

prepared for Prof. Dale Rothman

The goal is to simulate the emergency evacuation of a floorplan, for example in the case of fire.

The environment patches include rooms, corridors, and exit areas, as well as patches in normal, burning, and burnt states.

Agents are randomply placed people moving at various speeds and directions, but which can die and block each other.

Maps are editable for layout, patch flammability, number of agents, initial fire locations, agent speed range and plancement.


Prior art for this project includes, but is not limited to:

- Crowd Simulation Modeling Applied to Emergency and Evacuation Simulations using Multi-Agent Systems https://arxiv.org/ftp/arxiv/papers/1303/1303.4692.pdf


- Simulation of pedestrian evacuation route choice using social force model in large-scale public space: Comparison of five evacuation strategies https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6730895/


- Agent Pathing http://www.cs.us.es/~fsancho/?e=131


- A Novel Algorithm for Real-time ProceduralGeneration of Building Floor Plans https://arxiv.org/pdf/1211.5842.pdf


## HOW IT WORKS
Simulation Req's:

Environment- patches

- exit area

- Flammable patches

-- walls

-- floors

-- grass

- Burning

- burnt


Agent actions

- agents have variable speeds

- agents can die

- agents move towards exit area

- agents cant move through each other

- the number of agents is variable

- agents are randomly placed on floor patches

- is there a way to specify agent placement through the UI?



Sim UI features:

- can control flamability of patches

- starting fire spots


### Buttons

setup ; prepare model

go ; run model

reset-defaults ; undo temporary parameter changes


### Sliders

people ; participant count

person_path_weight ; how much a person blocks a path

People Speed Distribution 
- Slow
- Medium
- Fast

People Speeds ; movement rate coefficients
- Slow
- Medium
- Fast

### Switches

map-file ; select floor layouts

display-path-cost ; show distance to escape patches

add-person-spacing ; are people socially distancing?

people-wait ; are people waiting for a better path

set-fire ; whether it's burning

Fire_Speed ; consumption rate

### Plots

People
- y count of people in each speed category remaining
- x time

## THINGS TO NOTICE


## THINGS TO TRY


## EXTENDING THE MODEL


## RELATED MODELS


## HOW TO CITE


## COPYRIGHT AND LICENSE

MIT
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="FireSim" repetitions="1" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <exitCondition>not any? turtles</exitCondition>
    <metric>count turtles</metric>
    <metric>mean-escape-time</metric>
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
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
