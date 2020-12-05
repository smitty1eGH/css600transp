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
    return sqlite3.connect('../fire_sim.db')


@pytest.fixture
def filter_bits():
    return [('chokepoint_',[1,2,3]),('exit_dims_',[2,4,6,8])]

def test_do_filter(conn,sql_stats,filter_bits):
    with conn:
        cur = conn.cursor()
        y = cur.execute(sql_stats).fetchall()
        [print(z) for z in y]
