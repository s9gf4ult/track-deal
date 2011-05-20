/*
(defun gentriggers (table-name fields)
  (save-excursion
    (newline)
    (flet ((flds (fields)
                 (reduce (lambda (a b) (format "%s, %s" a b)) fields))
           (flds2 (new_old fields)
                  (reduce (lambda (a b) (format "%s||',%s" a b))
                          (mapcar (lambda (field)
                                    (format "%s = '||quote(%s.%s)" field new_old field)) fields)))
           (flds3 (new_old fields)
                  (reduce (lambda (a b) (format "%s||', '||%s" a b))
                          (mapcar (lambda (field) (format "quote(%s.%s)" new_old field)) fields))))
    (let (lines
          (selstep "(SELECT step_id from current_hystory_position limit 1)"))
      (push (format "CREATE TEMPORARY TRIGGER _insert_%s AFTER INSERT ON %s BEGIN" table-name table-name) lines)
      (push (format "INSERT INTO undo_queries (step_id, query) values (%s, 'DELETE FROM %s WHERE id = '||quote(new.id));" selstep table-name) lines)
      (push (format "INSERT INTO redo_queries (step_id, query) values (%s, 'INSERT INTO %s(%s) VALUES ('||%s||')');" selstep table-name (flds (cons "id" fields)) (flds3 "new" (cons "id" fields))) lines)
      (push "END;" lines)
      (push "" lines)
      (push (format "CREATE TEMPORARY TRIGGER _delete_%s AFTER DELETE ON %s BEGIN" table-name table-name) lines)
      (push (format "INSERT INTO redo_queries (step_id, query) values (%s, 'DELETE FROM %s WHERE id = '||quote(old.id));" selstep table-name) lines)
      (push (format "INSERT INTO undo_queries (step_id, query) values (%s, 'INSERT INTO %s(%s) VALUES ('||%s||')');" selstep table-name (flds (cons "id" fields)) (flds3 "old" (cons "id" fields))) lines)
      (push "END;" lines)
      (push "" lines)
      (push (format "CREATE TEMPORARY TRIGGER _update_%s AFTER UPDATE ON %s BEGIN" table-name table-name) lines)
      (push (format "INSERT INTO undo_queries(step_id, query) values (%s, 'UPDATE %s SET %s||' WHERE id = '||quote(new.id));" selstep table-name (flds2 "old" fields)) lines)
      (push (format "INSERT INTO redo_queries(step_id, query) values (%s, 'UPDATE %s SET %s||' WHERE id = '||quote(old.id));" selstep table-name (flds2 "new" fields)) lines)
      (push "END;" lines)
      (setf lines (reverse lines))
      (loop for line in lines do
            (progn (insert line)
            (newline)))))))
(defun genalltriggers (datalist)
  (loop for tt in (reverse datalist) do
        (save-excursion
          (newline)
          (apply #'gentriggers tt))))            
*/
CREATE TEMPORARY TABLE deal_groups(
id integer primary key not null,
direction integer not null,
paper_id integer not null);

CREATE TEMPORARY TABLE deal_group_assign(
deal_id integer not null,
group_id integer not null,
foreign key (group_id) references deal_groups(id) on delete cascade,
unique(deal_id));

CREATE TEMPORARY TRIGGER _just_one_deal_group_assign BEFORE INSERT ON deal_group_assign FOR EACH ROW
BEGIN
delete from deal_group_assign where deal_id = new.deal_id;
END;
        
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

CREATE TEMPORARY VIEW account_ballance AS
SELECT * FROM (
SELECT account_id, paper_type, paper_class, paper_name, sum(direction * count) as count FROM deals_view GROUP BY account_id, paper_id)
WHERE count <> 0;

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

/*
(genalltriggers '(("moneys" ("name" "full_name"))
                  ("candles" ("paper_id" "duration" "open_datetime" "close_datetime" "open_value" "close_value" "min_value" "max_value" "value_type"))
                  ("points" ("paper_id" "money_id" "point" "step"))
                  ("accounts" ("name" "comments" "money_id" "money_count"))
                  ("papers" ("type" "stock" "class" "name" "full_name"))
                  ("filters" ("root_redelt_id" "query_type" "from_part" "comment"))
                  ("filter_conditions" ("redelt_id" "is_formula" "left_value" "right_value" "binary_comparator"))
                  ("filter_redelts" ("parent_redelt" "value"))
                  ("positions" ("account_id" "paper_id" "count" "direction" "commission" "open_datetime" "close_datetime" "open_points" "close_points" "manual_made" "do_not_delete"))
                  ("user_position_attributes" ("position_id" "name" "value"))
                  ("stored_position_attributes" ("position_id" "type" "value"))
                  ("deals" ("sha1" "manual_made" "parent_deal_id" "account_id" "position_id" "paper_id" "count" "direction" "points" "commission" "datetime"))
                  ("stored_deal_attributes" ("deal_id" "type" "value"))
                  ("user_deal_attributes" ("deal_id" "name" "value"))))*/

CREATE TEMPORARY TRIGGER _insert_moneys AFTER INSERT ON moneys BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM moneys WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO moneys(id, name, full_name) VALUES ('||quote(new.id)||', '||quote(new.name)||', '||quote(new.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _delete_moneys AFTER DELETE ON moneys BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM moneys WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO moneys(id, name, full_name) VALUES ('||quote(old.id)||', '||quote(old.name)||', '||quote(old.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _update_moneys AFTER UPDATE ON moneys BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE moneys SET name = '||quote(old.name)||',full_name = '||quote(old.full_name)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE moneys SET name = '||quote(new.name)||',full_name = '||quote(new.full_name)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_candles AFTER INSERT ON candles BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM candles WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO candles(id, paper_id, duration, open_datetime, close_datetime, open_value, close_value, min_value, max_value, value_type) VALUES ('||quote(new.id)||', '||quote(new.paper_id)||', '||quote(new.duration)||', '||quote(new.open_datetime)||', '||quote(new.close_datetime)||', '||quote(new.open_value)||', '||quote(new.close_value)||', '||quote(new.min_value)||', '||quote(new.max_value)||', '||quote(new.value_type)||')');
END;

CREATE TEMPORARY TRIGGER _delete_candles AFTER DELETE ON candles BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM candles WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO candles(id, paper_id, duration, open_datetime, close_datetime, open_value, close_value, min_value, max_value, value_type) VALUES ('||quote(old.id)||', '||quote(old.paper_id)||', '||quote(old.duration)||', '||quote(old.open_datetime)||', '||quote(old.close_datetime)||', '||quote(old.open_value)||', '||quote(old.close_value)||', '||quote(old.min_value)||', '||quote(old.max_value)||', '||quote(old.value_type)||')');
END;

CREATE TEMPORARY TRIGGER _update_candles AFTER UPDATE ON candles BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE candles SET paper_id = '||quote(old.paper_id)||',duration = '||quote(old.duration)||',open_datetime = '||quote(old.open_datetime)||',close_datetime = '||quote(old.close_datetime)||',open_value = '||quote(old.open_value)||',close_value = '||quote(old.close_value)||',min_value = '||quote(old.min_value)||',max_value = '||quote(old.max_value)||',value_type = '||quote(old.value_type)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE candles SET paper_id = '||quote(new.paper_id)||',duration = '||quote(new.duration)||',open_datetime = '||quote(new.open_datetime)||',close_datetime = '||quote(new.close_datetime)||',open_value = '||quote(new.open_value)||',close_value = '||quote(new.close_value)||',min_value = '||quote(new.min_value)||',max_value = '||quote(new.max_value)||',value_type = '||quote(new.value_type)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_points AFTER INSERT ON points BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM points WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO points(id, paper_id, money_id, point, step) VALUES ('||quote(new.id)||', '||quote(new.paper_id)||', '||quote(new.money_id)||', '||quote(new.point)||', '||quote(new.step)||')');
END;

CREATE TEMPORARY TRIGGER _delete_points AFTER DELETE ON points BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM points WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO points(id, paper_id, money_id, point, step) VALUES ('||quote(old.id)||', '||quote(old.paper_id)||', '||quote(old.money_id)||', '||quote(old.point)||', '||quote(old.step)||')');
END;

CREATE TEMPORARY TRIGGER _update_points AFTER UPDATE ON points BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE points SET paper_id = '||quote(old.paper_id)||',money_id = '||quote(old.money_id)||',point = '||quote(old.point)||',step = '||quote(old.step)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE points SET paper_id = '||quote(new.paper_id)||',money_id = '||quote(new.money_id)||',point = '||quote(new.point)||',step = '||quote(new.step)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_accounts AFTER INSERT ON accounts BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM accounts WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO accounts(id, name, comments, money_id, money_count) VALUES ('||quote(new.id)||', '||quote(new.name)||', '||quote(new.comments)||', '||quote(new.money_id)||', '||quote(new.money_count)||')');
END;

CREATE TEMPORARY TRIGGER _delete_accounts AFTER DELETE ON accounts BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM accounts WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO accounts(id, name, comments, money_id, money_count) VALUES ('||quote(old.id)||', '||quote(old.name)||', '||quote(old.comments)||', '||quote(old.money_id)||', '||quote(old.money_count)||')');
END;

CREATE TEMPORARY TRIGGER _update_accounts AFTER UPDATE ON accounts BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE accounts SET name = '||quote(old.name)||',comments = '||quote(old.comments)||',money_id = '||quote(old.money_id)||',money_count = '||quote(old.money_count)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE accounts SET name = '||quote(new.name)||',comments = '||quote(new.comments)||',money_id = '||quote(new.money_id)||',money_count = '||quote(new.money_count)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_papers AFTER INSERT ON papers BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM papers WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO papers(id, type, stock, class, name, full_name) VALUES ('||quote(new.id)||', '||quote(new.type)||', '||quote(new.stock)||', '||quote(new.class)||', '||quote(new.name)||', '||quote(new.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _delete_papers AFTER DELETE ON papers BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM papers WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO papers(id, type, stock, class, name, full_name) VALUES ('||quote(old.id)||', '||quote(old.type)||', '||quote(old.stock)||', '||quote(old.class)||', '||quote(old.name)||', '||quote(old.full_name)||')');
END;

CREATE TEMPORARY TRIGGER _update_papers AFTER UPDATE ON papers BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE papers SET type = '||quote(old.type)||',stock = '||quote(old.stock)||',class = '||quote(old.class)||',name = '||quote(old.name)||',full_name = '||quote(old.full_name)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE papers SET type = '||quote(new.type)||',stock = '||quote(new.stock)||',class = '||quote(new.class)||',name = '||quote(new.name)||',full_name = '||quote(new.full_name)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_filters AFTER INSERT ON filters BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filters WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filters(id, root_redelt_id, query_type, from_part, comment) VALUES ('||quote(new.id)||', '||quote(new.root_redelt_id)||', '||quote(new.query_type)||', '||quote(new.from_part)||', '||quote(new.comment)||')');
END;

CREATE TEMPORARY TRIGGER _delete_filters AFTER DELETE ON filters BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filters WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filters(id, root_redelt_id, query_type, from_part, comment) VALUES ('||quote(old.id)||', '||quote(old.root_redelt_id)||', '||quote(old.query_type)||', '||quote(old.from_part)||', '||quote(old.comment)||')');
END;

CREATE TEMPORARY TRIGGER _update_filters AFTER UPDATE ON filters BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filters SET root_redelt_id = '||quote(old.root_redelt_id)||',query_type = '||quote(old.query_type)||',from_part = '||quote(old.from_part)||',comment = '||quote(old.comment)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filters SET root_redelt_id = '||quote(new.root_redelt_id)||',query_type = '||quote(new.query_type)||',from_part = '||quote(new.from_part)||',comment = '||quote(new.comment)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_filter_conditions AFTER INSERT ON filter_conditions BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filter_conditions WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filter_conditions(id, redelt_id, is_formula, left_value, right_value, binary_comparator) VALUES ('||quote(new.id)||', '||quote(new.redelt_id)||', '||quote(new.is_formula)||', '||quote(new.left_value)||', '||quote(new.right_value)||', '||quote(new.binary_comparator)||')');
END;

CREATE TEMPORARY TRIGGER _delete_filter_conditions AFTER DELETE ON filter_conditions BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filter_conditions WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filter_conditions(id, redelt_id, is_formula, left_value, right_value, binary_comparator) VALUES ('||quote(old.id)||', '||quote(old.redelt_id)||', '||quote(old.is_formula)||', '||quote(old.left_value)||', '||quote(old.right_value)||', '||quote(old.binary_comparator)||')');
END;

CREATE TEMPORARY TRIGGER _update_filter_conditions AFTER UPDATE ON filter_conditions BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filter_conditions SET redelt_id = '||quote(old.redelt_id)||',is_formula = '||quote(old.is_formula)||',left_value = '||quote(old.left_value)||',right_value = '||quote(old.right_value)||',binary_comparator = '||quote(old.binary_comparator)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filter_conditions SET redelt_id = '||quote(new.redelt_id)||',is_formula = '||quote(new.is_formula)||',left_value = '||quote(new.left_value)||',right_value = '||quote(new.right_value)||',binary_comparator = '||quote(new.binary_comparator)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_filter_redelts AFTER INSERT ON filter_redelts BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filter_redelts WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filter_redelts(id, parent_redelt, value) VALUES ('||quote(new.id)||', '||quote(new.parent_redelt)||', '||quote(new.value)||')');
END;

CREATE TEMPORARY TRIGGER _delete_filter_redelts AFTER DELETE ON filter_redelts BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM filter_redelts WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO filter_redelts(id, parent_redelt, value) VALUES ('||quote(old.id)||', '||quote(old.parent_redelt)||', '||quote(old.value)||')');
END;

CREATE TEMPORARY TRIGGER _update_filter_redelts AFTER UPDATE ON filter_redelts BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filter_redelts SET parent_redelt = '||quote(old.parent_redelt)||',value = '||quote(old.value)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE filter_redelts SET parent_redelt = '||quote(new.parent_redelt)||',value = '||quote(new.value)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_positions AFTER INSERT ON positions BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM positions WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO positions(id, account_id, paper_id, count, direction, commission, open_datetime, close_datetime, open_points, close_points, manual_made, do_not_delete) VALUES ('||quote(new.id)||', '||quote(new.account_id)||', '||quote(new.paper_id)||', '||quote(new.count)||', '||quote(new.direction)||', '||quote(new.commission)||', '||quote(new.open_datetime)||', '||quote(new.close_datetime)||', '||quote(new.open_points)||', '||quote(new.close_points)||', '||quote(new.manual_made)||', '||quote(new.do_not_delete)||')');
END;

CREATE TEMPORARY TRIGGER _delete_positions AFTER DELETE ON positions BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM positions WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO positions(id, account_id, paper_id, count, direction, commission, open_datetime, close_datetime, open_points, close_points, manual_made, do_not_delete) VALUES ('||quote(old.id)||', '||quote(old.account_id)||', '||quote(old.paper_id)||', '||quote(old.count)||', '||quote(old.direction)||', '||quote(old.commission)||', '||quote(old.open_datetime)||', '||quote(old.close_datetime)||', '||quote(old.open_points)||', '||quote(old.close_points)||', '||quote(old.manual_made)||', '||quote(old.do_not_delete)||')');
END;

CREATE TEMPORARY TRIGGER _update_positions AFTER UPDATE ON positions BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE positions SET account_id = '||quote(old.account_id)||',paper_id = '||quote(old.paper_id)||',count = '||quote(old.count)||',direction = '||quote(old.direction)||',commission = '||quote(old.commission)||',open_datetime = '||quote(old.open_datetime)||',close_datetime = '||quote(old.close_datetime)||',open_points = '||quote(old.open_points)||',close_points = '||quote(old.close_points)||',manual_made = '||quote(old.manual_made)||',do_not_delete = '||quote(old.do_not_delete)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE positions SET account_id = '||quote(new.account_id)||',paper_id = '||quote(new.paper_id)||',count = '||quote(new.count)||',direction = '||quote(new.direction)||',commission = '||quote(new.commission)||',open_datetime = '||quote(new.open_datetime)||',close_datetime = '||quote(new.close_datetime)||',open_points = '||quote(new.open_points)||',close_points = '||quote(new.close_points)||',manual_made = '||quote(new.manual_made)||',do_not_delete = '||quote(new.do_not_delete)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_user_position_attributes AFTER INSERT ON user_position_attributes BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM user_position_attributes WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO user_position_attributes(id, position_id, name, value) VALUES ('||quote(new.id)||', '||quote(new.position_id)||', '||quote(new.name)||', '||quote(new.value)||')');
END;

CREATE TEMPORARY TRIGGER _delete_user_position_attributes AFTER DELETE ON user_position_attributes BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM user_position_attributes WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO user_position_attributes(id, position_id, name, value) VALUES ('||quote(old.id)||', '||quote(old.position_id)||', '||quote(old.name)||', '||quote(old.value)||')');
END;

CREATE TEMPORARY TRIGGER _update_user_position_attributes AFTER UPDATE ON user_position_attributes BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE user_position_attributes SET position_id = '||quote(old.position_id)||',name = '||quote(old.name)||',value = '||quote(old.value)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE user_position_attributes SET position_id = '||quote(new.position_id)||',name = '||quote(new.name)||',value = '||quote(new.value)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_stored_position_attributes AFTER INSERT ON stored_position_attributes BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM stored_position_attributes WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO stored_position_attributes(id, position_id, type, value) VALUES ('||quote(new.id)||', '||quote(new.position_id)||', '||quote(new.type)||', '||quote(new.value)||')');
END;

CREATE TEMPORARY TRIGGER _delete_stored_position_attributes AFTER DELETE ON stored_position_attributes BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM stored_position_attributes WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO stored_position_attributes(id, position_id, type, value) VALUES ('||quote(old.id)||', '||quote(old.position_id)||', '||quote(old.type)||', '||quote(old.value)||')');
END;

CREATE TEMPORARY TRIGGER _update_stored_position_attributes AFTER UPDATE ON stored_position_attributes BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE stored_position_attributes SET position_id = '||quote(old.position_id)||',type = '||quote(old.type)||',value = '||quote(old.value)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE stored_position_attributes SET position_id = '||quote(new.position_id)||',type = '||quote(new.type)||',value = '||quote(new.value)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_deals AFTER INSERT ON deals BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM deals WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO deals(id, sha1, manual_made, parent_deal_id, account_id, position_id, paper_id, count, direction, points, commission, datetime) VALUES ('||quote(new.id)||', '||quote(new.sha1)||', '||quote(new.manual_made)||', '||quote(new.parent_deal_id)||', '||quote(new.account_id)||', '||quote(new.position_id)||', '||quote(new.paper_id)||', '||quote(new.count)||', '||quote(new.direction)||', '||quote(new.points)||', '||quote(new.commission)||', '||quote(new.datetime)||')');
END;

CREATE TEMPORARY TRIGGER _delete_deals AFTER DELETE ON deals BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM deals WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO deals(id, sha1, manual_made, parent_deal_id, account_id, position_id, paper_id, count, direction, points, commission, datetime) VALUES ('||quote(old.id)||', '||quote(old.sha1)||', '||quote(old.manual_made)||', '||quote(old.parent_deal_id)||', '||quote(old.account_id)||', '||quote(old.position_id)||', '||quote(old.paper_id)||', '||quote(old.count)||', '||quote(old.direction)||', '||quote(old.points)||', '||quote(old.commission)||', '||quote(old.datetime)||')');
END;

CREATE TEMPORARY TRIGGER _update_deals AFTER UPDATE ON deals BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE deals SET sha1 = '||quote(old.sha1)||',manual_made = '||quote(old.manual_made)||',parent_deal_id = '||quote(old.parent_deal_id)||',account_id = '||quote(old.account_id)||',position_id = '||quote(old.position_id)||',paper_id = '||quote(old.paper_id)||',count = '||quote(old.count)||',direction = '||quote(old.direction)||',points = '||quote(old.points)||',commission = '||quote(old.commission)||',datetime = '||quote(old.datetime)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE deals SET sha1 = '||quote(new.sha1)||',manual_made = '||quote(new.manual_made)||',parent_deal_id = '||quote(new.parent_deal_id)||',account_id = '||quote(new.account_id)||',position_id = '||quote(new.position_id)||',paper_id = '||quote(new.paper_id)||',count = '||quote(new.count)||',direction = '||quote(new.direction)||',points = '||quote(new.points)||',commission = '||quote(new.commission)||',datetime = '||quote(new.datetime)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_stored_deal_attributes AFTER INSERT ON stored_deal_attributes BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM stored_deal_attributes WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO stored_deal_attributes(id, deal_id, type, value) VALUES ('||quote(new.id)||', '||quote(new.deal_id)||', '||quote(new.type)||', '||quote(new.value)||')');
END;

CREATE TEMPORARY TRIGGER _delete_stored_deal_attributes AFTER DELETE ON stored_deal_attributes BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM stored_deal_attributes WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO stored_deal_attributes(id, deal_id, type, value) VALUES ('||quote(old.id)||', '||quote(old.deal_id)||', '||quote(old.type)||', '||quote(old.value)||')');
END;

CREATE TEMPORARY TRIGGER _update_stored_deal_attributes AFTER UPDATE ON stored_deal_attributes BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE stored_deal_attributes SET deal_id = '||quote(old.deal_id)||',type = '||quote(old.type)||',value = '||quote(old.value)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE stored_deal_attributes SET deal_id = '||quote(new.deal_id)||',type = '||quote(new.type)||',value = '||quote(new.value)||' WHERE id = '||quote(old.id));
END;


CREATE TEMPORARY TRIGGER _insert_user_deal_attributes AFTER INSERT ON user_deal_attributes BEGIN
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM user_deal_attributes WHERE id = '||quote(new.id));
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO user_deal_attributes(id, deal_id, name, value) VALUES ('||quote(new.id)||', '||quote(new.deal_id)||', '||quote(new.name)||', '||quote(new.value)||')');
END;

CREATE TEMPORARY TRIGGER _delete_user_deal_attributes AFTER DELETE ON user_deal_attributes BEGIN
INSERT INTO redo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'DELETE FROM user_deal_attributes WHERE id = '||quote(old.id));
INSERT INTO undo_queries (step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'INSERT INTO user_deal_attributes(id, deal_id, name, value) VALUES ('||quote(old.id)||', '||quote(old.deal_id)||', '||quote(old.name)||', '||quote(old.value)||')');
END;

CREATE TEMPORARY TRIGGER _update_user_deal_attributes AFTER UPDATE ON user_deal_attributes BEGIN
INSERT INTO undo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE user_deal_attributes SET deal_id = '||quote(old.deal_id)||',name = '||quote(old.name)||',value = '||quote(old.value)||' WHERE id = '||quote(new.id));
INSERT INTO redo_queries(step_id, query) values ((SELECT step_id from current_hystory_position limit 1), 'UPDATE user_deal_attributes SET deal_id = '||quote(new.deal_id)||',name = '||quote(new.name)||',value = '||quote(new.value)||' WHERE id = '||quote(old.id));
END;