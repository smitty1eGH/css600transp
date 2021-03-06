
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
