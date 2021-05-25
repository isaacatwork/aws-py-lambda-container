# AWS lambda  - Running Containerized Applications

AWS lambda is a function as a service(FaaS) that allows you to write any code in any programming language(using a Runtime API) to perform a specific task without provisioning servers. These programs usually perform tasks that are short lived like renaming s3 files, trigger Fargate tasks and so on, due to its 15 minutes limit. 

AWS lambda has a few limitation when it comes to application size. You can only upload 50 MB of zipped app. A work around this limit is to split your lambda package into multiple sub-packages and use layers and import these in the main program. Example, let say we have an event-driven Python application that processes HDF5 data from an IoT device uploaded to s3. The application requires a few dependencies like pandas, pyarrow, numpy and h5py. We can layer each of these packages and import in our main application. This is also very useful when we have other lambda functions that requires those packages, but it also has a limitation . The total unzipped size of all the layers cannot exceed 250 MB and can only have 5 layers.

All these limitation can be resolved with the new container image support. This allows you to deploy a container image up to 10GB in size. 

The following steps is an example of running / testing python application as a function locally.

The application reads files from s3 and retrieves a list employees that have have been employed for a specific number of years. 


## Set-up

The data folder is empty. It is mounted to the container to be used for object storage. 

Add .env file to the root directory containing your fake AWS credentials like below.

```bash
MINIO_ACCESS_KEY=JamesBond007
MINIO_SECRET_KEY=JamesBond007
```

* The Dockerfile uses base image from AWS containing everything you would need to run your functions.

* data_generator.py contains code to generate fake employee data

* main.py contains the main program lambda runs

After you have the file structure is set-up, use the following commands to run a test

```bash
docker compose up
```

Open another terminal and run the following command.

This command generates the fake employee data in a bucket. You can change the num_of_rows and bucket values. If you change the bucket name, change it in the request payload too.

```bash
 docker exec aws_lambda bash -c "python datagenerator.py --num_of_rows 10_000 --bucket testbucket"
 ```

```bash
 curl -XPOST "http://localhost:9001/2015-03-31/functions/function/invocations" -d '{"years_of_service": 5, "bucket":"testbucket", "key": "sample.parquet","destination": "s3://testbucket/sample_result.csv"}'
 ```

Open a http://localhost:8081/minio/ in a browser. Use credentials in the .env file to login and you should see the source and result file in the bucket.

