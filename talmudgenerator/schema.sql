drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  seed text not null,
  'text' text not null
);