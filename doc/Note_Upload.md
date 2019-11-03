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