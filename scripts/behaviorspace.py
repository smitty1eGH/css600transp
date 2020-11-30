from sqlalchemy import Index, Column, CheckConstraint, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import instrumentation, attributes
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint, ForeignKey, SchemaItem
import stringcase

Base = declarative_base()


def _set_callable(state, dict_, key, callable_):
    fn = InstanceState._instance_level_callable_processor(state.manager, callable_, key)
    fn(state, dict_, None)


def get_result_table(
    string_fields, result_table_name, result_table_fields, runMetricsEveryStep, metric
):
    """Calculate a SQLAlchemy Class for the desired experiment.
    Return: the calculated name, the class, and a map of how the data fields
      in the NetLogo output map to what the python class's members are named.
    METRIC is the arbitrary fields added at the end, in addition to the tick number,
       e.g. [tick, 'count turtles']
    """
    klass = None  # To be used in the constructor object below, does not exist
    #  until the type has been calculated
    def constructor(self, **kwargs):
        """Loose constructor function that will be bound in attr_dict below.
        KWARGS will be supplied downstream.
        """
        self.__dict__.update(kwargs)
        super(Base, klass).__init__(self)

    def fix_name(f):
        return f.replace("-", "_").replace("?", "_p").replace(" ", "_")

    self_ = {}
    attr_dict = {}
    result_name = stringcase.pascalcase(fix_name(result_table_name).replace("_", ""))
    attr_regs = {
        f"{result_table_name}_id": Column(Integer, primary_key=True),
        "run_number": Column(Integer),
    }
    result_field_map = {"run_number": "run_number"}
    attr_dict = {
        "__tablename__": result_table_name,
        "__visit_name__": result_name,
        "description": f"{result_name} data",
        "schema": "placebo",
        "foreign_key_constraints": set(),
        "_extra_dependencies": set(),
        "_sa_instance_state": None,
        "_orphaned_outside_of_session": False,
        "name": result_name,
    }

    # These are the UI elements
    #   elif f in string_fields:
    #       attr_dict[g]=Column(String)
    for f in result_table_fields:
        g = fix_name(f)
        result_field_map[f] = g
        if f[:-2] == "_p":
            attr_regs[g] = Column(Bool)
        else:
            attr_regs[g] = Column(String)

    if runMetricsEveryStep:
        result_field_map["__tick__"] = "__tick__"
        attr_regs["__tick__"] = Column(Integer)

    # Add in the metrics.
    # TODO: we are  only doing one right now, may
    g = fix_name(metric)
    result_field_map[g] = g
    attr_regs[g] = Column(Float)
    # for m in metric:
    #    g=fix_name(m)
    #    result_field_map[f]=g
    #    attr_dict[g]=Column(Float)

    attr_dict.update(attr_regs)
    result_type = type(result_name, (Base,), attr_dict)
    klass = result_type
    result_type.__init__ = constructor
    # instrumentation.register_class(result_type)
    # for k in attr_regs.keys():
    #     attributes.register_attribute(result_type,k,uselist=False,useobject=False)
    return result_name, result_type, result_field_map


def add_commit(sess, obj):
    sess.add(obj)
    sess.commit()


def get_exp_header(exp):
    name = repetitions = runMetricsEveryStep = setup = go = metric = None
    name = exp.attrs["name"]
    repetitions = int(exp.attrs["repetitions"])
    runMetricsEveryStep = bool(exp.attrs["runMetricsEveryStep"])
    timeLimit = 0
    for c in exp.children:
        if c.name == "setup":
            setup = c.string
        elif c.name == "go":
            go = c.string
        elif c.name == "metric":
            metric = c.string
        elif c.name == "timeLimit":
            print(c.attrs["steps"])
    return name, repetitions, runMetricsEveryStep, setup, go, metric, timeLimit


class ResultsFireSim(Base):
    """
     The raw output for this class comes from tests/test_soup.py/test_parsed_nlogo_class_file

     Output line 7 column headers:
    "[run number]"        ,"map-file"              ,"person_path_weight","Medium"
    ,"add-person-spacing?","equal-diagonal-weight?","display-path-cost?","Fire_Speed"
    ,"Fast-Speed"         ,"Slow"                  ,"people-wait?"      ,"set-fire?"
    ,"Slow-Speed"         ,"People"                ,"Fast"              ,"Medium-Speed"
    ,"[step]"             ,"count turtles"         ,"mean-escape-time"

    additional: test_number

    Field sequence needs to mirror NetLogo:
         [run number]","map-file","People","person_path_weight"
        ,"Slow","Medium","Fast","display-path-cost?"
        ,"add-person-spacing?","people-wait?","equal-diagonal-weight?"
        ,"Slow-Speed","Medium-Speed","Fast-Speed","set-fire?"
        ,"Fire_Speed","[step]","count turtles","mean-escape-time"
    """

    __tablename__ = "results_fire_sim"
    results_fire_sim_id = Column("results_fire_sim_id", Integer, primary_key=True)

    run_number = Column("run_number", Integer)
    map_file = Column("map_file", String)
    people = Column("people", Integer)
    person_path_weight = Column("person_path_weight", Float)

    slow = Column("slow", Integer)
    medium = Column("medium", Integer)
    fast = Column("fast", Integer)

    display_path_cost_p = Column("display_path_cost_p", Boolean)
    add_person_spacing_p = Column("add_person_spacing_p", Boolean)
    people_wait_p = Column("people_wait_p", Boolean)
    equal_diagonal_weight_p = Column("equal_diagonal_weight_p", Boolean)

    slow_speed = Column("slow_speed", Float)
    fast_speed = Column("fast_speed", Float)
    medium_speed = Column("medium_speed", Float)

    set_fire_p = Column("set_fire_p", Boolean)
    fire_speed = Column("fire_speed", Integer)

    step = Column("step", Integer)
    count_turtles = Column("count_turtles", Integer)
    mean_escape_time = Column("mean_escape_time", Float)
    # test_number             = Column('test_number',Integer)


class Experiments(Base):
    __tablename__ = "experiments"
    experiments_id = Column(Integer, primary_key=True)
    nlogo_file_path = Column(String)
    nlogo_file_name = Column(String)


class Experiment(Base):
    __tablename__ = "experiment"
    experiment_id = Column(Integer, primary_key=True)
    experiments_id = Column(Integer, ForeignKey("experiments.experiments_id"))
    name = Column(String)
    repetitions = Column(Integer)
    runMetricsEveryStep = Column(Boolean)
    setup = Column(String)
    go = Column(String)
    metric = Column(String)

    def xml(self, sess):
        evs = [
            e.xml(sess)
            for e in sess.query(EnumeratedValueSet).filter(
                EnumeratedValueSet.experiment_id == self.experiment_id
            )
        ]
        return f"""<experiments><experiment name="{self.name}" repetitions="{self.repetitions}" runMetricsEveryStep="{self.runMetricsEveryStep}">
    <setup>{self.setup}</setup>
    <go>{self.go}</go>
    <metric>{self.metric}</metric>
        {''.join(evs)}
        </experiment></experiments>
        """


class EnumeratedValueSet(Base):
    __tablename__ = "enumerated_value_set"
    enumerated_value_set_id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiment.experiment_id"))
    variable = Column(String)

    def xml(self, sess):
        """"""
        vs = [
            f'<value value="{v.value}"/>'
            for v in sess.query(Value).filter(
                Value.enumerated_value_set_id == self.enumerated_value_set_id
            )
        ]
        print(f"what was {vs=}")
        return f'<enumeratedValueSet variable="{self.variable}">{"".join(vs)}</enumeratedValueSet>'


class Value(Base):
    __tablename__ = "value"
    value_id = Column(Integer, primary_key=True)
    enumerated_value_set_id = Column(
        Integer, ForeignKey("enumerated_value_set.enumerated_value_set_id")
    )
    value = Column(String)


# class ExitCondition(Base):
#    __tablename__ = "exitCondition"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    PCDATA = Column("PCDATA", BLOB)
#
#
# class Final(Base):
#    __tablename__ = "final"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    PCDATA = Column("PCDATA", BLOB)
#
#
# class SteppedValueSet(Base):
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
# class TimeLimit(Base):
#    __tablename__ = "timeLimit"
#    primary_key = Column("primary_key", Integer, primary_key=True)
#    seq = Column("seq", Integer)
#    foreign_key_experiment = Column("foreign_key_experiment", Integer)
#    steps = Column("steps", BLOB)
#
#
