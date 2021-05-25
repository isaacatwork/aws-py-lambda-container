FROM public.ecr.aws/lambda/python:3.8 AS lambda-py

COPY ./anniversary/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt --target=.

# Copy python application
COPY ./anniversary .

# This is the entrypoint(main function) for lambda functions
CMD [ "main.get_employees_anniversary" ]

