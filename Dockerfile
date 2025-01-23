FROM python:3.12

WORKDIR /app


COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y wkhtmltopdf

COPY app.py /app/
COPY templates /app/templates
COPY static /app/static
COPY db /app/db
COPY outputs /app/outputs

EXPOSE 5000

CMD ["python", "/app/app.py"]
