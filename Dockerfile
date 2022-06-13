FROM python:3.9.1
# FROM public.ecr.aws/lambda/python:3.9

RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /root/requirements.txt
RUN pip install --no-cache-dir -r /root/requirements.txt
RUN rm /root/requirements.txt

COPY ./ ./app/
WORKDIR /app

CMD ["python3", "main.py"]
# CMD ["main.handler"]