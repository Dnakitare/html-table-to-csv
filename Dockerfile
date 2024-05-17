# Use a lightweight Linux base image for cross-compilation
FROM ubuntu:20.04 AS build

# Install necessary packages for cross-compilation
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    build-essential \
    mingw-w64 \
    zip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller and other Python dependencies
RUN pip3 install pyinstaller

# Set up working directory
WORKDIR /src
RUN mkdir dist

# Copy the requirements and the script
COPY requirements.txt .
COPY html_to_csv.py .

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Cross-compile the script to a Windows executable
RUN pyinstaller --onefile html_to_csv.py

# List the contents of the /src/dist directory to verify the executable
RUN ls -l /src/dist

# Final stage: Create a minimal image with the compiled executable
FROM scratch AS export-stage
COPY --from=build src/dist/html_to_csv /html_to_csv.exe

# Set entrypoint to the executable
ENTRYPOINT ["/html_to_csv.exe"]