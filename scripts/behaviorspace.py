from sqlalchemy import Index, Column, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint, ForeignKey

Base = declarative_base()


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
