FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Fix Windows CRLF line endings in start.sh and make it executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

CMD ["./start.sh"]