"""Utils functions for CockroachDB"""


def create_connection_string(user, password, host, port, database, options):
    """Create CockroachDB connection string."""
    return (
        "cockroachdb://"
        f"{user}:{password}@{host}:{port}/{database}"
        f"?sslmode=verify-full&options={options}"
    )
