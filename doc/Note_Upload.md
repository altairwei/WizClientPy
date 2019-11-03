## 主要服务

| 应用服务 | 用途                                                         | 是否可以跨区域分布式部署                       |                                      |
| -------- | ------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------ |
| as       | 账号服务，用于管理为知笔记账号等相关信息                     | 不能跨区域部署。                               | 无状态服务，可以启用多个服务同时工作 |
| ks       | 数据服务，以knowledge base（简称kb，知识库。一个用户的个人笔记为一个kb，一个群组的笔记也是一个kb）为单位，存储笔记/附件等数据。同时包含搜索服务。 | 可以跨区域部署，不同的kb可以保存在不同的区域。 | 无状态服务，可以启用多个服务同时工作 |

## 数据服务

`WizKMDatabaseServer` 负责管理数据服务 API 。

## KbValueVersions

`/as/user/kv/versions` 查询：

```shell
wizcli http -s get /as/user/kv/versions version=100 count=0 pageSize=0
```

返回结果：

```json
{
  "returnCode": 200,
  "returnMessage": "OK",
  "externCode": "",
  "result": [
    {
      "kbGuid": "50f12dc0-fa58-11e9-a766-55107cee3334",
      "versions": [
        {
          "key": "folders",
          "version": 1572359283417
        }
      ]
    }
  ]
}
```

## 获取笔记信息

### 获取笔记列表

查询：

```shell
wizcli http -s get /ks/note/list/version/dcd63470-e072-11e9-ac13-a304bc11c13b version=100 count=0 pageSize=0
```

返回结果似乎为空：

```json
{
  "returnCode": 200,
  "returnMessage": "OK",
  "externCode": "",
  "result": []
}
```

```C++
bool WizKMDatabaseServer::document_getList(int nCountPerPage, __int64 nStartVersion, std::deque<WIZDOCUMENTDATAEX>& arrayRet)
{
    QString urlPath = "/ks/note/list/version/" + getKbGuid();
    //
    return getJsonList<WIZDOCUMENTDATAEX>(*this, urlPath, nCountPerPage, nStartVersion, arrayRet);
}

bool WizKMDatabaseServer::document_getListByGuids(const CWizStdStringArray& arrayDocumentGUID, std::deque<WIZDOCUMENTDATAEX>& arrayRet)
{
    if (arrayDocumentGUID.empty())
        return true;
    //
    const WIZUSERINFOBASE info = userInfo();
    QString url = info.strKbServer + "/ks/note/list/guids/" + info.strKbGUID;
    //
    url = appendNormalParams(url, getToken());
    //
    Json::Value guids(Json::arrayValue);
    for (int i = 0; i < arrayDocumentGUID.size(); i++)
    {
        guids[i] = arrayDocumentGUID[i].toStdString();
    }
    //
    Json::FastWriter writer;
    std::string data = writer.write(guids);
    //
    return queryJsonList<WIZDOCUMENTDATAEX>(*this, url, "POST", QByteArray::fromStdString(data), arrayRet);
}

bool WizKMDatabaseServer::deleted_getList(int nCountPerPage, __int64 nStartVersion, std::deque<WIZDELETEDGUIDDATA>& arrayRet)
{
    QString urlPath = "/ks/deleted/list/version/" + getKbGuid();
    //
    return getJsonList<WIZDELETEDGUIDDATA>(*this, urlPath, nCountPerPage, nStartVersion, arrayRet);
}

bool WizKMDatabaseServer::deleted_postList(std::deque<WIZDELETEDGUIDDATA>& arrayDeletedGUID)
{
    QString urlPath = "/ks/deleted/upload/" + getKbGuid();
    //
    return postJsonList<WIZDELETEDGUIDDATA>(*this, urlPath, arrayDeletedGUID);
}
```

## 下载数据

### 下载笔记

```C++
bool WizKMDatabaseServer::document_downloadDataNew(const QString& strDocumentGUID, WIZDOCUMENTDATAEX& ret, const QString& oldFileName)
{
    QString url = buildUrl("/ks/note/download/" + m_userInfo.strKbGUID + "/" + strDocumentGUID + "?downloadData=1");
    // 查询笔记信息
    Json::Value doc;
    WIZSTANDARDRESULT jsonRet = WizRequest::execStandardJsonRequest(url, doc);
    m_lastJsonResult = jsonRet;
    if (!jsonRet)
    {
        setLastError(jsonRet);
        TOLOG1("Failed to download document data: %1", ret.strTitle);
        return false;
    }
    // 下载笔记数据（非HTML）
    Json::Value urlValue = doc["url"];
    if (!urlValue.isNull())
    {
        //encrypted note
        if (!::WizURLDownloadToData(urlValue.asString().c_str(), ret.arrayData))
        {
            TOLOG1("Failed to download document data: %1", ret.strTitle);
            return false;
        }
        //
        return true;
    }
    // 获取文档内容
    QString html = QString::fromUtf8(doc["html"].asString().c_str());
    if (html.isEmpty())
        return false;
    // 获取资源文件地址
    Json::Value resourcesObj = doc["resources"];
    //
    struct RESDATA : public WIZZIPENTRYDATA
    {
        QString url;
    };

    // 收集文档所需要的资源文件
    std::vector<RESDATA> serverResources;
    if (resourcesObj.isArray())
    {
        int resourceCount = resourcesObj.size();
        for (int i = 0; i < resourceCount; i++)
        {
            Json::Value resObj = resourcesObj[i];
            RESDATA data;
            data.name = QString::fromUtf8(resObj["name"].asString().c_str());
            data.url = QString::fromUtf8(resObj["url"].asString().c_str());
            data.size = atoi((resObj["size"].asString().c_str()));
            data.time = QDateTime::fromTime_t(resObj["time"].asInt64() / 1000);
            serverResources.push_back(data);
        }
    }
    // 创建文档压缩包
    WizTempFileGuard tempFile;
    WizZipFile newZip;
    if (!newZip.open(tempFile.fileName()))
    {
        TOLOG1("Failed to create temp file: %1", tempFile.fileName());
        return false;
    }
    // 压缩 index.html
    QByteArray htmlData;
    WizSaveUnicodeTextToData(htmlData, html, true);
    if (!newZip.compressFile(htmlData, "index.html"))
    {
        TOLOG("Failed to add index.html to zip file");
        return false;
    }
    // 检查旧压缩包是否存在
    WizUnzipFile oldZip;
    bool hasOldZip = false;
    if (WizPathFileExists(oldFileName))
    {
        if (!oldZip.open(oldFileName))
        {
            TOLOG1("Failed to open old file: %1", oldFileName);
        }
        else
        {
            hasOldZip = true;
        }
    }
    // 如果有旧的压缩包，则直接提取资源文件，压缩到新压缩包里
    for (intptr_t i = serverResources.size() - 1; i >= 0; i--)
    {
        auto res = serverResources[i];
        QString resName = "index_files/" + res.name;
        if (hasOldZip)
        {
            int index = oldZip.fileNameToIndex(resName);
            if (-1 != index)
            {
                QByteArray data;
                if (oldZip.extractFile(index, data))
                {
                    if (newZip.compressFile(data, resName))
                    {
                        serverResources.erase(serverResources.begin() + i);
                        continue;
                    }
                }
            }
        }
    }
    //
    QMutex mutex;
    // 只下载本地没有的资源文件
    int totalWaitForDownload = (int)serverResources.size();
    int totalDownloaded = 0;
    int totalFailed = 0;
    //
    int totalDownloadSize = 0;
    for (auto res : serverResources)
    {
        totalDownloadSize += res.size;
    }
    //
    m_objectsTotalSize = totalDownloadSize;
    // 依次下载资源文件
    for (auto res : serverResources)
    {
        QString resName = "index_files/" + res.name;
        //
#ifdef QT_DEBUG
        qDebug() << res.url;
#endif
        ::WizExecuteOnThread(WIZ_THREAD_DOWNLOAD_RESOURCES, [=, &mutex, &totalFailed, &totalDownloaded, &newZip] {
            //
            QByteArray data;
            qDebug() << "downloading " << resName;
            bool ret = WizURLDownloadToData(res.url, data, this, SLOT(onDocumentObjectDownloadProgress(QUrl, qint64, qint64)));
            qDebug() << "downloaded " << resName;
            //
            QMutexLocker locker(&mutex);
            if (!ret)
            {
                TOLOG1("Failed to download res: %1", res.url);
                totalFailed++;
                return;
            }
            //
            if (!newZip.compressFile(data, resName))
            {
                TOLOG("Failed to add data to zip file");
                totalFailed++;
                return;
                //
            }
            //
            totalDownloaded++;

        });
    }
    // 等待资源文件下载完成
    if (totalWaitForDownload > 0)
    {
        while (true)
        {
            if (totalWaitForDownload == totalDownloaded + totalFailed)
            {
                if (totalFailed == 0)
                    break;
                //
                return false;
            }
            //
            QEventLoop loop;
            loop.processEvents();
            //
            QThread::msleep(300);
        }
    }
    //
    if (!newZip.close())
    {
        TOLOG("Failed to close zip file");
        return false;
    }
    // 将压缩包读取到内存中
    if (!WizLoadDataFromFile(tempFile.fileName(), ret.arrayData))
    {
        TOLOG1("Failed to load data from file: %1", tempFile.fileName());
        return false;
    }
    //
    return true;
}
```

API 查询：

```shell
http get /ks/note/download/dcd63470-e072-11e9-ac13-a304bc11c13b/dce68820-e072-11e9-98a9-8372bbcbb603?downloadData=1
```

返回结果：

```json
{
  "returnCode": 200,
  "returnMessage": "OK",
  "externCode": "",
  "info": {
    "kbGuid": "dcd63470-e072-11e9-ac13-a304bc11c13b",
    "docGuid": "dce68820-e072-11e9-98a9-8372bbcbb603",
    "version": 2,
    "dataMd5": "175c77d3161306ff729c4a41eaa01067",
    "dataModified": 1569511955000,
    "infoMd5": "397af6f3e67ecdcee426481f572fe5c9",
    "infoModified": 1569511955000,
    "paramMd5": "00000000000000000000000000000000",
    "paramModified": "1970-01-01T00:00:00.000Z",
    "title": "Getting a Tidy Style by Markdown.md",
    "category": "/My Notes/",
    "owner": "test_api@test.com",
    "iconIndex": -1,
    "protected": 0,
    "readCount": 0,
    "attachmentCount": 0,
    "type": null,
    "fileType": null,
    "created": 1569511955000,
    "accessed": 1569511955000,
    "url": null,
    "styleGuid": null,
    "seo": null,
    "author": null,
    "keywords": null,
    "dataSize": 100,
    "abstractText": "Are you still struggling to which size should you select for the headline or how to style your article? Now you have the Markdown to give you a
simple experience on typesetting and help you concentrat",
    "abstractImage": 1
  },
  "html": "<!doctype html><html><head><title>Getting a Tidy Style by Markdown.md</title></head><body class=\"wiz-editor-body\" spellcheck=\"false\"></body></html>",
  "resources": [
    {
      "name": "635b26d3-35b5-4ac1-b2aa-759186202c0f.jpg",
      "time": 1561594904000,
      "size": 22510,
      "url": "https://vipkshttps4.wiz.cn/ks/object/download/dcd63470-e072-11e9-ac13-a304bc11c13b/dce68820-e072-11e9-98a9-8372bbcbb603?objType=resource&objId=635b26d3-35b5-4ac1-b2aa-759186202c0f.jpg&clientType=macos&clientVersion=None&wiz_es=1572774594038&wiz_signature=14e6e36fbe57a9c8a01d3e81da52d780"
    }
  ]
}
```

### 下载附件


```C++
bool WizKMDatabaseServer::attachment_downloadDataNew(const QString& strDocumentGUID, const QString& strAttachmentGUID, WIZDOCUMENTATTACHMENTDATAEX& ret)
{
    QString url = buildUrl("/ks/object/download/" + m_userInfo.strKbGUID + "/" + strDocumentGUID + "?objType=attachment&objId=" + strAttachmentGUID);
    return WizURLDownloadToData(url, ret.arrayData);
}
```

## 上传数据

### 上传笔记

```C++
bool WizKMDatabaseServer::document_postDataNew(const WIZDOCUMENTDATAEX& dataTemp, bool withData, __int64& nServerVersion)
{
    m_strLastLocalError.clear();
    // 拷贝笔记数据
    WIZDOCUMENTDATAEX data = dataTemp;
    // 构建地址
    QString url_main = buildUrl("/ks/note/upload/" + m_userInfo.strKbGUID + "/" + data.strGUID);
    QString url_res = buildUrl("/ks/object/upload/" + m_userInfo.strKbGUID + "/" + data.strGUID);
    //
    if (withData && data.arrayData.length() > 2)
    {
        if (data.arrayData[0] == 'P' && data.arrayData[1] == 'K')
        {
            if (data.nProtected != 0)
            {
                TOLOG("note is not encrypted, but protected is 1");
                data.nProtected = 0;
            }
        }
        else
        {
            if (data.nProtected != 1)
            {
                TOLOG("note is encrypted, but protected is 0");
                data.nProtected = 1;
            }
        }
    }
    //
    CString tags;
    ::WizStringArrayToText(data.arrayTagGUID, tags, "*");
    // 准备要发送的笔记数据
    Json::Value doc;
    doc["kbGuid"] = m_userInfo.strKbGUID.toStdString();
    doc["docGuid"] = data.strGUID.toStdString();
    doc["title"] = data.strTitle.toStdString();
    doc["dataMd5"] = data.strDataMD5.toStdString();
    doc["dataModified"] = (Json::UInt64)data.tDataModified.toTime_t() * (Json::UInt64)1000;
    doc["category"] = data.strLocation.toStdString();
    doc["owner"] = data.strOwner.toStdString();
    doc["protected"] = (int)data.nProtected;
    doc["readCount"] = (int)data.nReadCount;
    doc["attachmentCount"] = (int)data.nAttachmentCount;
    doc["type"] = data.strType.toStdString();
    doc["fileType"] = data.strFileType.toStdString();
    doc["created"] = (Json::UInt64)data.tCreated.toTime_t() * (Json::UInt64)1000;
    doc["accessed"] = (Json::UInt64)data.tAccessed.toTime_t() * (Json::UInt64)1000;
    doc["url"] = data.strURL.toStdString();
    doc["styleGuid"] = data.strStyleGUID.toStdString();
    doc["seo"] = data.strSEO.toStdString();
    doc["author"] = data.strAuthor.toStdString();
    doc["keywords"] = data.strKeywords.toStdString();
    doc["tags"] = tags.toStdString();
    doc["withData"] = withData;
    //
    std::vector<WIZZIPENTRYDATA> allLocalResources;
    WizUnzipFile zip;
    // 如果有数据且笔记不是受保护的
    if (withData && !data.nProtected)
    {
        // 打开压缩数据
        if (!zip.open(data.arrayData))
        {
            m_strLastLocalError = "WizErrorInvalidZip";
            TOLOG(QString("Can't open document data!"));
            qDebug() << "Can't open document data";
            return false;
        }
        // 读取主要的HTML和资源文件
        QString html;
        if (!zip.readMainHtmlAndResources(html, allLocalResources))
        {
            m_strLastLocalError = "WizErrorInvalidZip";
            TOLOG(QString("Can't load html and resources!"));
            qDebug() << "Can't load html and resources";
            return false;
        }
        // 将HTML写入JSON
        doc["html"] = html.toStdString();
        // 将资源文件信息写入JSON
        Json::Value res(Json::arrayValue);
        for (auto data : allLocalResources)
        {
            Json::Value elemObj;
            elemObj["name"] = data.name.toStdString();
            elemObj["time"] = (Json::UInt64)data.time.toTime_t() * (Json::UInt64)1000;
            elemObj["size"] = (Json::UInt64)data.size;
            res.append(elemObj);
        }
        //
        doc["resources"] = res;
    }

    // 服务端返回值
    Json::Value ret;
    WIZSTANDARDRESULT jsonRet = WizRequest::execStandardJsonRequest(url_main, "POST", doc, ret);
    m_lastJsonResult = jsonRet;
    if (!jsonRet)
    {
        setLastError(jsonRet);
        qDebug() << "Failed to upload note";
        return false;
    }
    //
    long long newVersion = -1;
    // 建立连接后上传资源文件
    if (withData)
    {
        QString key = QString::fromUtf8(ret["key"].asString().c_str());

        if (data.nProtected)
        {// 如果笔记是受保护的
            Json::Value res;
            if (!uploadObject(*this, url_res, key, m_userInfo.strKbGUID, data.strGUID, "document", data.strGUID, data.arrayData, true, res))
            {
                qDebug() << "Failed to upload note res";
                return false;
            }
            newVersion = res["version"].asInt64();
        }
        else
        {// 如果笔记不是受保护的
            Json::Value resourcesWaitForUpload = ret["resources"];
            size_t resCount = resourcesWaitForUpload.size();
            //
            if (resCount > 0)
            {
                // 准备资源文件压缩包信息
                std::map<QString, WIZZIPENTRYDATA> localResources;
                for (auto entry : allLocalResources)
                {
                    localResources[entry.name] = entry;
                }
                // 将资源文件按照大小分成两部分
                std::vector<WIZZIPENTRYDATA> resLess300K;
                std::vector<WIZZIPENTRYDATA> resLarge;
                //
                for (int i = 0; i < resCount; i++)
                {
                    QString resName = QString::fromUtf8(resourcesWaitForUpload[i].asString().c_str());
                    WIZZIPENTRYDATA entry = localResources[resName];
                    if (entry.size < 300 * 1024)
                    {
                        resLess300K.push_back(entry);
                    }
                    else
                    {
                        resLarge.push_back(entry);
                    }
                }
                //
                bool hasLarge = !resLarge.empty();
                // 解压并上传小于300K的资源文件
                while (!resLess300K.empty())
                {
                    int size = 0;
                    std::vector<WIZRESOURCEDATA> uploads;
                    while (!resLess300K.empty())
                    {
                        int count = resLess300K.size();
                        WIZZIPENTRYDATA last = resLess300K[count - 1];
                        if (size + last.size > 1024 * 1024)
                            break;
                        //
                        resLess300K.pop_back();
                        size += last.size;
                        //
                        QByteArray resData;
                        if (!zip.extractFile("index_files/" + last.name, resData))
                        {
                            m_strLastLocalError = "WizErrorInvalidZip";
                            TOLOG(QString("Can't extract resource from zip file!"));
                            qDebug() << "Can't extract resource from zip file";
                            return false;
                        }
                        WIZRESOURCEDATA data;
                        data.name = last.name;
                        data.data = resData;
                        //
                        uploads.push_back(data);
                    }
                    //
                    bool isLast = resLess300K.empty() && !hasLarge;
                    //
                    Json::Value res;
                    if (!uploadResources(*this, url_res, key, m_userInfo.strKbGUID, data.strGUID, uploads, isLast, res))
                    {
                        qDebug() << "Failed to upload note res";
                        return false;
                    }
                    //
                    if (isLast)
                    {
                        newVersion = res["version"].asInt64();
                    }
                }
                // 解压并上传较大的资源文件
                while (!resLarge.empty())
                {
                    int count = resLarge.size();
                    WIZZIPENTRYDATA last = resLarge[count - 1];
                    resLarge.pop_back();
                    //
                    QByteArray resData;
                    if (!zip.extractFile("index_files/" + last.name, resData))
                    {
                        m_strLastLocalError = "WizErrorInvalidZip";
                        qDebug() << "Can't extract resource from zip file";
                        return false;
                    }
                    //
                    bool isLast = resLarge.empty();
                    //
                    Json::Value res;
                    if (!uploadObject(*this, url_res, key, m_userInfo.strKbGUID, data.strGUID, "resource", last.name, resData, isLast, res))
                    {
                        qDebug() << "Failed to upload note res";
                        return false;
                    }
                    //
                    if (isLast)
                    {
                        newVersion = res["version"].asInt64();
                    }
                }
            }
        }
    }
    //
    if (newVersion == -1)
    {
        newVersion = ret["version"].asInt64();
    }
    //
    nServerVersion = newVersion;
    return true;
}
```

### 上传资源文件

体积较小的资源文件：

```C++
bool uploadResources(WizKMDatabaseServer& server, const QString& url, const QString& key, const QString& kbGuid, const QString& docGuid, const std::vector<WIZRESOURCEDATA>& files, bool isLast, Json::Value& res)
{
    QString objType = "resource";
    //
    QHttpMultiPart *multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType);
    //
    QHttpPart keyPart;
    keyPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"key\""));
    keyPart.setBody(key.toUtf8());

    QHttpPart kbGuidPart;
    kbGuidPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"kbGuid\""));
    kbGuidPart.setBody(kbGuid.toUtf8());

    QHttpPart docGuidPart;
    docGuidPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"docGuid\""));
    docGuidPart.setBody(docGuid.toUtf8());

    QHttpPart objTypePart;
    objTypePart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"objType\""));
    objTypePart.setBody(objType.toUtf8());

    QHttpPart isLastPart;
    isLastPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"isLast\""));
    isLastPart.setBody(isLast ? "1" : "0");

    multiPart->append(keyPart);
    multiPart->append(kbGuidPart);
    multiPart->append(docGuidPart);
    multiPart->append(objTypePart);
    multiPart->append(isLastPart);
    //
    for (auto file: files)
    {
        QHttpPart filePart;
        QString filePartHeader = QString("form-data; name=\"data\"; filename=\"%1\"").arg(file.name);
        filePart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant(filePartHeader));
        filePart.setBody(file.data);
        multiPart->append(filePart);
    }
    //
    QNetworkRequest request(url);

    QNetworkAccessManager networkManager;
    QNetworkReply* reply = networkManager.post(request, multiPart);
    multiPart->setParent(reply); // delete the multiPart with the reply
    //
    WizAutoTimeOutEventLoop loop(reply);
    loop.setTimeoutWaitSeconds(60 * 60);
    loop.exec();
    //
    QNetworkReply::NetworkError err = loop.error();
    if (err != QNetworkReply::NoError)
    {
        TOLOG2("Failed to exec json request, network error=%1, message=%2", WizIntToStr(err), loop.errorString());
        return false;
    }
    //
    QByteArray resData = loop.result();
    //
    WIZSTANDARDRESULT ret = WizRequest::isSucceededStandardJsonRequest(resData);
    if (!ret)
    {
        server.setLastError(ret);
        //
        qDebug() << ret.returnMessage;
        return false;
    }
    //
    return true;
}
```

体积较大的资源文件：

```C++
bool uploadObject(WizKMDatabaseServer& server, const QString& url, const QString& key, const QString& kbGuid, const QString& docGuid, const QString& objType, const QString& objId, const QByteArray& data, bool isLast, Json::Value& res)
{
    // 将数据分割成1M的块
    int partSize = 1024 * 1024; //1M
    int partCount = (data.length() + partSize - 1) / partSize;
    for (int i = 0; i < partCount; i++)
    {
        QHttpMultiPart *multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType);
        //
        QHttpPart keyPart;
        keyPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"key\""));
        keyPart.setBody(key.toUtf8());

        QHttpPart kbGuidPart;
        kbGuidPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"kbGuid\""));
        kbGuidPart.setBody(kbGuid.toUtf8());

        QHttpPart docGuidPart;
        docGuidPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"docGuid\""));
        docGuidPart.setBody(docGuid.toUtf8());

        QHttpPart objIdPart;
        objIdPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"objId\""));
        objIdPart.setBody(objId.toUtf8());

        QHttpPart objTypePart;
        objTypePart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"objType\""));
        objTypePart.setBody(objType.toUtf8());

        QHttpPart indexPart;
        indexPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"partIndex\""));
        indexPart.setBody(WizIntToStr(i).toUtf8());

        QHttpPart countPart;
        countPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"partCount\""));
        countPart.setBody(WizIntToStr(partCount).toUtf8());

        QHttpPart isLastPart;
        isLastPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data; name=\"isLast\""));
        isLastPart.setBody(isLast ? "1" : "0");

        QHttpPart filePart;
        QString filePartHeader = QString("form-data; name=\"data\"; filename=\"%1\"").arg(objId);
        filePart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant(filePartHeader));
        //
        int extra = 0;
        int partEnd = i * partSize + partSize;
        if (partEnd > data.length()) {
            extra = partEnd - data.length();
        }
        QByteArray partData = data.mid(i * partSize, partSize - extra);
        filePart.setBody(partData);
        // 组装HTTP请求
        multiPart->append(keyPart);
        multiPart->append(kbGuidPart);
        multiPart->append(docGuidPart);
        multiPart->append(objIdPart);
        multiPart->append(objTypePart);
        multiPart->append(indexPart);
        multiPart->append(countPart);
        multiPart->append(isLastPart);
        multiPart->append(filePart);
        //
        QNetworkRequest request(url);
        // 建立链接并上传
        QNetworkAccessManager networkManager;
        QNetworkReply* reply = networkManager.post(request, multiPart);
        multiPart->setParent(reply); // delete the multiPart with the reply
        //
        WizAutoTimeOutEventLoop loop(reply);
        loop.setTimeoutWaitSeconds(60 * 60);
        loop.exec();
        // 检查错误
        QNetworkReply::NetworkError err = loop.error();
        if (err != QNetworkReply::NoError)
        {
            TOLOG2("Failed to exec json request, network error=%1, message=%2", WizIntToStr(err), loop.errorString());
            return false;
        }
        //
        QByteArray resData = loop.result();
        //
        try {
            Json::Value partRes;
            WIZSTANDARDRESULT ret = WizRequest::isSucceededStandardJsonRequest(resData, partRes);
            if (!ret)
            {
                server.setLastError(ret);
                qDebug() << "Can't upload note data, ret code=" << ret.returnCode << ", message=" << ret.returnMessage;
                return false;
            }
            //
            if (i == partCount - 1)
            {
                res = partRes;
                return true;
            }
            //
            continue;
        }
        catch (std::exception& err)
        {
            qDebug() << "josn error: " << err.what();
            return false;
        }
    }
    //
    qDebug() << "Should not come here";
    return false;
}
```

### 上传附件

```C++
bool WizKMDatabaseServer::attachment_postDataNew(WIZDOCUMENTATTACHMENTDATAEX& data, bool withData, __int64& nServerVersion)
{
    QString url_main = buildUrl("/ks/attachment/upload/" + m_userInfo.strKbGUID + "/" + data.strDocumentGUID + "/" + data.strGUID);
    QString url_data = buildUrl("/ks/object/upload/" + m_userInfo.strKbGUID + "/" + data.strDocumentGUID);
    //
    Json::Value att;
    att["kbGuid"] = m_userInfo.strKbGUID.toStdString();
    att["docGuid"] = data.strDocumentGUID.toStdString();
    att["attGuid"] = data.strGUID.toStdString();
    att["dataMd5"] = data.strDataMD5.toStdString();
    att["dataModified"] = (Json::UInt64)data.tDataModified.toTime_t() * (Json::UInt64)1000;
    att["name"] = data.strName.toStdString();
    att["url"] = data.strURL.toStdString();
    att["withData"] = withData;
    //
    if (withData)
    {
        att["dataSize"] = data.arrayData.size();
    }
    //
    Json::Value ret;
    WIZSTANDARDRESULT jsonRet = WizRequest::execStandardJsonRequest(url_main, "POST", att, ret);
    if (!jsonRet)
    {
        setLastError(jsonRet);
        qDebug() << "Failed to upload note";
        return false;
    }
    //
    long long newVersion = -1;
    //
    if (withData)
    {
        QString key = QString::fromUtf8(ret["key"].asString().c_str());
        Json::Value res;
        if (!uploadObject(*this, url_data, key, m_userInfo.strKbGUID, data.strDocumentGUID, "attachment", data.strGUID, data.arrayData, true, res))
        {
            qDebug() << "Failed to upload attachment data";
            return false;
        }
        newVersion = res["version"].asInt64();
    }
    //
    if (newVersion == -1)
    {
        newVersion = ret["version"].asInt64();
    }
    //
    nServerVersion = newVersion;
    return true;
}
```