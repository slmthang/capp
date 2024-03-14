DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  dob DATE,
  gender VARCHAR(100),
  code INTEGER
);


-- INSERT INTO users VALUES( 0, "slm", "slmthang99@gmail.com", "password1", "2011-01-01", "male", "323");


CREATE TABLE events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(100) UNIQUE NOT NULL,
  owner INTEGER UNIQUE NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  location VARCHAR(100),
  description VARCHAR(100),
  creation_date DATE NOT NULL,
  FOREIGN KEY (owner) REFERENCES users (user_id)
);