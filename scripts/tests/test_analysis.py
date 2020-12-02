import itertools

import pytest
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import polyfit, polyval
import sqlite3                                   #No value add for SQLAlchemy here

# ALL_FIELDS
#  results_fire_sim_id|run_number             |map_file           |people
# |person_path_weight |slow                   |medium             |fast
# |display_path_cost_p|add_person_spacing_p   |people_wait_p      |equal_diagonal_weight_p
# |slow_speed         |fast_speed             |medium_speed       |set_fire_p
# |fire_speed         |step                   |count_turtles      |mean_escape_time
#
# ANALYSIS_FIELDS
# results_fire_sim_id,run_number,map_file,people,step,count_turtles,mean_escape_time
#
# ATTACH DATABASE 'fire_sim_100people.db' as fs100;
# ATTACH DATABASE 'fire_sim_300people.db' as fs300;
# ATTACH DATABASE 'fire_sim_500people.db' as fs500;
# select count(*) from fs100.results_fire_sim;
# select count(*) from fs300.results_fire_sim;
# select count(*) from fs500.results_fire_sim;
#
# SELECT * FROM fs100.results_fire_sim WHERE map_file='a.map' UNION
# SELECT * FROM fs300.results_fire_sim WHERE map_file='a.map' UNION
# SELECT * FROM fs500.results_fire_sim WHERE map_file='a.map' ;

@pytest.fixture
def conn():
    """Return a memory-only session instance
    """
    conn = sqlite3.connect(':memory:')
    with conn:
        conn.execute("ATTACH DATABASE 'fire_sim_100people.db' as fs100;")
        conn.execute("ATTACH DATABASE 'fire_sim_300people.db' as fs300;")
        conn.execute("ATTACH DATABASE 'fire_sim_500people.db' as fs500;")
    return conn

@pytest.fixture
def map_file_list():
    return ["a.map" ,"b.map" ,"c.map" ,"obstacles.map" ,"blank.map"]

@pytest.fixture
def sql_union():
    return '''SELECT * FROM fs100.results_fire_sim WHERE map_file='a.map' UNION
              SELECT * FROM fs300.results_fire_sim WHERE map_file='a.map' UNION
              SELECT * FROM fs500.results_fire_sim WHERE map_file='a.map' ;'''

@pytest.fixture
def sql_runs0():
    return '''SELECT step, count_turtles, mean_escape_time
              FROM   fs%s00.results_fire_sim
              WHERE  map_file='%s';'''

@pytest.fixture
def sql_runs1(map_file_list):
    return  [x for x in itertools.product([1,3,5],map_file_list )]

@pytest.fixture
def sql_runs2(sql_runs0,sql_runs1):
    return [sql_runs0 % (x[0],x[1]) for x in sql_runs1]

def test_connectivity(conn):
     with conn:
        cur = conn.cursor()
        y = cur.execute('select count(*) from fs100.results_fire_sim;')
        assert y.fetchone()[0] == 27264

def test_union(conn,sql_union):
     with conn:
        cur = conn.cursor()
        y = cur.execute(sql_union)
        z = y.fetchone()
        assert z == (1, 6, 'a.map', 100, 2.0, 25, 50, 25, 0, 0, 1, 1, 0.3, 1.0, 0.75, 0, 50, 0, 100, 0.0)

def test_one_run_len(conn,sql_runs2):
    assert len(sql_runs2[0]) == 127

def test_one_run_load(conn,sql_runs2):
    # (6, 0, 100, 0.0)
     with conn:
        cur = conn.cursor()
        y = cur.execute(sql_runs2[0]).fetchall()
        arr = np.fromiter(y, dtype='i4,i4,f4')
        arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
        assert len(arr) == 3950

def test_one_run_filter(conn,sql_runs2):
     crit = ' AND run_number=1;'
     with conn:
        cur = conn.cursor()
        y = cur.execute(sql_runs2[0].replace(';',crit)).fetchall()
        arr = np.fromiter(y, dtype='i4,i4,f4')
        arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
        assert len(arr) == 143

@pytest.mark.skip
def test_one_run_plot(conn,sql_runs2):
    '''Query for the first run. Polyfit the data. Plot the data, with the polyfit overlaid.
    '''
    out_dir ='../docs/figures/'
    fig, ax = plt.subplots()
    crit = ' AND run_number=1;'
    with conn:
        cur = conn.cursor()
        y = cur.execute(sql_runs2[0].replace(';',crit)).fetchall()
        arr = np.fromiter(y, dtype='i4,i4,f4')
        arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
        coeff = polyfit(arr['step'],arr['count_turtles'],3)
        print(f'{coeff=}') 
        ax.plot(arr['step'],arr['count_turtles'])
        ax.plot(arr['step'],polyval(arr['step'],coeff))
        plt.savefig(f'{out_dir}scrap.png')


def test_one_run_full_map(conn,sql_runs2):
    '''Query for the first run. Polyfit the data. Plot the data, with the polyfit overlaid.
    '''
    out_dir ='../docs/figures/'
    fig, ax = plt.subplots()
    a0=a1=a2=a3=[]
    for i in range(1,31):
        crit = f' AND run_number={i};'
        with conn:
            cur = conn.cursor()
            y = cur.execute(sql_runs2[0].replace(';',crit)).fetchall()
            arr = np.fromiter(y, dtype='i4,i4,f4')
            arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
            coeff = polyfit(arr['step'],arr['count_turtles'],0)
            a0.append(coeff[0])
           #a1.append(coeff[1])
           #a2.append(coeff[2])
           #a3.append(coeff[3])
            ax.plot(arr['step'],arr['count_turtles'])

    a4=[np.average(a0)]#,np.average(a1),np.average(a2),np.average(a3)]
    ax.plot(arr['step'],polyval(arr['step'],a4))
    ax.set_ylabel('people')
    ax.set_xlabel('tick')
    ax.set_title(f'a.map, all runs')
    plt.savefig(f'{out_dir}scrap_{i}.png')
