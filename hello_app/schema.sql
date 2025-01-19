DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS kmeans_TrainingData;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  is_admin BOOLEAN NOT NULL DEFAULT 0,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  is_private BOOLEAN NOT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE kmeans_TrainingData (
  id INTEGER PRIMARY KEY,-- AUTOINCREMENT,
  account_1 FLOAT,
  account_2 FLOAT,
  account_3 FLOAT,
  account_4 FLOAT,
  account_5 FLOAT,
  account_6 FLOAT,
  account_7 FLOAT,
  account_8 FLOAT,
  account_9 FLOAT,
  account_10 FLOAT,
  account_11 FLOAT,
  account_12 FLOAT,
  cluster INTEGER NOT NULL,
  if_train BOOLEAN NOT NULL
);