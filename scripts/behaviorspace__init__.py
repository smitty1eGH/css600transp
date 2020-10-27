from sqlalchemy import Index, Column, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint

Base = declarative_base()


class Experiments(Base):
    __tablename__ = "experiments"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)


class Experiment(Base):
    __tablename__ = "experiment"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiments = Column("foreign_key_experiments", INTEGER)
    name = Column("name", BLOB)


class Setup(Base):
    __tablename__ = "setup"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    PCDATA = Column("PCDATA", BLOB)


class Go(Base):
    __tablename__ = "go"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    PCDATA = Column("PCDATA", BLOB)


class Metric(Base):
    __tablename__ = "metric"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    PCDATA = Column("PCDATA", BLOB)


class ExitCondition(Base):
    __tablename__ = "exitCondition"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    PCDATA = Column("PCDATA", BLOB)


class Final(Base):
    __tablename__ = "final"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    PCDATA = Column("PCDATA", BLOB)


class SteppedValueSet(Base):
    __tablename__ = "steppedValueSet"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    variable = Column("variable", BLOB)
    first = Column("first", BLOB)
    step = Column("step", BLOB)
    last = Column("last", BLOB)


class TimeLimit(Base):
    __tablename__ = "timeLimit"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    steps = Column("steps", BLOB)


class EnumeratedValueSet(Base):
    __tablename__ = "enumeratedValueSet"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_experiment = Column("foreign_key_experiment", INTEGER)
    variable = Column("variable", BLOB)


class Value(Base):
    __tablename__ = "value"
    primary_key = Column("primary_key", INTEGER, primary_key=True)
    seq = Column("seq", INTEGER)
    foreign_key_enumeratedValueSet = Column("foreign_key_enumeratedValueSet", INTEGER)
    value = Column("value", BLOB)
