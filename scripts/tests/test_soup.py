import pytest
import re

from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

from behaviorspace import Base,Experiments,Experiment,EnumeratedValueSet,Value

#from functions import rxe, rxi

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

def test_load(behsp_xml,sess):

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

            for evs in e.find_all('enumeratedValueSet'):
                vname = evs.attrs['variable']
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id,variable=vname)
                add_commit(sess,enu)
                for v in evs.find_all('value'):
                    w = Value(enumerated_value_set_id=enu.enumerated_value_set_id,value=v.attrs['value'])
                    sess.add(w)
                    sess.commit()

            for ex in sess.query(Experiment).filter(Experiment.experiment_id==1):
                print(ex.xml(sess))
