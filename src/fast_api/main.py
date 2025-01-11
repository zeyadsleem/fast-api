import logging
import os
import ssl

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


class BMIOutput(BaseModel):
    bmi: float
    message: str


def sanitize_input(value: str) -> str:
    sanitized = value.replace("<", "").replace(">", "").replace("&", "")
    return sanitized


@app.get("/", response_class=HTMLResponse)
@limiter.limit("10/minute")
def home(request: Request):
    try:
        file_path = os.path.join(os.path.dirname(__file__), "index.html")
        if not os.path.exists(file_path):
            logger.error(f"الملف غير موجود: {file_path}")
            raise HTTPException(status_code=404, detail="الملف غير موجود")
        return FileResponse(file_path)
    except Exception as e:
        logger.error(f"حدث خطأ: {e}")
        raise HTTPException(status_code=500, detail="حدث خطأ داخلي")


@app.get("/calculate_bmi")
@limiter.limit("5/minute")
def calculate_bmi(
    request: Request,
    weight: float = Query(..., gt=20, lt=200, description="الوزن بالكيولوغرام"),
    height: float = Query(..., gt=1, lt=3, description="الطول بالمتر"),
):
    try:
        weight = float(sanitize_input(str(weight)))
        height = float(sanitize_input(str(height)))

        bmi = weight / (height**2)

        if bmi < 18.5:
            message = "لديك نقص فى الوزن, كل أكثر"
        elif 18.5 <= bmi < 25:
            message = "لديك وزن طبيعى, حافظ عليه"
        elif 25 <= bmi < 30:
            message = "لديك وزن متوسط, ظبط أكلك"
        else:
            message = "لديك زيادة فى الوزن, قم بعمل خطة والتزم بها"

        return BMIOutput(bmi=bmi, message=message)
    except ValueError as e:
        logger.error(f"قيم غير صالحة: {e}")
        raise HTTPException(status_code=400, detail="قيم غير صالحة")
    except Exception as e:
        logger.error(f"حدث خطأ: {e}")
        raise HTTPException(status_code=500, detail="حدث خطأ داخلي")


if __name__ == "__main__":
    import uvicorn

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="path/to/cert.pem", keyfile="path/to/key.pem")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
    )
