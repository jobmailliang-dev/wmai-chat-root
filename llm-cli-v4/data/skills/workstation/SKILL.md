---
name: workstation
description: 获取工位相关基础信息
argument-hint: time=查询时间 workstationName=工位名称
when_to_use:  machine
---

# Workstation Processing Guide

## Overview

指导文件可以帮助你在时间{time}内查询工位{workstationName}数据


### 工位查询分页
```bash
curl "http://192.168.3.100/api/blade-cps/workstation/pc-page?current=2&size=15&groupId=1&orderField=" ^
-H "Accept: application/json, text/plain, */*" ^
-H "Accept-Encoding: gzip, deflate" ^
-H "Accept-Language: zh-CN" ^
-H "Authorization: Basic c2FiZXI6c2FiZXJfc2VjcmV0" --insecure
```
