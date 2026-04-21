from fastapi import FastAPI,status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel


books = [
      {
        "id":1,
        "title": "The alchemist",
        "author": "Paulo coelho",
        "publish_date":"1988-01-01"
      },
      {
        "id":2,
        "title": "The God of small things",
        "author": "Arundhati roy",
         "publish_date":"1997-01-01"
      },
      {
        "id":3,
        "title": "The white tiger",
        "author": "Aravind adiga",
        "publish_date":"2008-01-01"
      },
      {
        "id":4,
        "title": "The palace of illusions",
        "author": "Chitra banerjee divakaruni",
        "publish_date":"2008-020-12"
      }
]

app = FastAPI()
@app.get("/books")
def grt_books ():
    return books

@app.get("/book/{book_id}")
def get_book(id: int):
    for book in books:
        if book["id"] == id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="book not found") 




class book(BaseModel):
    id: int
    title: str
    author: str
    publish_date: str 

@app.post("/books")
def create_book(book: book):
    new_book = books.model_dump()
    books.append(new_book)     

class bookupdate(BaseModel):
    title: str
    author: str
    publish_date: str 

@app.put("/books/{book_id}")
def update_book(book_id: int, book_update: bookupdate):
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            book["publish_date"] = book_update.publish_date
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="book not found")      

@app.delete("/book/{book_id}")
def delete_book(book_id:int):
    for book in books:
      if book['id'] == book_id:
        books.remove(book)
        return{"message":"our book deleted"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="book not found")



