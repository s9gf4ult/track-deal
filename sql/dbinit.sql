CREATE TABLE moneys(
id integer primary key not null,
name text not null,
full_name text);

CREATE TABLE accounts(
id integer primary key not null,
name text not null,
comments text,
money_id integer not null,
money_count float not null default 0,
foreign key (money_id) references moneys(id));

CREATE TABLE papers(
id integer primary key not null,
type text not null,
stock text,
class text,
name text not null,
full_name text);

CREATE TABLE points(
id integer primary key not null,
paper_id integer not null,
money_id integer not null,
point float not null,
step float not null,
foreign key (paper_id) references papers(id),
foreign key (money_id) references moneys(id),
unique(paper_id, money_id));
     
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
foreign key (account_id) references accounts(id),
foreign key (paper_id) references papers(id));
              
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
foreign key (parent_deal_id) references deals(id),
foreign key (account_id) references accounts(id),
foreign key (position_id) references positions(id),
foreign key (paper_id) references papers(id));

CREATE TABLE user_deal_attributes(
id integer primary key not null,
deal_id integer not null,
name text not null,
value,
foreign key (deal_id) references deals(id));

CREATE TABLE stored_deal_attributes(
id integer primary key not null,
deal_id integer not null,
type text not null,
value,
foreign key (deal_id) references deals(id));



CREATE TABLE user_position_attributes(
id integer primary key not null,
position_id integer not null,
name text not null,
value,
foreign key (position_id) references positions(id));

CREATE TABLE stored_position_attributes(
id integer primary key not null,
position_id integer not null,
type text not null,
value,
foreign key (position_id) references positions(id));



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
value_type text not null,
foreign key (paper_id) references papers(id));







CREATE TABLE global_data(
id integer primary key not null,
name text,
value );

CREATE TABLE database_attributes(
id integer primary key not null,
name text,
value );

CREATE TABLE hystory_steps(
id integer primary key not null,
autoname text);

CREATE TABLE undo_queries(
id integer primary key not null,
step_id integer not null,
query text not null,
foreign key (step_id) references hystory_steps(id));

CREATE TABLE redo_queries(
id integer primary key not null,
step_id integer not null,
query text not null,
foreign key (step_id) references hystory_steps(id));

CREATE TABLE current_hystory_position(
step_id integer not null,
foreign key (step_id) references hystory_steps(id));

CREATE TABLE filter_redelts(
id integer primary key not null,
parent_redelt integer not null,
value text not null,
foreign key (parent_redelt) references filter_redelts(id));

CREATE TABLE filters(
id integer primary key not null,
root_redelt_id integer not null,
query_type text not null,
from_part text not null,
comment text,
foreign key (root_redelt_id) references filter_redelts(id));

CREATE TABLE filter_conditions(
id integer primary key not null,
redelt_id integer not null,
left_value text,
right_value text,
binary_comparator text,
foreign key (redelt_id) references filter_redelts(id));
