---
name: workstation
description: 获取工位基础数据
argument-hint: time=查询时间(非必填) workstationName=工位名称(非必填)
when_to_use:  machine
---

# Workstation Processing Guide

## Overview

指导文件可以帮助你查询时间{time}内工位{workstationName}数据


### 工位查询分页
- current: 当前页码(默认1)
- size: 分页大小(默认15)
```bash
curl ^"{cps_base_url}/blade-cps/workstation/pc-page?current=1^&size=15^&groupId=1^&orderField=^" ^
  -H ^"Accept: application/json, text/plain, */*^" ^
  -H ^"Accept-Language: zh-CN^" ^
  -H ^"Authorization: {cps_authorization}^" ^
  -H ^"Blade-Auth: {cps_blade_token}^" ^
  -H ^"Content-Type: application/json^" ^
  --data-raw ^"^{^\^"keyWord^\^":^\^"^\^",^\^"type^\^":^\^"^\^",^\^"status^\^":^\^"1^\^",^\^"undefined^\^":^\^"^\^",^\^"filter^\^":^[^]^}^" ^
  --insecure
```

