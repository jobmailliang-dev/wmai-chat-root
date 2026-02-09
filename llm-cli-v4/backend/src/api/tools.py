"""工具管理 API"""

import json
import time

from fastapi import APIRouter, Query

from src.api.models import ApiResponse
from src.modules import ToolService, get_injector
from src.modules.base import ValidException
from src.modules.tools.dtos import ToolDto
from src.utils.logging_web import get_request_logger

router = APIRouter(prefix="/api/tools", tags=["tools"])

# 获取 Injector 实例
_injector = get_injector()

# 获取日志器
_logger = get_request_logger("src.api.tools")


@router.get("")
async def get_tools(id: int = Query(default=None, description="Tool ID (optional)")):
    """获取工具列表或单个工具

    - 无 id 参数时返回所有工具列表
    - 有 id 参数时返回单个工具
    """
    service: ToolService = _injector.get(ToolService)
    if id is not None:
        # 获取单个工具
        tool: ToolDto = service.get_one(id)
        return ApiResponse.ok(tool)

    # 获取所有工具
    tools: list[ToolDto] = service.get_list()
    return ApiResponse.ok(tools)


@router.post("")
async def create_tool(request: dict):
    """创建工具"""
    service: ToolService = _injector.get(ToolService)
    data = service.create_one(request)
    _logger.info("[tool_create] id=%s", data.id if data else None)
    return ApiResponse.ok(data)



@router.put("")
async def update_tool(id: int = Query(..., description="Tool ID"), request: dict = None):
    """更新工具"""
    service: ToolService = _injector.get(ToolService)
    data = service.update(id, request or {})
    _logger.info("[tool_update] id=%s", id)
    return ApiResponse.ok(data)



@router.delete("")
async def delete_tool(id: int = Query(..., description="Tool ID")):
    """删除工具"""
    service: ToolService = _injector.get(ToolService)
    success = service.delete_by_id(id)
    return ApiResponse.ok(success)


@router.post("/import")
async def import_tools(request: dict):
    """批量导入工具"""
    service: ToolService = _injector.get(ToolService)
    tools = request.get("tools", [])
    data = service.import_tools(tools)
    return ApiResponse.ok(data)


@router.get("/export")
async def export_tools():
    """导出所有工具"""
    service: ToolService = _injector.get(ToolService)
    tools: list[ToolDto] = service.export_tools()
    return ApiResponse.ok(tools)


@router.get("/inheritable")
async def get_inheritable_tools():
    """获取可继承的工具列表"""
    service: ToolService = _injector.get(ToolService)
    from src.modules.tools.dtos import ToolInheritableDto
    tools: list[ToolInheritableDto] = service.get_inheritable_tools()
    return ApiResponse.ok(tools)


@router.put("/active")
async def toggle_tool_active(
    id: int = Query(..., description="Tool ID"),
    request: dict = None
):
    """切换工具启用状态"""
    service: ToolService = _injector.get(ToolService)
    is_active = request.get("is_active", True) if request else True
    data = service.toggle_active(id, is_active)
    return ApiResponse.ok(data)


@router.post("/execute")
async def execute_tool(
    id: int = Query(..., description="Tool ID"),
    request: dict = None
):
    """执行工具"""
    from src.tools.registry import get_registry

    params = request.get("params", {}) if request else {}

    # 获取工具
    service: ToolService = _injector.get(ToolService)
    tool_data: ToolDto = service.get_one(id)
    if not tool_data:
        raise ValidException("tool is not found")

    # 检查是否启用
    if not tool_data.is_active:
        raise ValidException("tool is not active")

    # 执行工具
    registry = get_registry()
    start_time = time.time()

    result = registry.execute(tool_data.name, **params)

    # 解析结果
    try:
        result_data = json.loads(result)
        return ApiResponse.ok({
                "result": result_data.get("result", result),
                "execution_time": f"{(time.time() - start_time):.3f}s"
            })
    except (json.JSONDecodeError, TypeError):
        return ApiResponse(
            success=True,
            data={
                "result": result,
                "execution_time": f"{(time.time() - start_time):.3f}s"
            }
        )
