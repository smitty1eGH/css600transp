import keyword
import pprint
import re
import random
import string
import stringcase
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect

# Generate an NGA College data model using SQL Alchemy from an existing, loaded server.

CONSTR_PKONLY = True
CONSTR_MULTI = False

# TODO: Need to manage the dialect-specific full-text part, if there is any interest
#  in moving away from MySQL
# Full text search keyword management
fts = {
    "FULLTEXT": "mysql",
    "mysql": "FULLTEXT",
    "postgresql": "",
    "dialect_options": "",
}
dialect_keys = ["dialect_options", "type"]


def get_pkname(t, inspector):
    """Inspect the PK constraint for table T and return a tuple that manages a singular or plural primary key."""
    inds = inspector.get_pk_constraint(t)
    if len(inds["constrained_columns"]) == CONSTR_PKONLY:
        return (CONSTR_PKONLY, inds["constrained_columns"][0])
    else:
        return (
            CONSTR_MULTI,
            "PrimaryKeyConstraint('"
            + "','".join(inds["constrained_columns"])
            + f"',name='{t}_pk')",
        )


def get_table_meta_and_indexes(t, pkname, keep_dialect, res_words, inspector):
    """Here we return the table name and any additional argumentst for mulit-key schemas or additional indices as required."""

    def get_table_argument_vals(plname, inds):
        """return a list of strings based on inds

        INDEX MANAGEMENT
        """
        if pkname[0] == CONSTR_MULTI:
            ta_vals = [pkname[1]]
        else:
            ta_vals = []

        for i in inds:
            j = []
            for k, l in i.items():
                q = ""
                if isinstance(l, str):
                    q = "'"

                if k != "name":
                    if k == "column_names":
                        j.append(
                            f"Column({q}{str(l).replace('[','').replace(']','')}{q})"
                        )
                    else:
                        if keep_dialect and k in res_words:
                            j.append(f"{k}={q}{l}{q}")
                        elif not keep_dialect and k not in res_words:
                            if k in fts.keys() or k in dialect_keys:
                                pass
                            else:
                                j.append(f"{k}={q}{l}{q}")

            ta_vals.append(
                f"Index('{i['name'] + ''.join(random.choices(string.ascii_uppercase,k=5))}', {','.join(j)})"
            )
        return ta_vals

    ta_vals = get_table_argument_vals(pkname, inspector.get_indexes(t))
    if len(ta_vals):

        maybe_comma = ""
        if len(ta_vals) == 1:
            maybe_comma = ","

        return f"'{t}'\n    __table_args__=({','.join(ta_vals)}{maybe_comma})"
    else:
        return f"'{t}'"


def get_type(f_type, f_name):
    """Eliminate integer lengths in fields"""
    ftype = str(f_type)

    if ftype[:7] == "INTEGER":
        return re.sub("\(\d*\)", "", ftype)

    elif ftype[:4] == "ENUM":
        # TODO: we should test to see if the enumerations are numeric or string
        return ftype.replace("ENUM", f'String,CheckConstraint("{f_name} IN ') + '")'

    elif "TEXT" in ftype:
        return "String"

    elif ftype[:7] == "TINYINT":
        return "Boolean"

    return ftype


def get_reserved_words(source="mysql+pymysql", target="base"):
    """Just return the mysql reserved words.
    TODO: switch on SOURCE and TARGET for a more appropriate return.
    Also, we should return a translation dictionary if possible
    """
    from sqlalchemy.dialects.mysql.base import RESERVED_WORDS as mysql_reserved_words
    from sqlalchemy.sql.compiler import RESERVED_WORDS as base_reserved_words

    return mysql_reserved_words - base_reserved_words


def main(conn_method, keep_dialect, stand_alone):
    """Make a straight dump, or optionally fliter out dialect keywords if KEEP_DIALECT
      is set to false.

    TINYINT is how MySQL does Booleans
    """
    if stand_alone:
        file_header = """from sqlalchemy import Index,Column,CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import PrimaryKeyConstraint

Base = declarative_base()\n"""

    print(file_header)
    res_words = get_reserved_words(conn_method)
    connstr = conn_method + "behaviorspace.db"
    engine = create_engine(connstr)
    inspector = inspect(engine)
    pp = pprint.PrettyPrinter(indent=4)

    for t in inspector.get_table_names():
        """There were no check constraints found in the legacy NGC schema via
        inds=inspector.get_check_constraints(t)
        """
        pkname = get_pkname(t, inspector)

        """FIELD MANAGEMENT
        """

        def get_fields(t):
            fs = []
            for c in inspector.get_columns(t):

                # Python keyword handling
                maybe_underscore = ""
                if keyword.iskeyword(c["name"]):
                    maybe_underscore = "_"

                # Primary key handling
                pk = ""
                if pkname[0] == CONSTR_PKONLY and str(pkname[1]) == c["name"]:
                    pk = ",primary_key=True"

                fld = f"""{c['name']}{maybe_underscore} = Column('{c['name']}',{get_type(c['type'],c["name"])}{pk})\n"""
                fs.append(fld.replace(" UNSIGNED", ""))
            return "    ".join(fs)

        cldef = f"""class {stringcase.pascalcase(t)}(Base):
    __tablename__={get_table_meta_and_indexes(t,pkname,keep_dialect,res_words,inspector)}
    {get_fields(t)}\n"""
        print(cldef)


if __name__ == "__main__":
    # main(conn_method='mysql+pymysql',keep_dialect=True,stand_alone=True)
    main(conn_method="sqlite:///", keep_dialect=False, stand_alone=True)
