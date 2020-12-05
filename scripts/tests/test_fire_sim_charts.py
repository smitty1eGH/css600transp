import sqlite3                                   #No value add for SQLAlchemy here

import matplotlib.pyplot as plt
import pytest
import numpy as np


@pytest.fixture
def sql_stats():
    '''To get the same answer as official software, treat our data as a sample and
       divide by n-1. We also need to divide again by n. I think this has to do with the
       sub-querying inflating the numbers by n, but I have not really validated that;
       rather, I beat the numbers into submission.
    '''
    return '''SELECT      D.map_file
                       ,  MIN(D.mean_escape_time)
                       ,  AVG(D.mean_escape_time)
                       ,  MAX(D.mean_escape_time)
                       , (SUM(C.x_minus_mu * C.x_minus_mu)/(C.n-1)) / C.n AS variance
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
def conn():
    return sqlite3.connect('fire_sim.db')


@pytest.fixture
def filter_bits():
    """       i[0]            j  in the tests below
    """
    return [('chokepoint_%s',[1,2,3]),('exit_dims_%s',[2,4,6,8])]

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


def test_do_charts0(conn,sql_stats,filter_bits):
    '''Partition the output into lists of tuples of related stats.

    sample value for l below:
               MAP               MIN    AVG    MAX    VAR
         [ ('exit_dims_2_a.map', 472.0, 491.6, 516.0, 120.4888888888888)
         , ('exit_dims_2_b.map', 474.0, 496.5, 522.0, 184.94444444444443)
         , ('exit_dims_2_c.map', 473.0, 496.0, 524.0, 213.33333333333334)]
    '''
    out_dir ='../docs/figures/'

    with conn:
        cur = conn.cursor()
        rows = cur.execute(sql_stats).fetchall()
        for i in filter_bits:
            for j in i[1]:
                range_=[]
                domain=[]
                l = [m for m in rows if m[0].startswith( i[0] % j )]
                for n in l:
                    range_.append(n[2])
                    domain.append(n[0][:-4][-1:]) #just the letter the right of the period
                #print(f'{range_=}\n{domain=}')
                fig, ax = plt.subplots()
                ax.scatter(domain,range_)
                ax.set_ylabel('average escape steps')
                ax.set_xlabel('map letter')
                ax.set_title(f'map {i[0] % j}')
                plt.savefig(f'{out_dir}chart_{i[0] % j}.png')
