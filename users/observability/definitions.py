from observability.metrics import meter

user_login_count = meter.create_counter("user_login_count")
user_failed_login_count = meter.create_counter("user_failed_login_count")
