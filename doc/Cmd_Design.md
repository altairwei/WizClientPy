## 登录

`wizcli login` 登陆后输出格式化的用户信息到终端。

`wizcli login --local-user` 将会参考客户端的逻辑，寻找本地已经记住的用户名和密码。如果没有提供 `--user-id` ， 那么将会尝试读取本地默认用户名。

`wizcli login --remember` 将会在手动输入用户名和密码后，参考客户端逻辑将其储存在本地数据库。

## 同步

`wizcli sync` 参考客户端逻辑，同步本地账户数据库。

`wizcli sync create` 在服务端创建一个用户。

`wizcli sync push <src_dir>` 强制将本地数据库或者指定位置存在的数据库推送到服务端账户。

`wizcli sync pull <dest_dir>` 强制将服务端数据同步到本地账户或者指定位置，忽略本地账户或者指定位置已经存在的数据。