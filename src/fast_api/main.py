from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class BMIOutput(BaseModel):
    bmi: float
    message: str


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hi():
    return {"message": "Marhaba python"}


@app.get("/calculate_bmi")
def calculate_bmi(
    weight: float = Query(..., gt=20, lt=200, description="الوزن بالكيولوغرام"),
    height: float = Query(..., gt=1, lt=3, description="الطول بالمتر"),
):
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
