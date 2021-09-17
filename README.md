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

## 运行项目
````shell
python manage.py runserver
````

## 相关文档
[django文档](https://docs.djangoproject.com/zh-hans/3.2/)
