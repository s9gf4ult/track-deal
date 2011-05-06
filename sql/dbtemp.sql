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
commission float not null);

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
gross_after float);

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
unique(account_id, parameter_name));

CREATE TEMPORARY TABLE deal_paper_selected(
id integer,
paper_id integer,
deal_id integer);

CREATE TEMPORARY TRIGGER _just_one_deal_paper_selected BEFORE INSERT ON deal_paper_selected
BEGIN
delete from deal_paper_selected where paper_id = new.paper_id and deal_id = new.deal_id;
END;

CREATE TEMPORARY TABLE deal_account_selected(
id integer,
account_id integer,
deal_id integer);

CREATE TEMPORARY TRIGGER _just_one_deal_account_selected BEFORE INSERT ON deal_account_selected
BEGIN
delete from deal_account_selected where account_id = new.account_id and deal_id = new.deal_id;
END;

CREATE TEMPORARY TABLE position_account_selected(
id integer primary key not null,
position_id integer not null,
account_id integer not null);

CREATE TEMPORARY TRIGGER _just_one_position_account_selected BEFORE INSERT ON position_account_selected
BEGIN
delete from position_account_selected where position_id = new.position_id and account_id = new.account_id;
END;

CREATE TEMPORARY TABLE position_paper_selected(
id integer primary key not null,
paper_id integer not null,
position_id integer not null);

CREATE TEMPORARY TRIGGER _just_one_position_paper_selected BEFORE INSERT ON position_paper_selected
BEGIN
delete from position_paper_selected where paper_id = new.paper_id and position_id = new.position_id;
END;

-- CREATE TEMPORARY TABLE account_ballance(
-- account_id integer,
-- paper_type text,
-- paper_class text,
-- paper_name text,
-- count float);

CREATE TEMPORARY VIEW account_ballance AS
SELECT * FROM (
SELECT account_id, paper_type, paper_class, paper_name, sum(direction * count) as count FROM deals_view GROUP BY account_id, paper_id)
WHERE count <> 0;

-- CREATE TEMPORARY TABLE accounts_view(
-- account_id integer,
-- name text,
-- money_name text,
-- first_money float,
-- current_money float,
-- deals integer,
-- positions integer);

CREATE TEMPORARY VIEW accounts_view AS
SELECT
a.id as account_id,
a.name as name,
mm.name as money_name,
a.money_count as first_money,
(CASE WHEN ds.id THEN a.money_count + ds.profit ELSE a.money_count END) as current_money,
(CASE WHEN ds.id THEN ds.deals ELSE 0 END) as deals,
(CASE WHEN ps.id THEN ps.positions ELSE 0 END) as positions
FROM accounts a INNER JOIN moneys mm ON a.money_id = mm.id
LEFT JOIN (select account_id as id, count(id) as deals, sum(direction * volume) - sum(commission) as profit from deals_view group by account_id) ds ON ds.id = a.id
LEFT JOIN (select account_id as id, count(id) as positions from positions_view group by account_id) ps ON ps.id = a.id;

CREATE TEMPORARY TRIGGER _insert_moneys AFTER INSERT ON moneys
BEGIN
INSERT INTO undo_queries (step_id, query) values ((select step_id from current_hystory_position limit 1), 'DELETE FROM moneys WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((select step_id from current_hystory_position limit 1), 'INSERT INTO moneys (id, name, full_name) values ('||quote(new.id)||', '||quote(new.name)||', '||quote(new.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _delete_moneys AFTER DELETE ON moneys
BEGIN
INSERT INTO redo_queries (step_id, query) values ((select step_id from current_hystory_position limit 1), 'DELETE FROM moneys WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((select step_id from current_hystory_position limit 1), 'INSERT INTO moneys (id, name, full_name) values ('||quote(old.id)||', '||quote(old.name)||', '||quote(old.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _update_moneys AFTER UPDATE ON moneys
BEGIN
INSERT INTO undo_queries (step_id, query) VALUES ((select step_id from current_hystory_position limit 1), 'UPDATE moneys SET id = '||quote(old.id)||', name = '||quote(old.name)||', full_name = '||quote(old.full_name)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) VALUES ((select step_id from current_hystory_position limit 1), 'UPDATE moneys SET id = '||quote(new.id)||', name = '||quote(new.name)||', full_name = '||quote(new.full_name)||' WHERE id = '||quote(old.id));
END;
