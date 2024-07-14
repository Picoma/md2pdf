FROM python:3.11-slim

WORKDIR /opt/md2pdf
COPY src ./

RUN apt update && apt install pandoc -y
RUN python3 -m pip install Flask gunicorn
RUN apt install npm -y && npm install -g @mermaid-js/mermaid-cli

EXPOSE 5000
WORKDIR /opt/md2pdf/app
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]