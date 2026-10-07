"""Arlington's registered voters by year, as the state reports them
-> data/built/registration.csv

sources/government/state/va_dept_of_elections/registration_2010-2025.csv.gz, every row and
column as fetched. Nothing to reshape: the step exists so that the clean
stage reads it from data/built/ like every other source.
"""
from paths import VA_ELECTIONS, source, write

REGISTRATION = VA_ELECTIONS / "registration_2010-2025.csv.gz"


def build():
    return source(REGISTRATION, dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "registration")
