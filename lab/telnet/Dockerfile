FROM python:3.12-slim

COPY fake_telnet.py /fake_telnet.py

EXPOSE 23

# -u: unbuffered output, so the log line appears immediately
CMD ["python", "-u", "/fake_telnet.py"]