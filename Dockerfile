# Use the official Microsoft Playwright image with Python pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set up user permissions for Hugging Face Spaces (user ID 1000)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install streamlit for the Web UI
RUN pip install --no-cache-dir streamlit pandas

# Copy the rest of the application
COPY --chown=user . .

# Set env variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Expose Hugging Face default port
EXPOSE 7860

# Start Streamlit UI
CMD ["streamlit", "run", "src/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
