CREATE TABLE database_attributes(
id integer primary key not null,
name text,
value ,
unique(name));
        
CREATE TABLE moneys(
id integer primary key not null,
name text not null,
full_name text);

CREATE TRIGGER moneys_changed AFTER UPDATE ON moneys BEGIN
insert into database_attributes(name, value) values ('moneys_changed', 1);
END;

CREATE TABLE accounts(
id integer primary key not null,
name text not null,
comments text,
money_id integer not null,
money_count float not null default 0,
foreign key (money_id) references moneys(id) on delete cascade);

CREATE TRIGGER accounts_changed AFTER UPDATE ON accounts BEGIN
insert into database_attributes(name, value) values ('accounts_changed', 1);
END;

CREATE TABLE papers(
id integer primary key not null,
type text not null,
stock text,
class text,
name text not null,
full_name text,
unique(type, name));

CREATE TRIGGER papers_changed AFTER UPDATE ON papers BEGIN
insert into database_attributes(name, value) values ('papers_changed', 1);
END;

CREATE TABLE points(
id integer primary key not null,
paper_id integer not null,
money_id integer not null,
point float not null,
step float not null,
foreign key (paper_id) references papers(id) on delete cascade,
foreign key (money_id) references moneys(id) on delete cascade,
unique(paper_id, money_id));

CREATE TRIGGER points_inserted AFTER INSERT ON points BEGIN
insert into database_attributes(name, value) values ('points_changed', 1);
END;

CREATE TRIGGER points_updated AFTER UPDATE ON points BEGIN
insert into database_attributes(name, value) values ('points_changed', 1);
END;

CREATE TRIGGER points_deleted AFTER DELETE ON points BEGIN
insert into database_attributes(name, value) values ('points_changed', 1);
END;
     
CREATE TABLE positions(
id integer primary key not null,
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

CREATE TRIGGER positions_inserted AFTER INSERT ON positions BEGIN
insert into database_attributes(name, value) values ('positions_changed', 1);
END;

CREATE TRIGGER positions_deleted AFTER DELETE ON positions BEGIN
insert into database_attributes(name, value) values ('positions_changed', 1);
END;

CREATE TRIGGER positions_updated AFTER UPDATE ON positions BEGIN
insert into database_attributes(name, value) values ('positions_changed', 1);
END;

CREATE TABLE deals(
id integer primary key not null,
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

CREATE TRIGGER deals_inserted AFTER INSERT ON deals BEGIN
insert into database_attributes(name, value) values ('deals_changed', 1);
END;

CREATE TRIGGER deals_deleted AFTER DELETE ON deals BEGIN
insert into database_attributes(name, value) values ('deals_changed', 1);
END;

CREATE TRIGGER deals_updated AFTER UPDATE ON deals BEGIN
insert into database_attributes(name, value) values ('deals_changed', 1);
END;

CREATE TABLE user_deal_attributes(
id integer primary key not null,
deal_id integer not null,
name text not null,
value,
foreign key (deal_id) references deals(id) on delete cascade,
unique(deal_id, name));

CREATE TRIGGER deals_attributes_inserted AFTER INSERT ON user_deal_attributes BEGIN
insert into database_attributes(name, value) values ('deals_attributes_changed', 1);
END;

CREATE TRIGGER deals_attributes_updated AFTER UPDATE ON user_deal_attributes BEGIN
insert into database_attributes(name, value) values ('deals_attributes_changed', 1);
END;

CREATE TRIGGER deals_attributes_deleted AFTER DELETE ON user_deal_attributes BEGIN
insert into database_attributes(name, value) values ('deals_attributes_changed', 1);
END;

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

CREATE TRIGGER position_attributes_updated AFTER UPDATE ON user_position_attributes BEGIN
insert into database_attributes(name, value) values ('positions_attributes_changed', 1);
END;

CREATE TRIGGER position_attributes_inserted AFTER INSERT ON user_position_attributes BEGIN
insert into database_attributes(name, value) values ('positions_attributes_changed', 1);
END;

CREATE TRIGGER position_attributes_deleted AFTER DELETE ON user_position_attributes BEGIN
insert into database_attributes(name, value) values ('positions_attributes_changed', 1);
END;

CREATE TABLE stored_position_attributes(
id integer primary key not null,
position_id integer not null,
type text not null,
value,
foreign key (position_id) references positions(id) on delete cascade,
unique(position_id, type));

CREATE TABLE candles(
id integer primary key not null,
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

CREATE TABLE hystory_steps(
id integer primary key not null,
autoname text,
datetime datetime);

CREATE TABLE undo_queries(
id integer primary key not null,
step_id integer,
query text not null,
foreign key (step_id) references hystory_steps(id) on delete cascade);

CREATE TABLE redo_queries(
id integer primary key not null,
step_id integer,
query text not null,
foreign key (step_id) references hystory_steps(id) on delete cascade);

CREATE TABLE current_hystory_position(
step_id integer not null,
foreign key (step_id) references hystory_steps(id));

CREATE TRIGGER _just_one_hystorypos BEFORE INSERT ON current_hystory_position FOR EACH ROW BEGIN
delete from current_hystory_position;
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
