# pgconnparams.py

This small utility takes a `postgres:` URI and parses it, writing out the same connection information as standard command-line options.

It can also write a `.pgpass` file containing the information in the URI.

It's intended for systems that store database connection information as URIs, but want to invoke PostgreSQL utilities that don't take URI-style connection information.