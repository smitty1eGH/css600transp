from datetime import datetime, timedelta
import csv
from math import sqrt

import sqlite3                                   #No value add for SQLAlchemy here

import matplotlib.pyplot as plt
#import mplfinance as mpf
#import pandas as pd
import pytest


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

@pytest.fixture
def sql_stats():
    '''To get the same answer as official software, treat our data as a population and
         divide by n.
    '''
    return '''SELECT      D.map_file
                       ,  ROUND( MIN(D.mean_escape_time) )
                       ,  ROUND( AVG(D.mean_escape_time) )
                       ,  ROUND( MAX(D.mean_escape_time) )
                       ,  ROUND( (SUM(C.x_minus_mu * C.x_minus_mu)/ C.n)) AS variance
              FROM       (
                          SELECT      A.map_file
                                   ,  A.mean_escape_time - mu.mu          AS x_minus_mu
                                   ,  mu.n
                          FROM        results_fire_sim                    AS A
                          INNER JOIN (
                                      SELECT   map_file
                                             , AVG(mean_escape_time)      AS mu
                                             , COUNT(mean_escape_time)    AS n
                                      FROM     results_fire_sim
                                      GROUP BY map_file
                                     )                                    AS mu
                                  ON  A.map_file = mu.map_file
                         )                                                AS C
              INNER JOIN results_fire_sim                                 AS D
                      ON D.map_file = C.map_file
              GROUP BY   D.map_file;'''

@pytest.fixture
def conn_choke():
    """Return a memory-only session instance
    """
    conn = sqlite3.connect(':memory:')
    with conn:
        conn.execute("ATTACH DATABASE 'fire_sim_chokepoint_100.db' as c100;")
        conn.execute("ATTACH DATABASE 'fire_sim_chokepoint_200.db' as c200;")
        conn.execute("ATTACH DATABASE 'fire_sim_chokepoint_300.db' as c300;")
        conn.execute("ATTACH DATABASE 'fire_sim_chokepoint_400.db' as c400;")
        conn.execute("ATTACH DATABASE 'fire_sim_chokepoint_500.db' as c500;")
    return conn

@pytest.fixture
def sql_stats2():
    '''The chokepoint map varied the number of people.
    '''
    return '''
              SELECT      D.map_file
                       ,  D.people, D.slow, D.medium, D.fast
                       ,  D.slow_speed,D.fast_speed,D.medium_speed
                       ,  ROUND( MIN(D.mean_escape_time) )
                       ,  ROUND( AVG(D.mean_escape_time) )
                       ,  ROUND( MAX(D.mean_escape_time) )
                       ,  ROUND( (SUM(C.x_minus_mu * C.x_minus_mu)/ C.n)) AS variance
              FROM       (
                          SELECT      A.map_file
                                   ,  A.people, A.slow, A.medium, A.fast
                                   ,  A.slow_speed,A.fast_speed,A.medium_speed
                                   ,  A.mean_escape_time - mu.mu          AS x_minus_mu
                                   ,  mu.n
                          FROM        results_fire_sim                    AS A
                          INNER JOIN (
                                      SELECT   map_file
                                             , people, slow, medium, fast
                                             , slow_speed,fast_speed,medium_speed
                                             , AVG(mean_escape_time)      AS mu
                                             , COUNT(mean_escape_time)    AS n
                                      FROM     results_fire_sim
                                      GROUP BY map_file
                                             , people, slow, medium, fast
                                             , slow_speed,fast_speed,medium_speed
                                     )                                    AS mu
                                  ON  A.map_file = mu.map_file
                                 AND  A.people   = mu.people AND A.slow = mu.slow
                                 AND  A.medium   = mu.medium AND A.fast = mu.fast
                         )                                                AS C
              INNER JOIN results_fire_sim                                 AS D
                      ON D.map_file = C.map_file
              GROUP BY   D.map_file
                       , D.people, D.slow, D.medium, D.fast
                       , D.slow_speed,D.fast_speed,D.medium_speed
           '''

@pytest.fixture
def sql_stats3(sql_stats2):
    y = [' c%s00 ' % x for x in range(1,6)]
    z = [sql_stats2.replace(' results_fire_sim', f' {x}.results_fire_sim') for x in y]
    return ' UNION '.join(z) + ';'


@pytest.fixture
def sql_stats4():
    y = [' c%s00 ' % x for x in range(1,6)]
    z = [f'SELECT * FROM {x}.results_fire_sim' for x in y]
    return ' UNION '.join(z) + ';'


@pytest.fixture
def conn():
    return sqlite3.connect('fire_sim.db')


@pytest.fixture
def filter_bits():
    """       i[0]            j  in the tests below
    """
    return [('chokepoint_%s',[1,2,3]),('exit_dims_%s',[2,4,6,8])]

@pytest.mark.skip
def test_do_partition(conn,sql_stats,filter_bits):
    '''Partition the output into lists of tuples of related stats.
    '''
    with conn:
        cur = conn.cursor()
        rows = cur.execute(sql_stats).fetchall()
        for i in filter_bits:
            for j in i[1]:
                l = [m for m in rows if m[0].startswith( i[0] % j )]
                print(l)
                print()

@pytest.mark.skip
def test_show_union(sql_stats3):
    print(sql_stats3)

def test_dump_union(result_field_map,conn_choke,sql_stats3,sql_stats4):
    fs = ['map_file', 'people', 'slow', 'medium', 'fast', 'slow_speed','fast_speed','medium_speed','min', 'avg', 'max', 'variance']
    with conn_choke:
        cur = conn_choke.cursor()
        rows = cur.execute(sql_stats3)

        with open('fire_sim_analysis.csv','w') as f:
            g = csv.writer(f)
            g.writerow(fs)
            for m in rows:
                g.writerow(m)

        rows = cur.execute(sql_stats4)
        with open('fire_sim.csv','w') as f:
            g = csv.writer(f)
            g.writerow(result_field_map.values())
            for m in rows:
                g.writerow(m)

@pytest.mark.skip
def test_do_charts0(conn,sql_stats,filter_bits):
    '''Partition the output into lists of tuples of related stats.

    sample value for l below:
               MAP               MIN    AVG    MAX    VAR
         [ ('exit_dims_2_a.map', 472.0, 491.6, 516.0, 120.4888888888888)
         , ('exit_dims_2_b.map', 474.0, 496.5, 522.0, 184.94444444444443)
         , ('exit_dims_2_c.map', 473.0, 496.0, 524.0, 213.33333333333334)]

    To get the data into ohlc format for the candlestic:

    open  = avg - sqrt(var)
    high  = max
    low   = min
    close = avg + sqrt(var)

    '''
    out_dir = '../docs/figures/'

    out = open('candlestic_data.txt','w')
    with conn:
        cur = conn.cursor()
        rows = cur.execute(sql_stats).fetchall()
        for i in filter_bits:
            for j in i[1]:
                out.write(f'{i[0] % j}\n')
                data=[]
                labels=[]
                l = [m for m in rows if m[0].startswith( i[0] % j )]
                for d,n in enumerate(l):
                    labels.append(n[0][:-4][-1:]) #letter
                    data.append([datetime.now() + timedelta(days=d)
                                ,n[2]-sqrt(n[4])
                                ,n[3]
                                ,n[1]
                                ,n[2]+sqrt(n[4])])
                out.write(str(data))
                out.write('\n--\n')
                #print(f'{data=}')
               #pda = pd.DataFrame.from_records(data,index='Date',columns=['Date','Open','High','Low','Close'])
               #pda.index.name = 'letter'
               #pda.shape
               #print(f'{pda=}')
    out.close()

         #      ax.scatter(domain,range_)
         #   ax.set_ylabel('average escape steps')
         #   ax.set_xlabel('map letter')
         #   ax.set_title(f'map {i[0] % j}')
         #   plt.savefig(f'{out_dir}chart_{i[0] % j}.png')

@pytest.mark.skip
def test_do_chokepoint(conn,sql_stats):
    '''Partition the output into lists of tuples of related stats.

    To get the data into ohlc format for the candlestic:

    open  = avg - sqrt(var)
    high  = max
    low   = min
    close = avg + sqrt(var)

    '''
    out_dir = '../docs/figures/'

    out = open('candlestic_data.txt','w')
    with conn:
        cur = conn.cursor()
        rows = cur.execute(sql_stats).fetchall()
        data=[]
        labels=[]
        l = [m for m in rows if m[0].startswith( i[0] % j )]
        for d,n in enumerate(l):
            labels.append(n[0][:-4][-1:]) #letter
            data.append([datetime.now() + timedelta(days=d)
                        ,n[2]-sqrt(n[4])
                        ,n[3]
                        ,n[1]
                        ,n[2]+sqrt(n[4])])
        out.write(str(data))
        out.write('\n--\n')
        #print(f'{data=}')
        #pda = pd.DataFrame.from_records(data,index='Date',columns=['Date','Open','High','Low','Close'])
        #pda.index.name = 'letter'
        #pda.shape
        #print(f'{pda=}')
    out.close()

         #      ax.scatter(domain,range_)
         #   ax.set_ylabel('average escape steps')
         #   ax.set_xlabel('map letter')
         #   ax.set_title(f'map {i[0] % j}')
         #   plt.savefig(f'{out_dir}chart_{i[0] % j}.png')
