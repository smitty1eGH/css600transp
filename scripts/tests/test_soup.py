from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import  Column
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

from behaviorspace import get_result_table,add_commit,get_exp_header,Base,Experiments,Experiment,EnumeratedValueSet,Value

#from functions import rxe, rxi

@pytest.fixture
def netlogo_sh():
    return '/home/smitty/bin/NetLogo6.1.1/netlogo-headless.sh'


@pytest.fixture
def netlogo_args():
    '''We can write the XML out to a path via --setup-file,
       We can write the results to a path via --table
    '''
    return {'model':'/home/smitty/proj/css600transp/css600transp/FireSim.nlogo',
            'experiment':'FireSim',
            'table':'-',
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
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def try_result_name():
    return 'ResultsFireSim1'

@pytest.fixture
def result_field_map():
    return {'map-file': 'map_file', 'person_path_weight': 'person_path_weight', 'Medium': 'Medium', 'add-person-spacing?': 'add_person_spacing_p', 'equal-diagonal-weight?': 'equal_diagonal_weight_p', 'display-path-cost?': 'display_path_cost_p', 'Fire_Speed': 'Fire_Speed', 'Fast-Speed': 'Fast_Speed', 'Slow': 'Slow', 'people-wait?': 'people_wait_p', 'set-fire?': 'set_fire_p', 'Slow-Speed': 'Slow_Speed', 'People': 'People', 'Fast': 'Fast', 'Medium-Speed': 'Medium_Speed'}

@pytest.fixture
def beh_sp_path():
    return Path()

@pytest.fixture
def parsed_nlogo(behsp_xml,sess):
    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
    add_commit(sess,exps)
    soup = BeautifulSoup(behsp_xml,'lxml-xml')
    for e in soup.experiments:
        if e.name != None:
            name, repetitions, runMetricsEveryStep, setup, go, metric = get_exp_header(e)
            ex = Experiment(experiments_id=exps.experiments_id, name=name, repetitions=repetitions, setup=setup, go=go, metric=metric)
            add_commit(sess,ex)

            result_table_name = f'results_{name}_{ex.experiment_id}'
            result_table_fields = []

            for evs in e.find_all('enumeratedValueSet'):
                vname = evs.attrs['variable']
                result_table_fields.append(vname)
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id,variable=vname)
                add_commit(sess,enu)
                for v in evs.find_all('value'):
                    w = Value(enumerated_value_set_id=enu.enumerated_value_set_id,value=v.attrs['value'])
                    sess.add(w)
                    sess.commit()

            for ex in sess.query(Experiment).filter(Experiment.experiment_id==1):
                print(ex.xml(sess))
            return get_result_table(result_table_name,result_table_fields)

@pytest.mark.skip
def test_extract(behsp_xml):
    soup = BeautifulSoup(behsp_xml,'lxml-xml')
    for e in soup.experiments:
        if e.name != None:
            print(f'{e.attrs["name"]=}\t{e.repetitions=}\t{e.runMetricsEveryStep=}')
            for c in e.children:
                if c.name == 'setup':
                    print(c.string)
                elif c.name == 'go':
                    print(c.string)
                elif c.name == 'metric':
                    print(c.string)

            for evs in e.find_all('enumeratedValueSet'):
                vname = evs.attrs['variable']
                v = evs.find('value')
                vval = v.attrs['value']
                print(f'{vname=}\t{vval=}')

@pytest.mark.skip
def test_load(behsp_xml,sess):

    def get_result_table(result_table_name,result_table_fields):
        '''Calculate a SQLAlchemy Class for the desired experiment.
           Return: the calculated name, the class, and a map of how the data fields
             in the NetLogo output map to what the python class's members are named.
        '''
        def fix_name(f):
            return f.replace('-','_').replace('?','_p')

        attr_dict={'__tablename__':result_table_name
                 ,f'{result_table_name}_id':Column(Integer,primary_key=True) }

        result_field_map = {}
        for f in result_table_fields:
            g=fix_name(f)
            result_field_map[f]=g
            attr_dict[g]=Column(Float)

        result_name =stringcase.pascalcase(fix_name(result_table_name).replace('_',''))
        return result_name, type(result_name,(Base,), attr_dict),result_field_map

    def add_commit(sess,obj):
        sess.add(obj)
        sess.commit()

    def get_exp_header(exp):
        name = repetitions = runMetricsEveryStep = setup = go = metric = None
        name = exp.attrs["name"]
        repetitions = exp.repetitions
        runMetricsEveryStep=exp.runMetricsEveryStep
        for c in exp.children:
            if c.name == 'setup':
                setup = c.string
            elif c.name == 'go':
                go = c.string
            elif c.name == 'metric':
                metric = c.string
        return name, repetitions, runMetricsEveryStep, setup, go, metric

    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
    add_commit(sess,exps)
    soup = BeautifulSoup(behsp_xml,'lxml-xml')
    for e in soup.experiments:
        if e.name != None:
            name, repetitions, runMetricsEveryStep, setup, go, metric = get_exp_header(e)
            ex = Experiment(experiments_id=exps.experiments_id, name=name, repetitions=repetitions, setup=setup, go=go, metric=metric)
            add_commit(sess,ex)

            result_table_name = f'results_{name}_{ex.experiment_id}'
            result_table_fields = []

            for evs in e.find_all('enumeratedValueSet'):
                vname = evs.attrs['variable']
                result_table_fields.append(vname)
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id,variable=vname)
                add_commit(sess,enu)
                for v in evs.find_all('value'):
                    w = Value(enumerated_value_set_id=enu.enumerated_value_set_id,value=v.attrs['value'])
                    sess.add(w)
                    sess.commit()

            for ex in sess.query(Experiment).filter(Experiment.experiment_id==1):
                print(ex.xml(sess))
            result_name,result_table,result_field_map = get_result_table(result_table_name,result_table_fields)
            print(f'{result_name=}\t{result_field_map=}')

def test_parse_output(parsed_nlogo,beh_sp_path,netlogo_sh,netlogo_args):
    class_name, ClassName, class_field_map=parsed_nlogo
    args = [netlogo_sh]
    for k,v in netlogo_args.items():
        args.append(f'--{k}')
        args.append(v)
    result = subprocess.run(args, capture_output=True)
    print(f'{" ".join(result.args)}')
    print(f'{result.stderr=}')
    print(f'{result.stdout=}')

