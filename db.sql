CREATE TABLE coins(
  id SERIAL PRIMARY KEY,
  coin VARCHAR(255),
  news TEXT,
  summary TEXT
);