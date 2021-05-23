import datetime
import logging

import pyarrow.parquet as pq
import s3fs

client_kwargs = {"client_kwargs": {"endpoint_url": "http://minio:9000"}}
s3 = s3fs.S3FileSystem(**client_kwargs)


def get_employees_anniversary(event, context):
    """
    lambda handler to desmostrate using containers with third party packages like pandas and
    integration with s3.

    Funtion gets list of employees celebrating anniversary using the number of years of services specified in request payload.

    """

    try:
        # get required data from payload
        year = int(event["year"])
        bucket = event["bucket"]
        key = event["key"]
        destination = event["destination"]  # full s3 path with key
    except ValueError:
        logging.error({"error": "Year must be a valid 4 digit year"})
        return False
    except KeyError as e:
        logging.error({"error": f"{e} required in payload"})
        return False

    try:
        df = pq.read_table(f"s3://{bucket}/{key}", filesystem=s3).to_pandas(
            date_as_object=False, split_blocks=True, self_destruct=True
        )
        year_today = datetime.date.today().year

        df = df[(year_today - df.start_date.dt.year) == year]

        df.to_csv(destination, storage_options=client_kwargs)

        return {"status": "done", "result_path": destination}
    except Exception as e:
        return logging.error(e)
