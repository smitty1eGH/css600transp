from sqlalchemy import Index, Column, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint, ForeignKey
import stringcase

Base = declarative_base()

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
    assert result_name
    result_type = type(result_name,(Base,), attr_dict)
    assert result_type
    assert result_field_map
    return result_name, result_type, result_field_map

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

class Experiments(Base):
    __tablename__ = "experiments"
    experiments_id = Column(Integer, primary_key=True)
    nlogo_file_path = Column(String)
    nlogo_file_name = Column(String)

class Experiment(Base):
    __tablename__ = "experiment"
    experiment_id = Column( Integer, primary_key=True)
    experiments_id = Column( Integer, ForeignKey('experiments.experiments_id'))
    name = Column(String)
    repetitions = Column(Integer)
    runMetricsEveryStep = Column(Boolean)
    setup = Column(String)
    go = Column(String)
    metric = Column(String)

    def xml(self,sess):
        evs = [e.xml(sess) for e in \
               sess.query(EnumeratedValueSet).filter(EnumeratedValueSet.experiment_id==self.experiment_id)]
        return f'''<experiments><experiment name="{self.name}" repetitions="{self.repetitions}" runMetricsEveryStep="{self.runMetricsEveryStep}">
    <setup>{self.setup}</setup>
    <go>{self.go}</go>
    <metric>{self.metric}</metric>
        {''.join(evs)}
        </experiment></experiments>
        '''

class EnumeratedValueSet(Base):
    __tablename__ = "enumerated_value_set"
    enumerated_value_set_id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiment.experiment_id'))
    variable = Column(String)

    def xml(self,sess):
        '''
        '''
        vs = [f'<value value="{v.value}"/>' for v in \
              sess.query(Value).filter(Value.enumerated_value_set_id==self.enumerated_value_set_id)]
        print(f'what was {vs=}')
        return f'<enumeratedValueSet variable="{self.variable}">{"".join(vs)}</enumeratedValueSet>'

class Value(Base):
    __tablename__ = "value"
    value_id = Column(Integer, primary_key=True)
    enumerated_value_set_id = Column(Integer, ForeignKey('enumerated_value_set.enumerated_value_set_id'))
    value = Column(String)

#class ExitCondition(Base):
#    __tablename__ = "exitCondition"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    PCDATA = Column("PCDATA", BLOB)
#
#
#class Final(Base):
#    __tablename__ = "final"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    PCDATA = Column("PCDATA", BLOB)
#
#
#class SteppedValueSet(Base):
#    __tablename__ = "steppedValueSet"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    variable = Column("variable", BLOB)
#    first = Column("first", BLOB)
#    step = Column("step", BLOB)
#    last = Column("last", BLOB)
#
#
#class TimeLimit(Base):
#    __tablename__ = "timeLimit"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    steps = Column("steps", BLOB)
#
#
