CREATE TABLE Album (
  aid int(11) NOT NULL AUTO_INCREMENT,
  aname char(20) DEFAULT NULL,
  uid int(11) NOT NULL,
  adate date DEFAULT NULL,
  cover longblob,
  PRIMARY KEY (aid),
  UNIQUE KEY aid_UNIQUE (aid),
  KEY uid_idx (uid),
  CONSTRAINT uid FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1


CREATE TABLE Comment (
  cid int(11) NOT NULL AUTO_INCREMENT,
  uid int(11) DEFAULT NULL,
  authorName varchar(45) DEFAULT NULL,
  content char(50) DEFAULT NULL,
  cdate date DEFAULT NULL,
  pid int(11) NOT NULL,
  PRIMARY KEY (cid),
  UNIQUE KEY cid_UNIQUE (cid),
  KEY comment_uid_idx (uid),
  KEY comment_pid_idx (pid),
  CONSTRAINT comment_pid FOREIGN KEY (pid) REFERENCES Photo (pid) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT comment_uid FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1



CREATE TABLE Friends (
  uid int(11) NOT NULL,
  f_uid int(11) NOT NULL,
  PRIMARY KEY (uid,f_uid),
  KEY friends_uid2_idx (f_uid),
  CONSTRAINT friends_uid FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT friends_uid2 FOREIGN KEY (f_uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1



CREATE TABLE Likes (
  uid int(11) NOT NULL,
  pid int(11) NOT NULL,
  KEY like_uid_idx (uid),
  KEY like_pid_idx (pid),
  CONSTRAINT like_pid FOREIGN KEY (pid) REFERENCES Photo (pid) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT like_uid FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1


CREATE TABLE Photo (
  pid int(11) NOT NULL AUTO_INCREMENT,
  data longblob NOT NULL,
  caption varchar(255) DEFAULT NULL,
  uid int(11) NOT NULL,
  aname char(20) NOT NULL,
  aid int(11) NOT NULL,
  likes int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (pid),
  UNIQUE KEY pid_UNIQUE (pid),
  KEY photo_uid_idx (uid),
  KEY photo_aid_idx (aid),
  CONSTRAINT photo_aid FOREIGN KEY (aid) REFERENCES Album (aid) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT photo_uid FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=latin1


CREATE TABLE Tag (
  word char(20) NOT NULL,
  pid int(11) NOT NULL,
  uid int(11) NOT NULL,
  KEY 1_idx (pid),
  KEY uidd_idx (uid),
  CONSTRAINT pidd FOREIGN KEY (pid) REFERENCES Photo (pid) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT uidd FOREIGN KEY (uid) REFERENCES Users (uid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1


CREATE TABLE Users (
  uid int(11) NOT NULL AUTO_INCREMENT,
  email varchar(50) NOT NULL,
  password varchar(50) NOT NULL,
  first varchar(20) NOT NULL,
  last varchar(20) NOT NULL,
  birth varchar(10) NOT NULL,
  hometown varchar(20) NOT NULL,
  gender varchar(10) NOT NULL,
  contribution int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (uid),
  UNIQUE KEY email (email),
  UNIQUE KEY uid_UNIQUE (uid)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1