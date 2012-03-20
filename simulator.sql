drop table if exists bots;
drop table if exists tasks;
drop table if exists logs;

# Bots 的信息
create table bots (
	bot tinytext,			# 名称
	info_ip int unsigned,	# IP 地址（Int32，用 INET_ATON, INET_NTOA）
	info_hostname tinytext,	# 主机名
	info_os tinytext,		# 操作系统版本
	ts_up timestamp not null default 0,		# 上线时间
	ts_down timestamp not null default 0,		# 下线时间（由服务器计算，不需要 Bot 提交）
	ts_lastact timestamp not null default 0	# 最后活动时间
);

# 指定 Bot 上需要执行的任务
# 任务包括 C&C、攻击等各种类型的操作，由模块名标识
create table tasks (
	id int auto_increment,	# 任务 ID，便于 Bot 识别是否为新任务
	bot tinytext,			# 指定任务执行者
	module tinytext,		# 模块名
	param_1 text,			# 第一个参数
	param_2 text,			# ...
	param_3 text,			# ...
	param_4 text,			# 第四个参数
	param_extra text,		# 还有更多参数？写在一起
	source tinytext,		# 任务来源（管理员，或者某 C&C 模块？）
	ts_created timestamp not null default 0,	# 任务创建时间（由任务创建者填写）
	ts_begin timestamp not null default 0,		# 开始执行时间（由 Bot 填写）
	ts_finish timestamp not null default 0,	# 完成时间（由 Bot 填写，不是必须的）
	cancelled bool default 0,  # 任务已被取消，Bot 应该终止该模块的运行
	primary key (id)
);

# 日志
create table logs (
	bot tinytext,			# Bot 名称
	module tinytext,		# 模块名
	ts timestamp,			# 时间
	type tinytext,			# 类型（DEBUG/INFO/WARNING/ERROR...）
	message text			# 消息内容
);
