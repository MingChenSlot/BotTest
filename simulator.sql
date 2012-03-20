drop table if exists bots;
drop table if exists tasks;
drop table if exists logs;

# Bots ����Ϣ
create table bots (
	bot tinytext,			# ����
	info_ip int unsigned,	# IP ��ַ��Int32���� INET_ATON, INET_NTOA��
	info_hostname tinytext,	# ������
	info_os tinytext,		# ����ϵͳ�汾
	ts_up timestamp not null default 0,		# ����ʱ��
	ts_down timestamp not null default 0,		# ����ʱ�䣨�ɷ��������㣬����Ҫ Bot �ύ��
	ts_lastact timestamp not null default 0	# ���ʱ��
);

# ָ�� Bot ����Ҫִ�е�����
# ������� C&C�������ȸ������͵Ĳ�������ģ������ʶ
create table tasks (
	id int auto_increment,	# ���� ID������ Bot ʶ���Ƿ�Ϊ������
	bot tinytext,			# ָ������ִ����
	module tinytext,		# ģ����
	param_1 text,			# ��һ������
	param_2 text,			# ...
	param_3 text,			# ...
	param_4 text,			# ���ĸ�����
	param_extra text,		# ���и��������д��һ��
	source tinytext,		# ������Դ������Ա������ĳ C&C ģ�飿��
	ts_created timestamp not null default 0,	# ���񴴽�ʱ�䣨�����񴴽�����д��
	ts_begin timestamp not null default 0,		# ��ʼִ��ʱ�䣨�� Bot ��д��
	ts_finish timestamp not null default 0,	# ���ʱ�䣨�� Bot ��д�����Ǳ���ģ�
	cancelled bool default 0,  # �����ѱ�ȡ����Bot Ӧ����ֹ��ģ�������
	primary key (id)
);

# ��־
create table logs (
	bot tinytext,			# Bot ����
	module tinytext,		# ģ����
	ts timestamp,			# ʱ��
	type tinytext,			# ���ͣ�DEBUG/INFO/WARNING/ERROR...��
	message text			# ��Ϣ����
);
