FROM ruby:3.1.2

RUN apt-get update && \
    apt-get install -y \
    python3 python3-pip python3-dev \
    build-essential \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pandas geopandas folium

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

CMD ["irb"]
