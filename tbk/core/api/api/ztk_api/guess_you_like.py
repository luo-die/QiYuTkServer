from typing import Optional, List

from fastapi import Depends, Body
from pydantic import BaseModel, Field
from structlog.stdlib import BoundLogger
from ztk_api import ZTK, GuessYouLikeArgs, GuessYouLikeModel

from core.logger import get_logger
from core.resp.base import ResponseModel, ApiResp
from core.shared import AppErrno
from core.vendor.ztk import get_ztk_api_v2
from .. import fields
from ..app import app
from ...api_utils import api_inner_wrapper


class GuessYouLikeResponseModel(ResponseModel):
    data: Optional[List[GuessYouLikeModel]] = Field(None, title="返回数据")


class GuessYouLikeForm(BaseModel):
    """
    猜你喜欢接口请求参数
    """

    page: int = fields.page_field
    page_size: int = fields.page_size_field
    sort: str = fields.sort_fields

    device_value: Optional[str] = Field(
        None, title="设备号", description="设备号加密后的值（MD5加密需32位小写）"
    )
    device_encrypt: Optional[str] = Field(
        None, title="设备类型", description="设备号类型：IMEI，或者IDFA，或者UTDID（UTDID不支持MD5加密）"
    )
    item_id: Optional[str] = Field(
        None,
        title="商品ID",
        description="如果该值非空，那么device_value、device_encrypt和device_type无效，反之，如果这三个值非空，那么商品ID无效",
    )

    def to_data(self) -> GuessYouLikeArgs:
        return GuessYouLikeArgs.from_dict(self.dict())


@app.post(
    "/ztk/guess_you_like",
    tags=["折淘客"],
    summary="猜你喜欢",
    description="使用折淘客 猜你喜欢接口",
    response_model=GuessYouLikeResponseModel,
)
async def guess_you_like(
    g: GuessYouLikeForm = Body(..., title="请求参数"),
    logger: BoundLogger = Depends(get_logger),
    ztk: ZTK = Depends(get_ztk_api_v2),
):
    @api_inner_wrapper(logger)
    async def inner():
        args = g.to_data()
        j = await ztk.guess_you_like(args)
        if j.status == 200:
            return ApiResp.from_data(j.content)
        else:
            return ApiResp.from_errno(AppErrno.ztk_error, str(j.content))

    return await inner
