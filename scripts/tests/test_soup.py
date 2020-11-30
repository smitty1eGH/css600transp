from csv import DictReader
import keyword
from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
import pytest
from sqlalchemy import create_engine, inspect, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column, MetaData
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

from behaviorspace import (
    get_result_table,
    add_commit,
    get_exp_header,
    Base,
    Experiments,
    Experiment,
    EnumeratedValueSet,
    Value,
)


@pytest.fixture
def netlogo_sh():
    return "/home/smitty/bin/NetLogo6.1.1/netlogo-headless.sh"


@pytest.fixture
def netlogo_args():
    """We can write the XML out to a path via --setup-file,
    We can write the results to a path via --table
    """
    return {
        "model": "/home/smitty/proj/css600transp/css600transp/FireSim.nlogo",
        "experiment": "FireSim",
        "table": "-",
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
    """Return a session instance, but also add the SQLAlchemy metadata as a
    member for the instance so that the dynamically generated table
    is easier to instantiate.
    """
    engine = create_engine("sqlite://", echo=True)
    with engine.begin() as conn:
        conn.execute("ATTACH DATABASE ':memory:' AS placebo")
    Base.metadata.create_all(engine)
    sess = sessionmaker(bind=engine)()
    sess.engine = engine
    sess.metadata = MetaData(bind=engine)
    return sess


@pytest.fixture
def try_result_name():
    return "ResultsFireSim1"


@pytest.fixture
def result_field_map():
    return {
        "run_number": "run_number",
        "map-file": "map_file",
        "person_path_weight": "person_path_weight",
        "Medium": "Medium",
        "add-person-spacing?": "add_person_spacing_p",
        "equal-diagonal-weight?": "equal_diagonal_weight_p",
        "display-path-cost?": "display_path_cost_p",
        "Fire_Speed": "Fire_Speed",
        "Fast-Speed": "Fast_Speed",
        "Slow": "Slow",
        "people-wait?": "people_wait_p",
        "set-fire?": "set_fire_p",
        "Slow-Speed": "Slow_Speed",
        "People": "People",
        "Fast": "Fast",
        "Medium-Speed": "Medium_Speed",
    }


@pytest.fixture
def beh_sp_path():
    return Path()


@pytest.fixture
def string_fields():
    return ["map_file"]


@pytest.fixture
def parsed_nlogo(string_fields, behsp_xml, sess):
    """The METRIC return from get_experiment_header is the additional outputs we store
    in addition to the UI widget values.
    """
    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
    add_commit(sess, exps)
    soup = BeautifulSoup(behsp_xml, "lxml-xml")
    for e in soup.experiments:
        if e.name != None:
            (
                name,
                repetitions,
                runMetricsEveryStep,
                setup,
                go,
                metric,
                timeLimit,
            ) = get_exp_header(e)
            ex = Experiment(
                experiments_id=exps.experiments_id,
                name=name,
                repetitions=repetitions,
                setup=setup,
                go=go,
                metric=metric,
            )
            add_commit(sess, ex)

            result_table_name = f"results_{name}_{ex.experiment_id}"
            result_table_fields = []

            for evs in e.find_all("enumeratedValueSet"):
                vname = evs.attrs["variable"]
                result_table_fields.append(vname)
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id, variable=vname)
                add_commit(sess, enu)
                for v in evs.find_all("value"):
                    w = Value(
                        enumerated_value_set_id=enu.enumerated_value_set_id,
                        value=v.attrs["value"],
                    )
                    sess.add(w)
                    sess.commit()

            # for ex in sess.query(Experiment).filter(Experiment.experiment_id==1):
            #    print(ex.xml(sess))
            # insp = inspect(result_type)
            result_name, result_type, result_field_map = get_result_table(
                string_fields,
                result_table_name,
                result_table_fields,
                runMetricsEveryStep,
                metric,
            )
            sess.metadata.create_all(bind=sess.engine, tables=[result_type])
            sess.commit()
            for t in sess.metadata.sorted_tables:
                print(t.name)
            # result_type_reflected = Table(result_name, sess.metadata, autoload=True, autoload_with=sess.engine)
            return result_name, result_type, result_field_map


# @pytest.fixture
# def parsed_nlogo_type_module(string_fields,behsp_xml,sess):
#    '''The METRIC return from get_experiment_header is the additional outputs we store
#         in addition to the UI widget values.
#    '''
#    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
#    add_commit(sess,exps)
#    soup = BeautifulSoup(behsp_xml,'lxml-xml')
#    for e in soup.experiments:
#        if e.name != None:
#            name, repetitions, runMetricsEveryStep, setup, go, metric, timeLimit = get_exp_header(e)
#            ex = Experiment(experiments_id=exps.experiments_id, name=name, repetitions=repetitions, setup=setup, go=go, metric=metric)
#            add_commit(sess,ex)
#
#            result_table_name = f'results_{name}_{ex.experiment_id}'
#            result_table_fields = []
#
#            for evs in e.find_all('enumeratedValueSet'):
#                vname = evs.attrs['variable']
#                result_table_fields.append(vname)
#                enu = EnumeratedValueSet(experiment_id=ex.experiment_id,variable=vname)
#                add_commit(sess,enu)
#                for v in evs.find_all('value'):
#                    w = Value(enumerated_value_set_id=enu.enumerated_value_set_id,value=v.attrs['value'])
#                    sess.add(w)
#                    sess.commit()
#
#           #for ex in sess.query(Experiment).filter(Experiment.experiment_id==1):
#           #    print(ex.xml(sess))
#           #insp = inspect(result_type)
#            result_name, result_type, result_field_map = get_result_table(string_fields,result_table_name,result_table_fields,runMetricsEveryStep,metric)
#            sess.metadata.create_all(bind=sess.engine,tables=[result_type])
#            sess.commit()
#            for t in sess.metadata.sorted_tables:
#                print(t.name)
#           #result_type_reflected = Table(result_name, sess.metadata, autoload=True, autoload_with=sess.engine)
#            return result_name, result_type, result_field_map


@pytest.fixture
def parsed_nlogo_class_file(string_fields, behsp_xml, sess):
    """The METRIC return from get_experiment_header is the additional outputs we store
    in addition to the UI widget values.
    """
    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
    add_commit(sess, exps)
    soup = BeautifulSoup(behsp_xml, "lxml-xml")
    for e in soup.experiments:
        if e.name != None:
            (
                name,
                repetitions,
                runMetricsEveryStep,
                setup,
                go,
                metric,
                timeLimit,
            ) = get_exp_header(e)
            ex = Experiment(
                experiments_id=exps.experiments_id,
                name=name,
                repetitions=repetitions,
                setup=setup,
                go=go,
                metric=metric,
            )
            add_commit(sess, ex)

            result_table_name = f"results_{name}_{ex.experiment_id}"
            result_table_fields = []

            for evs in e.find_all("enumeratedValueSet"):
                vname = evs.attrs["variable"]
                result_table_fields.append(vname)
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id, variable=vname)
                add_commit(sess, enu)
                for v in evs.find_all("value"):
                    w = Value(
                        enumerated_value_set_id=enu.enumerated_value_set_id,
                        value=v.attrs["value"],
                    )
                    sess.add(w)
                    sess.commit()
            return (
                string_fields,
                result_table_name,
                result_table_fields,
                runMetricsEveryStep,
                metric,
                e.name,
            )


@pytest.mark.skip
def test_extract(behsp_xml):
    print(behsp_xml)
    soup = BeautifulSoup(behsp_xml, "lxml-xml")
    for e in soup.experiments:
        if e.name != None:
            print(
                f'{e.attrs["name"]=}\t{e.attrs["repetitions"]=}\t{e.runMetricsEveryStep=}'
            )
            for c in e.children:
                if c.name == "setup":
                    print(c.string)
                elif c.name == "go":
                    print(c.string)
                elif c.name == "metric":
                    print(c.string)
                elif c.name == "timeLimit":
                    print(c.attrs["steps"])

            for evs in e.find_all("enumeratedValueSet"):
                vname = evs.attrs["variable"]
                v = evs.find("value")
                vval = v.attrs["value"]
                print(f"{vname=}\t{vval=}")


@pytest.mark.skip
def test_load(behsp_xml, sess):
    def get_result_table(result_table_name, result_table_fields):
        """Calculate a SQLAlchemy Class for the desired experiment.
        Return: the calculated name, the class, and a map of how the data fields
          in the NetLogo output map to what the python class's members are named.
        """

        def fix_name(f):
            return f.replace("-", "_").replace("?", "_p")

        attr_dict = {
            "__tablename__": result_table_name,
            f"{result_table_name}_id": Column(Integer, primary_key=True),
        }

        result_field_map = {}
        for f in result_table_fields:
            g = fix_name(f)
            result_field_map[f] = g
            attr_dict[g] = Column(Float)

        result_name = stringcase.pascalcase(
            fix_name(result_table_name).replace("_", "")
        )
        return result_name, type(result_name, (Base,), attr_dict), result_field_map

    def add_commit(sess, obj):
        sess.add(obj)
        sess.commit()

    def get_exp_header(exp):
        name = repetitions = runMetricsEveryStep = setup = go = metric = None
        name = exp.attrs["name"]
        repetitions = exp.repetitions
        runMetricsEveryStep = exp.runMetricsEveryStep
        timeLimit = 0
        for c in exp.children:
            if c.name == "setup":
                setup = c.string
            elif c.name == "go":
                go = c.string
            elif c.name == "metric":
                metric = c.string
            elif c.name == "timeLimit":
                timeLimit = c.attrs["steps"]
        return name, repetitions, runMetricsEveryStep, setup, go, metric, timeLimit

    exps = Experiments(nlogo_file_path=str(filen.parents), nlogo_file_name=filen.name)
    add_commit(sess, exps)
    soup = BeautifulSoup(behsp_xml, "lxml-xml")
    for e in soup.experiments:
        if e.name != None:
            (
                name,
                repetitions,
                runMetricsEveryStep,
                setup,
                go,
                metric,
                timeLimit,
            ) = get_exp_header(e)
            ex = Experiment(
                experiments_id=exps.experiments_id,
                name=name,
                repetitions=repetitions,
                setup=setup,
                go=go,
                metric=metric,
            )
            add_commit(sess, ex)

            result_table_name = f"results_{name}_{ex.experiment_id}"
            result_table_fields = []

            for evs in e.find_all("enumeratedValueSet"):
                vname = evs.attrs["variable"]
                result_table_fields.append(vname)
                enu = EnumeratedValueSet(experiment_id=ex.experiment_id, variable=vname)
                add_commit(sess, enu)
                for v in evs.find_all("value"):
                    w = Value(
                        enumerated_value_set_id=enu.enumerated_value_set_id,
                        value=v.attrs["value"],
                    )
                    sess.add(w)
                    sess.commit()

            for ex in sess.query(Experiment).filter(Experiment.experiment_id == 1):
                print(ex.xml(sess))
            result_name, result_table, result_field_map = get_result_table(
                result_table_name, result_table_fields
            )
        # print(f'{result_name=}\t{result_field_map=}')


@pytest.mark.skip
def test_parse_output(parsed_nlogo, beh_sp_path, netlogo_sh, netlogo_args, sess):
    START_DATA = 8
    ELIDE_LAST = -1
    class_name, ClassName, class_field_map = parsed_nlogo
    args = [netlogo_sh]
    for k, v in netlogo_args.items():
        args.append(f"--{k}")
        args.append(v)
    result = subprocess.run(args, capture_output=True)
    lines = f"{result.stdout=}".split("\\n")[START_DATA:]
    fnames = class_field_map.values()
    dr = DictReader(lines[:ELIDE_LAST], fnames)
    for line in dr:
        x = ClassName(**line)
        print(x.insert())
        # print(f'{isinstance(x,ClassName)=}\n{dir(x)}\n\t{print(x.__class__)}')
        # add_commit(sess,x)
        # sess.add(x)


# def test_parse_output_type_module(parsed_nlogo_type_module,beh_sp_path,netlogo_sh,netlogo_args, sess):
#    '''One last try to get this to work.
#    '''
#    START_DATA=8
#    ELIDE_LAST=-1
#    class_name, ClassName, class_field_map=parsed_nlogo_type_module
#    args = [netlogo_sh]
#    for k,v in netlogo_args.items():
#        args.append(f'--{k}')
#        args.append(v)
#    result = subprocess.run(args, capture_output=True)
#    lines = f'{result.stdout=}'.split('\\n')[START_DATA:]
#    fnames =class_field_map.values()
#    dr = DictReader(lines[:ELIDE_LAST],fnames)
#    for line in dr:
#        x=ClassName(**line)
#        print(x.insert())
#        #print(f'{isinstance(x,ClassName)=}\n{dir(x)}\n\t{print(x.__class__)}')
#        #add_commit(sess,x)
#        #sess.add(x)


@pytest.mark.skip
def test_parsed_nlogo_class_file(parsed_nlogo_class_file):
    """parsed_nlogo_class_file[0]=['map_file']
    parsed_nlogo_class_file[1]='results_FireSim_1'
    parsed_nlogo_class_file[2]=['map-file', 'person_path_weight', 'Medium', 'add-person-spacing?', 'equal-diagonal-weight?', 'display-path-cost?', 'Fire_Speed', 'Fast-Speed', 'Slow', 'people-wait?', 'set-fire?', 'Slow-Speed', 'People', 'Fast', 'Medium-Speed']
    parsed_nlogo_class_file[3]=True
    parsed_nlogo_class_file[4]='count turtles'
    """

    def get_fields(pkanme, t):
        fs = [f"{pkname} = Column('{pkname}',Integer,primary_key=True)"]
        for c in t:
            d = c.replace("-", "_").replace("?", "_p")
            maybe_underscore = ""
            if keyword.iskeyword(d):
                maybe_underscore = "_"
            fs.append(f"    {d}{maybe_underscore} = Column('{d}',String)")
        return "\t\n".join(fs)

    file_header = """from sqlalchemy import Index,Column,CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint

Base = declarative_base()\n"""

    with open("fire_sim.py", "w") as f:
        f.write(file_header)
        pkname = f"{parsed_nlogo_class_file[1]}_id"
        cldef = f"""class {stringcase.capitalcase(parsed_nlogo_class_file[1]).replace('_','')}(Base):
    __tablename__='{parsed_nlogo_class_file[1]}'
    {get_fields(pkname,parsed_nlogo_class_file[2])}\n"""
        f.write(cldef)


def test_dump_behsp_xml(behsp_xml):
    print(behsp_xml)
