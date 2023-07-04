from fastapi import FastAPI, Body, Path, Query, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from config import settings
import db

app = FastAPI()
app.title = "Store API"
app.version = "0.1.0"

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET'],
    allow_headers=[],
)

products = db.data

class JWTBearer(HTTPBearer):
	async def __call__(self, request:Request):
		auth = await super().__call__(request)
		data = validate_token(auth.credentials)
		if data['email'] != settings.user_email:
			raise HTTPException(status_code=403, detail="Invalid credentials")

class Product(BaseModel):
	id: Optional[int] = None
	title: str = Field(min_length=5, max_length=25)
	price: int = Field(default=0, ge=0, le=5000)
	description: str = Field(min_length=5, max_length=100)
	category: str= Field(min_length=5, max_length=25)
	image: str=Field(min_length=5, max_length=50)

	class Config:
		schema_extra = {
			"example": {
				"id": 1,
				"title": "Strawberry mochi",
				"price" : 150,
				"description": "Mochi filled with strawberry cream",
				"category": "Fruits",
				"image": "/images/mochi_1.jpeg"
			}
		}

class User(BaseModel):
	email: str = Field(min_length=5, max_length=50)
	password: str = Field(min_length=5, max_length=15)

@app.get('/', tags=['home'])
def message():
	return HTMLResponse('<h2>Welcome to the Mochi Store API!</h2>')

@app.post('/login', tags=['auth'])
def login(user: User):
	if user.email == settings.user_email and user.password == settings.user_password:
		token: str = create_token(user.dict())
		return JSONResponse(status_code=200, content=token)

@app.get('/products', tags=['products'], response_model=List[Product], status_code=200)
def get_products() -> List[Product]:
	return JSONResponse(status_code=200, content=products)

@app.get('/products/{id}', tags=['products'], response_model=Product)
def get_product(id: int = Path(ge=1)) -> Product:
	for item in products:
		if item["id"] == id:
			return JSONResponse(status_code=200, content=item)

	return JSONResponse(status_code=404, content=[])

@app.get('/products/', tags=['products'], response_model=List[Product], status_code=200)
def get_products_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Product]:
	products = [ item for item in products if item["category"].lower() == category.lower() ]
	return JSONResponse(status_code=200, content=products)

@app.post('/products', tags=['products'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_product(product: Product) -> dict:
	products.append(product.dict())

	return JSONResponse(status_code=201, content={
		"message" : "Product created succesfully"
	})

@app.put('/products/{id}', tags=['products'], response_model=dict, dependencies=[Depends(JWTBearer())])
def update_product(id: int, product: Product) -> dict:
	for item in products:
		if item["id"] == id:
			item["title"] = product.title
			item["price"] = product.price
			item["description"] = product.description
			item["category"] = product.category
			item["image"] = product.image

			return JSONResponse(status_code=200, content={
				"message" : "Product modified succesfully"
			})

	return JSONResponse(status_code=404, content={
			"message" : "Product not found"
		})

@app.delete('/products/{id}', tags=['products'], response_model=dict, dependencies=[Depends(JWTBearer())])
def delete_product(id: int) -> dict:
	for item in products:
		if item["id"] == id:
			products.remove(item)

			return JSONResponse(status_code=200, content={
				"message" : "Product deleted succesfully"
			})

	return JSONResponse(status_code=404, content={
			"message" : "Product not found"
		})