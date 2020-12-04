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

@pytest.fixture
def sql_aggr(sql_runs1):
    return ['''SELECT   step, avg(count_turtles), avg(mean_escape_time)
               FROM     fs%s00.results_fire_sim
               WHERE    map_file='%s'
               GROUP BY step''' % (x[0],x[1]) for x in sql_runs1]


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
        coeff = polyfit(arr['step'],arr['count_turtle s'],3)
        print(f'{coeff=}') 
        ax.plot(arr['step'],arr['count_turtles'])
        ax.plot(arr['step'],polyval(arr['step'],coeff))
        plt.savefig(f'{out_dir}scrap.png')


@pytest.mark.skip
def test_one_run_full_map(conn,map_file_list,sql_runs2,sql_aggr):
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
            coeff = polyfit(arr['step'],arr['count_turtles'],3)
            ax.plot(arr['step'],arr['count_turtles'])

    with conn:
        cur = conn.cursor()
        y = cur.execute(sql_aggr % (1,map_file_list[0])).fetchall()
        arr = np.fromiter(y, dtype='i4,f4,f4')
        arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
        coeff = polyfit(arr['step'],arr['count_turtles'],3)
        print(f'{coeff=}')
        ax.plot(arr['step'],polyval(arr['step'],coeff))
    ax.set_ylabel('people')
    ax.set_xlabel('tick')
    ax.set_title(f'a.map, all runs with aggregate')
    plt.savefig(f'{out_dir}scrap_{i}.png')

@pytest.mark.skip
def test_one_run_full_map(conn,map_file_list,sql_runs2,sql_aggr):
    '''Show the aggregates for the files for each map
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
            coeff = polyfit(arr['step'],arr['count_turtles'],3)
            ax.plot(arr['step'],arr['count_turtles'])

    with conn:
        cur = conn.cursor()
        y = cur.execute(sql_aggr % (1,map_file_list[0])).fetchall()
        arr = np.fromiter(y, dtype='i4,f4,f4')
        arr.dtype.names = ['step', 'count_turtles', 'mean_escape_time']
        coeff = polyfit(arr['step'],arr['count_turtles'],3)
        print(f'{coeff=}')
        ax.plot(arr['step'],polyval(arr['step'],coeff))
    ax.set_ylabel('people')
    ax.set_xlabel('tick')
    ax.set_title(f'a.map, all runs with aggregate')
    plt.savefig(f'{out_dir}scrap_{i}.png')
