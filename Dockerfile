# Lean base, faster builds
FROM python:3.11-slim

# Headless plotting + sane Python defaults for CI
ENV MPLBACKEND=Agg \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Work inside /app
WORKDIR /app

# Install deps first (better layer caching)
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy only what we need to run the analysis
COPY analysis/ analysis/
COPY data/ data/

# Run Task 1 analysis (produces CSV/PNG in analysis/outputs)
CMD ["python", "analysis/data_analysis.py"]