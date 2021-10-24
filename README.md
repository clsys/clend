# clend

## 安装依赖包
conda 批量导出包含环境中所有组件的requirements.txt文件
````shell
conda list -e > requirements.txt
````
conda 批量安装requirements.txt文件中包含的组件依赖
````shell
conda install --yes --file requirements.txt    #这种执行方式，一遇到安装不上就整体停止不会继续下面的包安装
FOR /F "delims=~" %f in (requirements.txt) DO conda install --yes "%f" #这个执行能解决上面出现的不执行后续包的问题
````
## 项目配置
### 项目运行需要的组件
1. Mysql
2. Redis

### 下面两个配置
#### Mysql配置
在settings.py中找到

````python
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': './clend/my123.cnf',
        },
    }
}
````
数据库配置文件my123.cnf

````commandline
[client]
database = db
host = 11.11.11.11
user = root
password = root
default-character-set = utf8
````
#### gateway连接配置
在settings.py中找到
````python
SETTING_FILENAME: Path = BASE_DIR.joinpath("clend").joinpath("setting.json")
````
gateway连接配置文件setting.json
````json
{
  "font.size": 12,
  "log.active": true,
  "log.level": 50,
  "log.console": true,
  "log.file": true,
  "datafeed.name": "udata",
  "datafeed.username": "token",
  "datafeed.password": "xxxx",
  "database.timezone": "Asia/Shanghai",
  "database.name": "mysql",
  "database.database": "xx",
  "database.host": "11.11.11.11",
  "database.port": 3306,
  "database.user": "root",
  "database.password": "root",
  "xtp.username": "xxxxxxxxxx9",
  "xtp.password": "xxxxxxxx",
  "xtp.clentid": 1,
  "xtp.maip": "11.11.11.11",
  "xtp.maport": 6002,
  "xtp.taip": "11.11.11.11",
  "xtp.taport": 6101,
  "xtp.protocol": "TCP",
  "xtp.code": "xxxxxxxxxxxxxxxxxxxx9xxxxxx9112e"
}
````
## 运行项目
### 本地开发环境运行
````shell
python manage.py runserver
````
### docker 运行
````shell
docker run -d --name clend -p 8000:8000 -v setting.json:/usr/src/app/setting.json -v my123.cnf:/usr/src/app/my123.cnf hhvssqg/clend:0.1
````

## 相关文档
[django文档](https://docs.djangoproject.com/zh-hans/3.2/)
[django文档](https://docs.djangoproject.com/zh-hans/3.2/)