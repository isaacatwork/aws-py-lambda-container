import argparse
import datetime
import itertools
import logging
import os
import random

import boto3
import pandas as pd
from botocore.exceptions import ClientError
from faker import Faker


def date_generator():
    """
    Simple random date generator

    Returns datetime.date - a valid random date

    Example:
        >>> r_date = date_generator()
        >>> isinstance(r_date, datetime.date)
        True
    """
    year = random.randint(1990, 2021) # assuming company started in 1990
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year=year, month=month, day=day)


def create_bucket(bucket_name: str) -> bool:
    """Create an S3 bucket

    Args:
        bucket_name(str): Bucket to create

    Returns:
        bool - True if bucket created, else False
    """

    # Create bucket
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-1",
        )
        s3_client.create_bucket(Bucket=bucket_name)
        return True
    except KeyError as e:
        logging.error(f"Key not found: {e}")
    except ClientError as e:
        logging.error(e)
        return False


def employee_data_generator(bucket_name: str, num_of_rows: int = 1_000_000) -> bool:
    """
    Generates a dateframe with 4 columns - employee_name, start_date, department and title.
    Writes generated data in 3 formats - csv, parquet, json into s3 bucket for lambda container playground

    Args:
        bucket_name(str): name of bucket to write sample data.
        num_of_rows(int): number of rows of data to generate. Max 1_000_000 rows. Defaults to 1_000_000

    Returns:
        Tr: genereted data

    Raises:
        ValueError: when num_of_rows is lager than 1000000

    Example:
        >>> employee_data_generator(bucket_name=test_bucket, num_of_rows=500)
        True
    """
    if num_of_rows > 1_000_000:
        raise ValueError("Row number too large, Try less than 1 million rows")

    client_kwargs = {"client_kwargs": {"endpoint_url": "http://minio:9000"}}

    fake = Faker("en_US")
    sample_names = [fake.name() for _ in range(num_of_rows)]
    sample_roles = random.choices(
        [
            "Data Engineer",
            "Data Scientist",
            "Engineering Manager",
            "Software Engineer",
            "Team Lead",
        ],
        k=num_of_rows,
    )

    sample_department = random.choices(
        ["R&D", "Sales", "Product", "Marketing"], k=num_of_rows
    )

    generated_date = [date_generator() for _ in range(0, num_of_rows)]

    try:

        df = pd.DataFrame(
            {
                "employee_name": sample_names,
                "start_date": generated_date,
                "department": sample_department,
                "role": sample_roles,
            }
        )
        df.loc[:, "start_date"] = pd.to_datetime(df.start_date)

        df.to_parquet(
            f"s3://{bucket_name}/sample.parquet",
            engine="pyarrow",
            compression="snappy",
            storage_options=client_kwargs,
        )

        return True
    except Exception as e:
        logging.error(e)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--num_of_rows", help="Number of rows to generate", required=False
    )
    parser.add_argument(
        "-b", "--bucket", help="Name of bucket to save generated files", required=True
    )
    args = vars(parser.parse_args())

    num_of_rows = int(args.get("num_of_rows", 1_000_00))
    bucket_name = args.get("bucket")
    create_bucket(bucket_name=bucket_name)
    employee_data_generator(bucket_name=bucket_name, num_of_rows=num_of_rows)