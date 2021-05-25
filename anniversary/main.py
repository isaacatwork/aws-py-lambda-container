import datetime
import json
import logging
from typing import Dict, Any

import pyarrow.parquet as pq
import s3fs

client_kwargs = {"client_kwargs": {"endpoint_url": "http://minio:9000"}} # this is used to simulate s3
s3 = s3fs.S3FileSystem(**client_kwargs)


def get_employees_anniversary(event: Dict[str, str], context: Any) -> str:
    """
    lambda handler to desmostrate using containers with third party packages like pandas and
    integration with s3.

    Funtion gets list of employees employeed for a specific number of years using the number of years of services specified in request payload.

    """

    try:
        # get required data from payload
        year = int(event["years_of_service"])
        bucket = event["bucket"]
        key = event["key"]
        destination = event["destination"]  # full s3 path with key
    except ValueError as e:
        msg = "Year must be a valid 4 digit year"
        logging.error(msg=msg)
        return json.dumps({"error_message": msg})
    except KeyError as e:
        msg = f"{e} required in payload"
        logging.error(msg=msg)
        return json.dumps({"error_message": msg})

    try:
        df = pq.read_table(f"s3://{bucket}/{key}", filesystem=s3).to_pandas(
            date_as_object=False, split_blocks=True, self_destruct=True
        )
        year_today = datetime.date.today().year

        df = df[(year_today - df.start_date.dt.year) == year]

        df.to_csv(destination, storage_options=client_kwargs)

        return json.dumps(
            {
                "status": "done",
                "result": {"file_path": destination, "rows_returned": len(df)},
            }
        )
    except Exception as e:
        logging.error(e)
        return json.dumps({"error_message": e})
