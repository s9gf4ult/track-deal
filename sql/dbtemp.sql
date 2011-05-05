CREATE TEMPORARY TABLE deals_view(
id integer primary key not null,
deal_id integer not null,
manual_made integer,
account_id integer not null,
paper_id integer not null,
paper_type text,
paper_class text,
paper_name text not null,
money_id integer not null,
money_name text,
point float,
step float,
datetime datetime not null,
datetime_formated text,
date date,
date_formated text,
time time,
time_formated text,
day_of_week integer,
day_of_week_formated text,
month integer,
month_formated text,
year integer,
points float not null,
price float not null,
price_formated text,
count float not null,
volume float not null,
volume_formated text,
direction integer not null,
direction_formated text,
net_before float,
net_after float,
paper_ballance_before float,
paper_ballance_after float,
user_attributes_formated text,
foreign key (deal_id) references deals(id),
foreign key (account_id) references accounts(id),
foreign key (paper_id) references papers(id),
foreign key (money_id) references moneys(id));

CREATE TEMPORARY TRIGGER _just_one_deals_view BEFORE INSERT ON deals_view
BEGIN
delete from deals_view where deal_id = new.deal_id;
END;

CREATE TEMPORARY TABLE positions_view(
id integer primary key not null,
account_id integer not null,
position_id integer not null,
money_id integer not null,
money_name text,
manual_made integer,
point float,
step float,
paper_id integer not null,
paper_type text,
paper_class text,
paper_name text not null,
direction float not null,
direction_formated text,
count float not null,
open_points float not null,
open_price float not null,
open_price_formated text,
open_volume float not null,
open_volume_formated text,
close_points float not null,
close_price float not null,
close_price_formated text,
close_volume float not null,
close_volume_formated text,
open_datetime datetime not null,
open_datetime_formated text,
open_date date,
open_date_formated text,
open_time time,
open_time_formated text,
open_day_of_week integer,
open_day_of_week_formated text,
open_month integer,
open_month_formated text,
open_year integer,
close_datetime datetime not null,
close_datetime_formated text,
close_date date,
close_date_formated text,
close_time time,
close_time_formated text,
close_day_of_week integer,
close_day_of_week_formated text,
close_month integer,
close_month_formated text,
close_year integer,
duration timedelta,
duration_formated text,
points_range float,
points_range_abs float,
points_range_abs_formated text,
price_range float,
price_range_abs float,
price_range_abs_formated text,
pl_gross float,
pl_gross_abs float,
pl_gross_abs_formated text,
pl_net float,
pl_net_abs float,
pl_net_abs_formated text,
steps_range float,
steps_range_abs float,
steps_range_abs_formated text,
percent_range float,
percent_range_abs float,
percent_range_abs_formated text,
commission float,
net_before float,
net_after float,
gross_before float,
gross_after float,
foreign key (position_id) references positions(id),
foreign key (account_id) references accounts(id),
foreign key (paper_id) references papers(id),
foreign key (money_id) references moneys(id));

CREATE TEMPORARY TRIGGER _just_one_positions_view BEFORE INSERT ON positions_view
BEGIN
delete from positions_view where position_id = new.position_id;
END;

CREATE TEMPORARY TABLE account_statistics(
id integer primary key not null,
account_id integer not null,
parameter_name text not null,
parameter_comment text,
value,
foreign key (account_id) references accounts(id),
unique(account_id, parameter_name));

CREATE TEMPORARY TABLE deal_paper_selected(
id integer,
paper_id integer,
deal_id integer,
foreign key (paper_id) references papers(id),
foreign key (deal_id) references deals(id));

CREATE TEMPORARY TRIGGER _just_one_deal_paper_selected BEFORE INSERT ON deal_paper_selected
BEGIN
delete from deal_paper_selected where paper_id = new.paper_id and deal_id = new.deal_id;
END;

CREATE TEMPORARY TABLE deal_account_selected(
id integer,
account_id integer,
deal_id integer,
foreign key (account_id) references accounts(id),
foreign key (deal_id) references deals(id));

CREATE TEMPORARY TRIGGER _just_one_deal_account_selected BEFORE INSERT ON deal_account_selected
BEGIN
delete from deal_account_selected where account_id = new.account_id and deal_id = new.deal_id;
END;

CREATE TEMPORARY TABLE position_account_selected(
id integer primary key not null,
position_id integer not null,
account_id integer not null,
foreign key (position_id) references positions(id),
foreign key (account_id) references accounts(id));

CREATE TEMPORARY TRIGGER _just_one_position_account_selected BEFORE INSERT ON position_account_selected
BEGIN
delete from position_account_selected where position_id = new.position_id and account_id = new.account_id;
END;

CREATE TEMPORARY TABLE position_paper_selected(
id integer primary key not null,
paper_id integer not null,
position_id integer not null,
foreign key (paper_id) references papers(id),
foreign key (position_id) references positions(id));

CREATE TEMPORARY TABLE account_ballance(
account_id integer,
paper_type text,
paper_class text,
paper_name text,
count float);

CREATE TEMPORARY TABLE accounts_view(
account_id integer,
name text,
money_name text,
first_money float,
current_money float,
deals integer,
positions integer);