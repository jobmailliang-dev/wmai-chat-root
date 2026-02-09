"""通用 API 响应模型"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """通用 API 响应模型

    Attributes:
        success: 是否成功
        message: 提示信息
        data: 响应数据
        error: 错误信息
    """
    success: bool = Field(default=False, description="是否成功")
    message: Optional[str] = Field(default=None, description="提示信息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")


    @staticmethod
    def ok(data: Optional[any]):
        return ApiResponse( success = True,  data = data)

    @staticmethod
    def fail( message: Optional[str] ):
        return ApiResponse(message=message)


    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": {"id": 1, "name": "test"},
                "error": None
            }
        }
