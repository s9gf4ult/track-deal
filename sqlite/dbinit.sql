CREATE TABLE database_attributes(
id integer primary key not null,
name text,
value ,
unique(name));
        
CREATE TABLE moneys(
id integer primary key not null,
name text not null,
full_name text,
unique(name));

CREATE TABLE accounts(
id integer primary key not null,
name text not null,
comments text,
money_id integer not null,
money_count float not null default 0,
foreign key (money_id) references moneys(id) on delete cascade);

CREATE TABLE account_in_out(
id integer primary key not null,
account_id integer not null,
datetime datetime not null,
money_count float not null,
foreign key (account_id) references accounts(id) on delete cascade);

CREATE TABLE papers(
id integer primary key not null,
type text not null,
stock text,
class text,
name text not null,
full_name text,
unique(type, name));

CREATE TABLE points(
id integer primary key not null,
paper_id integer not null,
money_id integer not null,
point float not null,
step float not null,
foreign key (paper_id) references papers(id) on delete cascade,
foreign key (money_id) references moneys(id) on delete cascade,
unique(paper_id, money_id));

CREATE TABLE positions(
id integer primary key autoincrement not null,
account_id integer not null,
paper_id integer not null,
count float not null,
direction integer not null,
commission float not null default 0,
open_datetime datetime not null,
close_datetime datetime not null,
open_points float not null,
close_points points not null,
manual_made integer,
do_not_delete integer,
foreign key (account_id) references accounts(id) on delete cascade,
foreign key (paper_id) references papers(id) on delete cascade);

CREATE TABLE deals(
id integer primary key autoincrement not null,
sha1 text,
manual_made integer,
parent_deal_id integer,
account_id integer not null,
position_id integer,
paper_id integer not null,
count float not null,
direction integer not null,
points float not null,
commission float not null default 0,
datetime datetime not null,
foreign key (parent_deal_id) references deals(id) on delete cascade,
foreign key (account_id) references accounts(id) on delete cascade,
foreign key (position_id) references positions(id) on delete set null,
foreign key (paper_id) references papers(id) on delete cascade,
unique(sha1, account_id));

CREATE INDEX deals_datetime on deals(datetime);

CREATE TABLE user_deal_attributes(
id integer primary key not null,
deal_id integer not null,
name text not null,
value,
foreign key (deal_id) references deals(id) on delete cascade,
unique(deal_id, name));

CREATE TABLE stored_deal_attributes(
id integer primary key not null,
deal_id integer not null,
type text not null,
value,
foreign key (deal_id) references deals(id) on delete cascade,
unique(deal_id, type));

CREATE TABLE user_position_attributes(
id integer primary key not null,
position_id integer not null,
name text not null,
value,
foreign key (position_id) references positions(id) on delete cascade,
unique(position_id, name));

CREATE TABLE stored_position_attributes(
id integer primary key not null,
position_id integer not null,
type text not null,
value,
foreign key (position_id) references positions(id) on delete cascade,
unique(position_id, type));

CREATE TABLE candles(
id integer primary key autoincrement not null,
paper_id integer not null,
duration text not null,
open_datetime datetime not null,
close_datetime datetime not null,
open_value float not null,
close_value float not null,
min_value float not null,
max_value float not null,
volume float,
value_type text not null,
foreign key (paper_id) references papers(id) on delete cascade,
unique(paper_id, duration, value_type, open_datetime),
unique(paper_id, duration, value_type, close_datetime));

CREATE TABLE global_data(
id integer primary key not null,
name text,
value ,
unique(name));

CREATE TRIGGER _just_one_global_data BEFORE INSERT ON global_data FOR EACH ROW BEGIN
DELETE FROM global_data where name = new.name;
END;

CREATE TRIGGER _just_one_database_attributes BEFORE INSERT ON database_attributes FOR EACH ROW BEGIN
DELETE FROM database_attributes where name = new.name;
END;

CREATE TABLE history_steps(
id integer primary key autoincrement not null, /*this will increase count of tables in 1*/
autoname text,
datetime datetime);

CREATE TABLE undo_queries(
id integer primary key autoincrement not null,
step_id integer,
query text not null,
foreign key (step_id) references history_steps(id) on delete cascade);

CREATE TABLE redo_queries(
id integer primary key autoincrement not null,
step_id integer,
query text not null,
foreign key (step_id) references history_steps(id) on delete cascade);

CREATE TABLE current_history_position(
step_id integer not null,
foreign key (step_id) references history_steps(id) on delete cascade);

CREATE TRIGGER _just_one_historypos BEFORE INSERT ON current_history_position FOR EACH ROW BEGIN
delete from current_history_position;
END;

CREATE TABLE filter_redelts(
id integer primary key not null,
parent_redelt integer not null,
value text not null,
foreign key (parent_redelt) references filter_redelts(id) on delete cascade);

CREATE TABLE filters(
id integer primary key not null,
root_redelt_id integer not null,
query_type text not null,
from_part text not null,
comment text,
foreign key (root_redelt_id) references filter_redelts(id) on delete set null,
unique(root_redelt_id));

CREATE TABLE filter_conditions(
id integer primary key not null,
redelt_id integer not null,
is_formula integer,
left_value text,
right_value text,
binary_comparator text,
foreign key (redelt_id) references filter_redelts(id) on delete cascade);
