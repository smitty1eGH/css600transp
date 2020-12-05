from csv import DictReader
import keyword
from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
import pytest
from sqlalchemy import create_engine, inspect, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column, MetaData
from sqlalchemy.types import *
import stringcase

from constants import (
    filen,
    RX,
    BEHAVIOR_SPACE,
    EXTRACT,
    INSERT,
    RX0,
    RX1,
    RX2,
    XML_TEMPLATE,
)

from behaviorspace import (
    get_result_table,
    add_commit,
    get_exp_header,
    Base,
    Experiments,
    Experiment,
    EnumeratedValueSet,
    Value,
    ResultsFireSim,
)


# All of the interface elements are fixtures, so that their ranges are controlled from within the python code.

# ==NetLogo UI fixtures==
@pytest.fixture
def map_file():
    """
    <enumeratedValueSet variable="map-file"> <value value="&quot;blank.map&quot;"/> </enumeratedValueSet>

    map file names:
    "a.map" ,"b.map" ,"c.map" ,"obstacles.map" ,"blank.map"
    """
    cur_map = "chokepoint_1_a.map"
    return f'<enumeratedValueSet variable="map-file"> <value value="&quot;{cur_map}&quot;"/> </enumeratedValueSet>'


@pytest.fixture
def map_file_interp():
    """
    "a.map" ,"b.map" ,"c.map" ,"obstacles.map" ,"blank.map"
    """
    return '<enumeratedValueSet variable="map-file"> <value value="&quot;%s&quot;"/> </enumeratedValueSet>'

@pytest.fixture
def map_file_list():
    #return ["a.map" ,"b.map" ,"c.map" ,"obstacles.map" ,"blank.map"]
    choke_nums=[1,2,3]
    choke_lets=['a','b','c','d']
    choke_temp='chokepoint_%s_%s.map'
    exits_nums=[2,4,6,8]
    exits_lets=['a','b','c']
    exits_temp='exit_dims_%s_%s.map'
    return choke_nums, choke_lets, choke_temp, exits_nums, exits_lets, exits_temp,


@pytest.fixture
def people():
    """
    <enumeratedValueSet variable="People"> <value value="500"/> </enumeratedValueSet>

    Integer between 1 and 500
    """
    people = 500
    return f'<enumeratedValueSet variable="People"> <value value="{people}"/> </enumeratedValueSet>'


@pytest.fixture
def person_path_weight():
    """
    <enumeratedValueSet variable="person_path_weight"> <value value="2"/> </enumeratedValueSet>

    Float from 0.0 to 2.0 in steps of 0.1
    """
    ppw = 2.0
    return f'<enumeratedValueSet variable="person_path_weight"> <value value="{ppw}"/> </enumeratedValueSet>'


@pytest.fixture
def people_speed():
    """People Speed Distribution, integer from 0 to 100 representing a percentage of PEOPLE

    <enumeratedValueSet variable="Slow"> <value value=""/> </enumeratedValueSet>
    <enumeratedValueSet variable="Medium"> <value value=""/> </enumeratedValueSet>
    <enumeratedValueSet variable="Fast"> <value value=""/> </enumeratedValueSet>
    """
    slow = 100
    medium = 0
    fast = 100 - medium - slow
    assert slow + medium + fast == 100
    return f"""<enumeratedValueSet variable="Slow"> <value value="{slow}"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Medium"> <value value="{medium}"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Fast"> <value value="{fast}"/> </enumeratedValueSet>
    """


# Predicates
@pytest.fixture
def display_path_cost_p():
    """
    <enumeratedValueSet variable="display-path-cost?"> <value value="true"/> </enumeratedValueSet>
    """
    return '<enumeratedValueSet variable="display-path-cost?"> <value value="false"/> </enumeratedValueSet>'


@pytest.fixture
def add_person_spacing_p():
    """
    <enumeratedValueSet variable="add-person-spacing?"> <value value="true"/> </enumeratedValueSet>
    """
    return '<enumeratedValueSet variable="add-person-spacing?"> <value value="true"/> </enumeratedValueSet>'


@pytest.fixture
def people_wait_p():
    """
    <enumeratedValueSet variable="people-wait?"> <value value="true"/> </enumeratedValueSet>
    """
    return '<enumeratedValueSet variable="people-wait?"> <value value="true"/> </enumeratedValueSet>'


@pytest.fixture
def equal_diagonal_weight_p():
    """
    <enumeratedValueSet variable="equal-diagonal-weight?"> <value value="true"/> </enumeratedValueSet>
    """
    return '<enumeratedValueSet variable="equal-diagonal-weight?"> <value value="true"/> </enumeratedValueSet>'


@pytest.fixture
def people_move_rates():
    """
    Slow < Medium < Fast
    <enumeratedValueSet variable="Slow-Speed"> <value value="0.1"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Medium-Speed"> <value value="0.4"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Fast-Speed"> <value value="0.8"/> </enumeratedValueSet>
    """
    slow = 0.3
    medium = 0.75
    fast = 1.0
    assert slow < medium < fast
    return f"""<enumeratedValueSet variable="Slow-Speed"> <value value="{slow}"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Medium-Speed"> <value value="{medium}"/> </enumeratedValueSet>
    <enumeratedValueSet variable="Fast-Speed"> <value value="{fast}"/> </enumeratedValueSet> """


# Fire values
@pytest.fixture
def set_fire_p():
    """
    <enumeratedValueSet variable="set-fire?"> <value value="false"/> </enumeratedValueSet>
    """
    return '<enumeratedValueSet variable="set-fire?"> <value value="false"/> </enumeratedValueSet>'


@pytest.fixture
def fire_speed():
    """
    <enumeratedValueSet variable="Fire_Speed"> <value value="50"/> </enumeratedValueSet>
    """
    fire_spd = 50
    return f'<enumeratedValueSet variable="Fire_Speed"> <value value="{fire_spd}"/> </enumeratedValueSet>'


# == Derived ==
@pytest.fixture
def get_beshp_xml(
    map_file,
    people,
    person_path_weight,
    people_speed,
    display_path_cost_p,
    add_person_spacing_p,
    people_wait_p,
    equal_diagonal_weight_p,
    people_move_rates,
    set_fire_p,
    fire_speed,
):
    """<experiments>
    <experiment name="FireSim" repetitions="1" runMetricsEveryStep="false">
      <setup>setup</setup>
      <go>go</go>
      <exitCondition>not any? turtles</exitCondition>
      <metric>count turtles</metric>
      <metric>mean-escape-time</metric>
      <enumeratedValueSet variable="map-file"> <value value="&quot;blank.map&quot;"/> </enumeratedValueSet>
      <enumeratedValueSet variable="person_path_weight"> <value value="2"/> </enumeratedValueSet>
      <enumeratedValueSet variable="add-person-spacing?"> <value value="true"/> </enumeratedValueSet>
      <enumeratedValueSet variable="equal-diagonal-weight?"> <value value="true"/> </enumeratedValueSet>
      <enumeratedValueSet variable="display-path-cost?"> <value value="true"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Fire_Speed"> <value value="50"/> </enumeratedValueSet>
      <enumeratedValueSet variable="people-wait?"> <value value="true"/> </enumeratedValueSet>
      <enumeratedValueSet variable="set-fire?"> <value value="false"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Slow-Speed"> <value value="0.1"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Medium-Speed"> <value value="0.4"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Fast-Speed"> <value value="0.8"/> </enumeratedValueSet>
      <enumeratedValueSet variable="People"> <value value="500"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Slow"> <value value="33"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Medium"> <value value="0"/> </enumeratedValueSet>
      <enumeratedValueSet variable="Fast"> <value value="0"/> </enumeratedValueSet>
    <metric>count turtles</metric>
    """
    return f"""<experiments>
  <experiment name="FireSim" repetitions="1" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <exitCondition>not any? turtles</exitCondition>
    <metric>mean-escape-time</metric>
    {map_file}{people}{person_path_weight}{people_speed}{display_path_cost_p}{add_person_spacing_p}{people_wait_p}{equal_diagonal_weight_p}{people_move_rates}{set_fire_p}{fire_speed}
  </experiment> </experiments>
    """

@pytest.fixture
def reps():
    return 10


@pytest.fixture
def get_beshp_xml_interp(
    reps,
    map_file_interp,
    people,
    person_path_weight,
    people_speed,
    display_path_cost_p,
    add_person_spacing_p,
    people_wait_p,
    equal_diagonal_weight_p,
    people_move_rates,
    set_fire_p,
        fire_speed,
):
    '''NOTE: map_file_interp has a % in it for later inerpolation
       def map_file_interp():
           ~eturn '<enumeratedValueSet variable="map-file"> <value value="&quot;%s&quot;"/> </enumeratedValueSet>'
    <metric>count turtles</metric>
    '''
    return f"""<experiments>
  <experiment name="FireSim" repetitions="{reps}" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <exitCondition>not any? turtles</exitCondition>
    <metric>mean-escape-time</metric>
    {map_file_interp}{people}{person_path_weight}{people_speed}{display_path_cost_p}{add_person_spacing_p}{people_wait_p}{equal_diagonal_weight_p}{people_move_rates}{set_fire_p}{fire_speed}
  </experiment> </experiments>
    """

# ==Housekeeping fixtures==
@pytest.fixture
def netlogo_sh():
    """TODO: move the path to the NetLogo invocation script out to a configuration file and load that here."""
    return "/home/smitty/bin/NetLogo6.1.1/netlogo-headless.sh"


@pytest.fixture
def netlogo_args():
    """We can write the XML out to a path via --setup-file,
    We can write the results to a path via --table
    """
    return {
        "model": "/home/smitty/proj/css600transp/css600transp/FireSim.nlogo",
        "setup-file": "setup-file.xml",
        "experiment": "FireSim",
        "table": "-",
    }


@pytest.fixture
def behsp_xml():
    h = None
    with open(filen, "r") as f:
        rx = re.compile(RX)
        g = f.read()
        h = rx.split(g)
    return h[BEHAVIOR_SPACE]


@pytest.fixture
def sess():
    """Return a memory-only session instance"""
    engine = create_engine("sqlite://", echo=True)
    with engine.begin() as conn:
        conn.execute("ATTACH DATABASE ':memory:' AS placebo")
    Base.metadata.create_all(engine)
    sess = sessionmaker(bind=engine)()
    return sess


@pytest.fixture
def sess_file():
    """Return a memory-only session instance"""
    engine = create_engine("sqlite:///fire_sim.db", echo=True)
    Base.metadata.create_all(engine)
    sess = sessionmaker(bind=engine)()
    return sess


@pytest.fixture
def try_result_name():
    return "ResultsFireSim"


@pytest.fixture
def result_field_map():
    """Recent pythons have an ordered dictionary, so we can be comfortable with these columns
        "count turtles": "count_turtles",
        "[step]": "step",
    """
    return {
        "[run number]": "run_number",
        "map-file": "map_file",
        "People": "people",
        "person_path_weight": "person_path_weight",
        "Slow": "slow",
        "Medium": "medium",
        "Fast": "fast",
        "display-path-cost?": "display_path_cost_p",
        "add-person-spacing?": "add_person_spacing_p",
        "people-wait?": "people_wait_p",
        "equal-diagonal-weight?": "equal_diagonal_weight_p",
        "Slow-Speed": "slow_speed",
        "Medium-Speed": "medium_speed",
        "Fast-Speed": "fast_speed",
        "set-fire?": "set_fire_p",
        "Fire_Speed": "fire_speed" ,
        "mean-escape-time": "mean_escape_time",
    }


def fix_bools(line):
    fs = [
        "display_path_cost_p",
        "add_person_spacing_p",
        "people_wait_p",
        "equal_diagonal_weight_p",
        "set_fire_p",
    ]
    for f in fs:
        if line[f] == "false":
            line[f] = False
        else:
            line[f] = True

def get_map_files(map_file_list):
    for x in map_file_list[0]:
        for y in map_file_list[1]:
            yield map_file_list[2] % (x,y)
        if x==1:
            yield map_file_list[2] % (x,'e')
            yield map_file_list[2] % (x,'f')
        elif x==2:
            yield map_file_list[2] % (x,'e')

    for x in map_file_list[3]:
        for y in map_file_list[4]:
            yield map_file_list[5] % (x,y)

# ==Simulation Driver==
@pytest.mark.skip
def test_get_map_files(map_file_list):
    for f in get_map_files(map_file_list):
        print(f)

@pytest.mark.skip
def test_fire_sim_persist(
    netlogo_sh, netlogo_args, sess_file, get_beshp_xml, result_field_map
):
    """This is a persistent test of whether the thing works, without persisting the data.

    1. Build the NetLogo args vector for invocation
    2. Write a setup-file to contain the model arguments
    3. Invoke NetLogo
    4. Write captured output do Db
    """
    START_DATA = 8
    ELIDE_LAST = -1

    # 1.
    args = [netlogo_sh]
    for k, v in netlogo_args.items():
        args.append(f"--{k}")
        args.append(v)

    # 2.
    with open("setup-file.xml", "w") as f:
        f.write(get_beshp_xml)

    # 3.
    result = subprocess.run(args, capture_output=True)
    lines = f"{result.stdout=}".split("\\n")[START_DATA:]
    print(f'{lines=}')

    # 4.
    fnames = result_field_map.values()
    print(f'{fnames=}')
    dr = DictReader(lines[:ELIDE_LAST], fieldnames=fnames, restkey="restkey")

   # for line in dr:
   #     if "restkey" in line:
   #         del line["restkey"]
   #     fix_bools(line)

   #     x = ResultsFireSim(**line)
   #     add_commit(sess_file, x)
   #     sess_file.add(x)

#@pytest.mark.skip
def test_fire_sim_persist_interp(
    netlogo_sh, netlogo_args, sess_file, get_beshp_xml_interp, result_field_map, map_file_list
):
    START_DATA = 8
    ELIDE_LAST = -1

    args = [netlogo_sh]
    for k, v in netlogo_args.items():
        args.append(f"--{k}")
        args.append(v)

    for m in get_map_files(map_file_list):
        print(f'working on map {m}')
        with open("setup-file.xml", "w") as f:
            f.write(get_beshp_xml_interp % m)

        result = subprocess.run(args, capture_output=True)
        lines = f"{result.stdout=}".split("\\n")[START_DATA:]

        fnames = result_field_map.values()
        dr = DictReader(lines[:ELIDE_LAST], fieldnames=fnames, restkey="restkey")

        for line in dr:
            if "restkey" in line:
                del line["restkey"]
            fix_bools(line)

            x = ResultsFireSim(**line)
            add_commit(sess_file, x)
            sess_file.add(x)
