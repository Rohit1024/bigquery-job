# IAM Role Crawler

This Python script crawls Google Cloud IAM roles and stores them in a BigQuery table. It uses the Google Cloud IAM and BigQuery APIs.

## Prerequisites

Before running the script, ensure you have the following:

*   A Google Cloud Project with the IAM and BigQuery APIs enabled.
*   Authentication set up. The easiest way is to use Application Default Credentials. You can set these up using the `gcloud` CLI: `gcloud auth application-default login`
*   Python 3 installed.
*   The required Python libraries installed:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth google-cloud-bigquery
```

-   A BigQuery dataset and table created. The script will use the dataset and table names specified as environment variables (see Configuration). If the table doesn't exist, the MERGE statement will effectively create it based on the schema defined by the `Role` TypedDict.

Configuration
-------------

The script uses environment variables for configuration:

-   `DATASET_NAME`: The name of the BigQuery dataset. Defaults to `iam_roles`.
-   `TABLE_NAME`: The name of the BigQuery table. Defaults to `roles`.

You can set these environment variables in your terminal before running the script:

Bash

```bash
export DATASET_NAME="my_dataset"
export TABLE_NAME="my_roles_table"
python iam_role_crawler.py
```

Usage
-----

1.  Clone this repository (or copy the code into a file named `iam_role_crawler.py`).
2.  Install the required libraries as described in the Prerequisites section.
3.  Set the environment variables as described in the Configuration section.
4.  Run the script:

Bash

```bash
python iam_role_crawler.py
```

The script will crawl all IAM roles in your project, retrieve detailed information for each role, and store the data in the specified BigQuery table. The output will indicate the progress and any errors encountered.

Code Overview
-------------

The script consists of the following functions:

-   `get_bigquery_client()`: Initializes and returns a BigQuery client.
-   `upload_to_bigquery(dataset_name, table_name, roles)`: Uploads the list of roles to the specified BigQuery table using a MERGE statement for efficient updates and inserts. The MERGE statement ensures that existing roles are updated and new roles are inserted. This prevents duplicates and keeps the table consistent.
-   `list_all_roles()`: Lists all IAM roles in the project using the IAM API. Handles pagination to retrieve all roles.
-   `get_role_details(role_name)`: Retrieves detailed information about a specific role using the IAM API.
-   `crawl_roles()`: Orchestrates the entire process. It lists all roles, retrieves details for each role, and uploads the data to BigQuery. It also handles setting the BigQuery dataset and table name via environment variables. It returns 0 on success, and 1 on error.
-   `if __name__ == "__main__":`: Entry point of the script. Calls `crawl_roles()` and exits with the returned status code.

The `Role` TypedDict defines the structure of the role data. This helps with type checking and ensures consistency.

Error Handling
--------------

The `crawl_roles()` function includes a `try...except` block to catch potential errors during the crawl process. This helps to provide more informative error messages and prevent the script from crashing.

BigQuery Schema
---------------

The BigQuery table schema is implicitly defined by the `Role` TypedDict. The script uses this structure when inserting or updating data. The table will contain the following columns:

-   `name`: STRING (Primary Key)
-   `title`: STRING
-   `description`: STRING
-   `deleted`: BOOLEAN
-   `etag`: STRING
-   `included_permissions`: STRING (Repeated)
-   `stage`: STRING

The `name` field is used as the primary key for the MERGE operation. The `included_permissions` field is a repeated field, allowing for multiple permissions to be associated with a role.
