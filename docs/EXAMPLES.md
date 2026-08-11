# Example outputs: no skill vs SimpleEnglish vs agent-ste

Every text below is an unedited benchmark output. Each one comes from one raw JSON file in [`evals/results/raw/`](../evals/results/raw/). The violation counts come from the upstream linter. Pick any cell in the raw folder to compare more.

## Example 1: README introduction (descriptive text)

Task: write a README introduction for `sqlpipe`, a CLI tool that syncs PostgreSQL tables to S3 as Parquet. Model: `gemini-3.6-flash-medium`.

### No skill — 4 violations per 114 words

```text
**sqlpipe** is a lightweight, high-performance CLI tool designed to seamlessly
stream PostgreSQL tables into Amazon S3 as optimized Apache Parquet files.
Built for modern data engineering and analytics workflows, `sqlpipe` extracts
relational data with minimal database overhead, handles schema conversion
automatically, and writes compressed columnar files ready for immediate
querying in data lake engines such as AWS Athena, DuckDB, Snowflake, and
Databricks.

Whether you need daily full-table snapshots or continuous incremental syncs,
`sqlpipe` streamlines your data pipeline architecture. By streaming records
directly from Postgres to S3 without relying on intermediate disk staging or
complex ETL frameworks, it delivers a fast, memory-efficient, and dependable
solution for powering your analytical data lake with a single command.
```

`lightweight`, `high-performance`, `seamlessly`, and `optimized` carry no facts. The second paragraph is one 44-word sentence.

### SimpleEnglish — 0 violations per 112 words

```text
`sqlpipe` is a command-line tool that syncs PostgreSQL tables to Amazon S3 as
Parquet files. The tool reads rows from a PostgreSQL database, converts the
data to Parquet format, and writes files to an S3 bucket. You can use
`sqlpipe` for data replication, scheduled exports, and background data
transfers.

Parquet files use column-oriented storage and compression to reduce storage
costs. Analytical query engines like Amazon Athena, Snowflake, and Apache
DuckDB read Parquet files faster than CSV files or JSON files. `sqlpipe`
saves the state of each sync to copy only new or modified rows during future
operations. This saved state keeps network usage low and prevents duplicate
records in your S3 storage.
```

### agent-ste — 0 violations per 122 words

```text
`sqlpipe` is a command-line tool that exports data from PostgreSQL databases
to Amazon S3. The tool reads tables from your database and writes the data to
S3 as Apache Parquet files. You can run `sqlpipe` as a single job or set a
schedule for recurring data syncs. `sqlpipe` converts PostgreSQL data types
into standard Parquet data types automatically.

Parquet files reduce storage costs and increase query speed in data
warehouses like Snowflake, BigQuery, and AWS Athena. If you need to sync
large tables, `sqlpipe` uses multipart uploads to transfer files efficiently.
If a network error occurs during a transfer, `sqlpipe` retries the failed
part automatically. You must provide database credentials and AWS access keys
in environment variables or in a configuration file.
```

Note the STE moves: every condition starts its sentence ("If you need to sync large tables, ..."), the requirement is a `must`, and each sentence adds one fact.

## Example 2: Release notes with a breaking change

Task: write v2.0 release notes with one breaking API change, one new flag, and one performance gain. Model: `claude-opus-4-8-medium`.

### No skill — 2 violations per 117 words

```text
# sqlpipe v2.0 Release Notes

**Breaking Change:** The `name` field on `/v2/users` has been split into two
separate fields, `first_name` and `last_name`. Any integrations that read or
write the old `name` field must be updated to use the new fields before
upgrading. Responses will no longer include `name`.

**New Feature:** Added the `--incremental` flag, allowing pipelines to
process only new or changed records since the last run rather than
reprocessing entire datasets. This significantly reduces runtime and resource
usage for recurring syncs.

**Performance:** Parquet writes are now up to 40% faster, thanks to
optimizations in our serialization and buffering layer. Existing Parquet
workflows benefit automatically with no configuration changes required.
```

`has been split` hides the actor. `, allowing pipelines to process` chains a second thought onto a done sentence. `must be updated` does not say who updates what.

### agent-ste — 0 violations per 91 words

```text
# sqlpipe v2.0 release notes

## Breaking changes

The `/v2/users` endpoint changed the response format. Version 1 returned one
`name` field. Version 2 returns two fields: `first_name` and `last_name`.

If your code reads `name`, you must update it before you upgrade. Read
`first_name` and `last_name` instead.

## New features

Version 2.0 adds the `--incremental` flag. If you set `--incremental`,
sqlpipe copies only the rows that changed since the last run.

## Performance

Version 2.0 writes Parquet files 40% faster than version 1.9.

## How to upgrade

1. Update your client code to read `first_name` and `last_name`.
2. Install sqlpipe v2.0.
3. Run your pipeline.
```

The skill turned the same facts into active sentences, put the condition before the command, and added the upgrade procedure as a numbered list.
