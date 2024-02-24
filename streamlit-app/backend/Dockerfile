from rstudio/plumber as main

# Set the working directory to /app
WORKDIR /app

COPY requirements.R /app/requirements.R
RUN R -e "source('requirements.R')"

COPY . app

# Expose port 8088 for the application to run on
EXPOSE 8080

# CMD ["R", "-e", ./api.R"]