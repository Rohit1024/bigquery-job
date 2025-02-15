from googleapiclient import discovery
from google.cloud import bigquery
from typing import List, TypedDict
import os
import sys

class Role(TypedDict):
    name: str
    title: str
    description: str
    deleted: bool
    etag: str
    included_permissions: List[str]
    stage: str

def get_bigquery_client():
    """Initialize BigQuery client"""
    return bigquery.Client()

def upload_to_bigquery(dataset_name: str, table_name: str, roles: List[Role]):
    client = get_bigquery_client()
    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    # Convert roles to a list of dictionaries for easier query construction
    rows_to_insert = [dict(role) for role in roles]

    # Construct the MERGE query
    query = f"""
    MERGE `{dataset_name}.{table_name}` T
    USING UNNEST(@rows_to_insert) S
    ON T.name = S.name
    WHEN MATCHED THEN UPDATE SET
        T.title = S.title,
        T.description = S.description,
        T.deleted = S.deleted,
        T.etag = S.etag,
        T.included_permissions = S.included_permissions,
        T.stage = S.stage
    WHEN NOT MATCHED THEN INSERT ROW
    """

    query_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("rows_to_insert", bigquery.Struct([
                bigquery.Field("name", "STRING"),
                bigquery.Field("title", "STRING"),
                bigquery.Field("description", "STRING"),
                bigquery.Field("deleted", "BOOLEAN"),
                bigquery.Field("etag", "STRING"),
                bigquery.Field("included_permissions", "STRING", mode="REPEATED"),
                bigquery.Field("stage", "STRING")
            ]), rows_to_insert)
        ]
    )


    query_job = client.query(query, job_config=query_job_config)
    query_job.result()  # Wait for the query to complete
    print(f"Merge operation completed.")

def list_all_roles() -> List[Role]:
    """List all IAM roles"""
    service = discovery.build('iam', 'v1')
    roles: List[Role] = []
    page_token = None

    while True:
        request = service.roles().list(pageToken=page_token, showDeleted=False)
        response = request.execute()

        if 'roles' in response:
            for role in response['roles']:
                roles.append({
                    'name': role.get('name', ''),
                    'title': role.get('title', ''),
                    'description': role.get('description', ''),
                    'deleted': role.get('deleted', False),
                    'etag': role.get('etag', ''),
                    'included_permissions': role.get('includedPermissions', []),
                    'stage': role.get('stage', '')
                })

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return roles

def get_role_details(role_name: str) -> Role:
    """Get detailed information about a specific role"""
    service = discovery.build('iam', 'v1')
    request = service.roles().get(name=role_name)
    role = request.execute()

    return {
        'name': role.get('name', ''),
        'title': role.get('title', ''),
        'description': role.get('description', ''),
        'deleted': role.get('deleted', False),
        'etag': role.get('etag', ''),
        'included_permissions': role.get('includedPermissions', []),
        'stage': role.get('stage', '')
    }

def crawl_roles():
    """Crawl IAM roles and store them in BigQuery"""
    dataset_name = os.environ.get("DATASET_NAME", "iam_roles")
    table_name = os.environ.get("TABLE_NAME", "roles")

    print(f"Starting role crawl. Data will be stored in BigQuery dataset: {dataset_name}, table: {table_name}")
    
    try:
        # Get all roles
        roles = list_all_roles()
        detailed_roles = []
        
        # Get detailed information for each role
        for role in roles:
            detailed_role = get_role_details(role['name'])
            detailed_roles.append(detailed_role)
            print(f"Successfully processed role {role['name']}")

        # Upload to BigQuery
        upload_to_bigquery(dataset_name, table_name, detailed_roles)
        
        print(f"Crawl completed. Check the '{dataset_name}.{table_name}' table in BigQuery")
        return 0
    except Exception as e:
        print(f"Error during crawl: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(crawl_roles())
