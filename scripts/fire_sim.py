from sqlalchemy import Index, Column, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint

Base = declarative_base()


class ResultsFireSim(Base):
    """
     The raw output for this class comes from

     Output line 7 column headers:
    "[run number]"        ,"map-file"              ,"person_path_weight","Medium"
    ,"add-person-spacing?","equal-diagonal-weight?","display-path-cost?","Fire_Speed"
    ,"Fast-Speed"         ,"Slow"                  ,"people-wait?"      ,"set-fire?"
    ,"Slow-Speed"         ,"People"                ,"Fast"              ,"Medium-Speed"
    ,"[step]"             ,"count turtles"         ,"mean-escape-time"

    There will be an additional test_number added

    Fields have been re-sequenced here for ease of comparison with the netlogo interface.
    """

    __tablename__ = "results_fire_sim"
    results_FireSim_1_id = Column("results_fire_sim_id", Integer, primary_key=True)
    test_number = Column("test_number", Integer)

    # ==NetLogo UI==
    map_file = Column("map_file", String)
    people = Column("people", Integer)
    person_path_weight = Column("person_path_weight", Float)

    # People Speed Distribution, integger from 0 to 100 representing a percentage of PEOPLE
    slow = Column("slow", Integer)
    medium = Column("medium", Integer)
    fast = Column("fast", Integer)

    # Predicates
    display_path_cost_p = Column("display_path_cost_p", Boolean)
    add_person_spacing_p = Column("add_person_spacing_p", Boolean)
    people_wait_p = Column("people_wait_p", Boolean)
    equal_diagonal_weight_p = Column("equal_diagonal_weight_p", Boolean)

    # Movement rates of people in this bin, 0 to 1
    slow_speed = Column("slow_speed", Float)
    fast_speed = Column("fast_speed", Float)
    medium_speed = Column("medium_speed", Float)

    # Fire values
    set_fire_p = Column("set_fire_p", String)
    fire_speed = Column("fire_speed", Integer)

    # Outputs
    run_number = Column("run_number", Integer)
    step = Column("step", Integer)
    count_turtles = Column("count_turtles", Integer)
    mean_escape_time = Column("mean_escape_time", Float)
