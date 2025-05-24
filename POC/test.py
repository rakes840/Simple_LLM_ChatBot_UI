Login error: (sqlite3.OperationalError) no such column: users.profile_updated_at
[SQL: SELECT users.id AS users_id, users.username AS users_username, users.email AS users_email, users.hashed_password AS users_hashed_password, users.last_login AS users_last_login, users.profile_updated_at AS users_profile_updated_at
FROM users
WHERE users.username = ?
 LIMIT ? OFFSET ?]
[parameters: ('Rakesh', 1, 0)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
