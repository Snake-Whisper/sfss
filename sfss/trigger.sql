CREATE TRIGGER groupSyncInsert
AFTER INSERT
ON sfss.groups
FOR EACH ROW
BEGIN
	DECLARE v_front TEXT DEFAULT NULL;
    DECLARE v_frontlen INT DEFAULT NULL;
    DECLARE v_user TEXT DEFAULT NULL;
    DECLARE v_userstring TEXT;
    DECLARE v_tmpUserGroups TEXT;
    DECLARE v_buffer TEXT;
    SET v_userstring = new.members;
    iterator:
    LOOP
		IF LENGTH(TRIM(v_userstring)) = 0 OR v_userstring IS NULL THEN
			LEAVE iterator;
		END IF;
		SET v_front = SUBSTRING_INDEX(v_userstring, ',', 1);
		SET v_frontlen = LENGTH(v_front);
		SET v_user = TRIM(v_front);
        select users.groups into v_tmpUserGroups from sfss.users where id = v_user;
        SET v_buffer = FIND_IN_SET(new.id , v_tmpUserGroups);
        IF v_buffer = 0 or v_buffer IS NULL THEN 
			UPDATE users set users.groups = concat_ws(",", v_tmpUserGroups, new.id) where users.id = v_user;
		END IF;			
		SET v_userstring = INSERT(v_userstring,1,v_frontlen + 1,'');
    END LOOP;
END$$

CREATE TRIGGER groupSyncUpdate
AFTER UPDATE
ON sfss.groups
FOR EACH ROW
BEGIN
	DECLARE v_front TEXT DEFAULT NULL;
    DECLARE v_frontlen INT DEFAULT NULL;
    DECLARE v_user TEXT DEFAULT NULL;
    DECLARE v_userstring TEXT;
	DECLARE v_olduserstring TEXT;
    DECLARE v_tmpUserGroups TEXT;
    DECLARE v_buffer TEXT;
    SET v_userstring = new.members;
	SET v_olduserstring = old.members;
	#commit delete user
	iterator:
    LOOP
		IF LENGTH(TRIM(v_olduserstring)) = 0 OR v_olduserstring IS NULL THEN
			LEAVE iterator;
		END IF;
		SET v_front = SUBSTRING_INDEX(v_olduserstring,',',1);
		SET v_frontlen = LENGTH(v_front);
		SET v_user = TRIM(v_front);
        select users.groups into v_tmpUserGroups from sfss.users where id = v_user;
		IF LENGTH(TRIM(v_tmpUserGroups)) = 0 OR v_tmpUserGroups IS NULL OR FIND_IN_SET(old.id, v_tmpUserGroups) = 0 THEN
			SET v_olduserstring = INSERT(v_olduserstring,1,v_frontlen + 1,'');
			ITERATE iterator;
		END IF;
		UPDATE users SET groups = TRIM( BOTH "," FROM REPLACE(REPLACE (v_tmpUserGroups, old.id, ""), ",,", ",")) WHERE id = v_user;
		SET v_olduserstring = INSERT(v_olduserstring,1,v_frontlen + 1,'');
    END LOOP;
	#commit add user
    iterator:
    LOOP
		IF LENGTH(TRIM(v_userstring)) = 0 OR v_userstring IS NULL THEN
			LEAVE iterator;
		END IF;
		SET v_front = SUBSTRING_INDEX(v_userstring,',',1);
		SET v_frontlen = LENGTH(v_front);
		SET v_user = TRIM(v_front);
        SELECT users.groups INTO v_tmpUserGroups FROM sfss.users WHERE id = v_user;
        SET v_buffer = FIND_IN_SET(new.id , v_tmpUserGroups);
        IF v_buffer = 0 or v_buffer IS NULL THEN 
			INSERT INTO sfss.TriggerLog (msg) VALUES(concat("executed: ", new.id));
			UPDATE users set users.groups = TRIM(BOTH "," FROM concat_ws(",", v_tmpUserGroups, new.id)) where users.id = v_user;
		END IF;			
		SET v_userstring = INSERT(v_userstring,1,v_frontlen + 1,'');
    END LOOP;
END$$

CREATE TRIGGER groupSyncDelete
AFTER DELETE
ON sfss.groups
FOR EACH ROW
BEGIN
	DECLARE v_front TEXT DEFAULT NULL;
    DECLARE v_frontlen INT DEFAULT NULL;
    DECLARE v_user TEXT DEFAULT NULL;
	DECLARE v_olduserstring TEXT;
    DECLARE v_tmpUserGroups TEXT;
	SET v_olduserstring = old.members;
	#commit delete user
	iterator:
    LOOP
		IF LENGTH(TRIM(v_olduserstring)) = 0 OR v_olduserstring IS NULL THEN
			LEAVE iterator;
		END IF;
		SET v_front = SUBSTRING_INDEX(v_olduserstring,',',1);
		SET v_frontlen = LENGTH(v_front);
		SET v_user = TRIM(v_front);
        SELECT users.groups INTO v_tmpUserGroups FROM sfss.users WHERE id = v_user;
		IF LENGTH(TRIM(v_tmpUserGroups)) = 0 OR v_tmpUserGroups IS NULL OR FIND_IN_SET(old.id, v_tmpUserGroups) = 0 THEN
			SET v_olduserstring = INSERT(v_olduserstring,1,v_frontlen + 1,'');
			ITERATE iterator;
		END IF;
		UPDATE users SET groups = TRIM( BOTH "," FROM REPLACE(REPLACE (v_tmpUserGroups, old.id, ""), ",,", ",")) WHERE id = v_user;
		SET v_olduserstring = INSERT(v_olduserstring,1,v_frontlen + 1,'');
    END LOOP;
END$$
