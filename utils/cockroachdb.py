"""Utils functions for CockroachDB"""

import sqlalchemy


def create_connection_string(user, password, host, port, database, options):
    """Create CockroachDB connection string."""
    return (
        "cockroachdb://"
        f"{user}:{password}@{host}:{port}/{database}"
        f"?sslmode=verify-full&options={options}"
    )


def create_engine(user, password, host, port, database, options):
    """Create SQL Alchemy engine."""
    return sqlalchemy.create_engine(
        create_connection_string(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            options=options,
        )
    )
