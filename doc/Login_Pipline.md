## 主要服务

| 应用服务 | 用途                                                         | 是否可以跨区域分布式部署                       |                                      |
| -------- | ------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------ |
| as       | 账号服务，用于管理为知笔记账号等相关信息                     | 不能跨区域部署。                               | 无状态服务，可以启用多个服务同时工作 |
| ks       | 数据服务，以knowledge base（简称kb，知识库。一个用户的个人笔记为一个kb，一个群组的笔记也是一个kb）为单位，存储笔记/附件等数据。同时包含搜索服务。 | 可以跨区域部署，不同的kb可以保存在不同的区域。 | 无状态服务，可以启用多个服务同时工作 |

## 账号服务

`WizKMAccountsServer` 类负责账号服务。

### 登录流程

`WizToken` 是单例模式，保存有用户名和密码。

```cpp
    // FIXME: move to WizService initialize
    WizToken token;
    ...
    WizToken::setUserId(strUserId);
    WizToken::setPasswd(strPassword);
```

### 获取 Token

在 WizQTClient 中，这一步由 `WizToken` 类负责实现：

```cpp
QString WizTokenPrivate::token()
{
    QMutexLocker locker(m_mutex);
    Q_UNUSED(locker);
    // 判断是否尚未获取Token
    if (m_info.strToken.isEmpty())
    {
        WizKMAccountsServer asServer;
        if (asServer.login(m_strUserId, m_strPasswd))
        {
            m_info = asServer.getUserInfo();
            // 设置过期时间
            m_info.tTokenExpried = QDateTime::currentDateTime().addSecs(TOKEN_TIMEOUT_INTERVAL);
            return m_info.strToken;
        }
        else
        {
            m_lastErrorCode = asServer.getLastErrorCode();
            m_lastErrorMessage = asServer.getLastErrorMessage();
            m_bLastIsNetworkError = asServer.isNetworkError();
            return QString();
        }
    }
    // 判断Token是否已过期
    if (m_info.tTokenExpried >= QDateTime::currentDateTime())
    {
        return m_info.strToken;
    }
    else
    {
        WIZUSERINFO info = m_info;
        WizKMAccountsServer asServer;
        asServer.setUserInfo(info);

        // 延长Token有效期
        if (asServer.keepAlive())
        {
            m_info.tTokenExpried = QDateTime::currentDateTime().addSecs(TOKEN_TIMEOUT_INTERVAL);
            return m_info.strToken;
        }
        else
        {
            QString strToken;
            // 重新登录
            if (asServer.getToken(m_strUserId, m_strPasswd, strToken))
            {
                m_info.strToken = strToken;
                m_info.tTokenExpried = QDateTime::currentDateTime().addSecs(TOKEN_TIMEOUT_INTERVAL);
                return m_info.strToken;
            }
            else
            {
                m_lastErrorCode = asServer.getLastErrorCode();
                m_lastErrorMessage = asServer.getLastErrorMessage();
                m_bLastIsNetworkError = asServer.isNetworkError();
                return QString();
            }
        }
    }

    Q_ASSERT(0);
}
```

Token 的过期时间为 20 分钟：

```cpp
// use 10 minutes locally, server use 20 minutes
#define TOKEN_TIMEOUT_INTERVAL 60 * 10
```

也就是说获取 Token 的 URL 为 `https://as.wiz.cn/as/user/token` 或者 `https://as.wiz.cn/as/user/token`  ，这两个 API 基本一致。

尝试一下获取 Token：

```
http -j POST https://as.wiz.cn/as/user/token userId=test_api@test.com password=123456789
```

返回信息如下：

```json
HTTP/1.1 200 OK
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: Cache-Control, Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, X-Wiz-Referer, X-Wiz-Token
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Connection: keep-alive
Content-Encoding: gzip
Content-Type: application/json; charset=utf-8
Date: Thu, 26 Sep 2019 15:32:59 GMT
Server: nginx
Transfer-Encoding: chunked
Vary: Accept-Encoding

{
    "externCode": "",
    "result": {
        "avatarVersion": null,
        "clientType": "unknown",
        "created": 1569511954000,
        "displayName": "test_api",
        "displayname": "test_api",
        "dtCreated": 1569511954000,
        "email": "test_api@test.com",
        "emailVerify": "no",
        "gmtOffset": 156,
        "id": 4686204,
        "inviteCode": "dd1141a0",
        "kbGuid": "dcd63470-e072-11e9-ac13-a304bc11c13b",
        "kbServer": "https://vipkshttps4.wiz.cn",
        "kbType": "person",
        "kbXmlRpcServer": "https://vipkshttps4.wiz.cn/wizks/xmlrpc",
        "lang": "en",
        "lastLogin": 1569511955000,
        "locked": false,
        "maxAge": 900,
        "medalCount": 0,
        "mobile": null,
        "mobileVerify": "no",
        "mywizEmail": "test_api-5dq@mywiz.cn",
        "noticeLink": "",
        "noticeText": "",
        "points": 110,
        "snsList": "sina=新浪微博,0",
        "syncType": 100,
        "tenantId": null,
        "token": "a6d54add4e7cecd11f243a307a052bf7gyhnpzchgirott",
        "uploadSizeLimit": 104857600,
        "user": {
            "created": 1569511954000,
            "displayName": "test_api",
            "email": "test_api@test.com",
            "mobile": null,
            "userGuid": "dc870300-e072-11e9-ac13-a304bc11c13b",
            "userId": "test_api@test.com"
        },
        "userGuid": "dc870300-e072-11e9-ac13-a304bc11c13b",
        "userId": "test_api@test.com",
        "userLanguage": "en",
        "userLevel": 0,
        "userLevelName": "幼儿园",
        "userPoints": 110,
        "userState": 2,
        "userType": "free",
        "vip": false,
        "vipDate": null
    },
    "returnCode": 200,
    "returnMessage": "OK",
    "return_code": 200,
    "return_message": "success"
}
```



### 登录账户

”登录“ 这个操作是针对客户端而言的，实际上在获取 Token 的过程中，用户的所有信息已经获取了。

下面是 `login` 函数的实现：

```cpp
bool WizKMAccountsServer::login(const QString& strUserName, const QString& strPassword)
{
    if (m_bLogin)
    {
        return TRUE;
    }
    //
    QString urlPath = "/as/user/login";
    Json::Value params;
    params["userId"] = strUserName.toStdString();
    params["password"] = strPassword.toStdString();
    //
    m_bLogin = WithResult::execStandardJsonRequest<WIZUSERINFO>(*this, urlPath, m_userInfo, "POST", params);
    //
    qDebug() << "new server" << m_userInfo.strKbServer;
    //
    return m_bLogin;
}
```



### 保持登录状态

服务端返回的 Token 实际有效期是 15 分钟，但客户端使用保守的 10 分钟。因此，当判断 Token 过期时，会先尝试利用旧 Token 来延长有效期。

```C++
bool WizKMAccountsServer::keepAlive()
{
    QString urlPath = "/as/user/keep";
    //
    WIZSTANDARDRESULT jsonRet = NoResult::execStandardJsonRequest(*this, urlPath);
    if (!jsonRet)
    {
        TOLOG1("Failed to call %1", urlPath);
        return false;
    }
    //
    return true;
}
```

### 创建账户

这个API似乎是无效的。

```C++
bool WizKMAccountsServer::createAccount(const QString& strUserName, const QString& strPassword, const QString& strInviteCode, const QString& strCaptchaID, const QString& strCaptcha)
{
    QString urlPath = "/as/user/register";
    Json::Value params;
    params["userId"] = strUserName.toStdString();
    params["password"] = strPassword.toStdString();
    params["inviteCode"] = strInviteCode.toStdString();
    params["productName"] = "WizNoteQT";
    if (!strCaptchaID.isEmpty())
    {
        params["captchaId"] = strCaptchaID.toStdString();
        params["captcha"] = strCaptcha.toStdString();
    }
    //
    if (!WithResult::execStandardJsonRequest<WIZUSERINFO>(*this, urlPath, m_userInfo, "POST", params))
    {
        TOLOG("Failed to create account");
        return false;
    }
    //
    return true;
}
```