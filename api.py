from fastapi import FastAPI
import uvicorn
import source_code

app=FastAPI()

@app.get('/')
async def stocks():
    mod=source_code.search_stock()
    lst=[]
    for ticker in mod:
        if(mod[ticker]=='POSITIVE'):
            lst.append(ticker)
    return lst

if __name__=='__main__':
    uvicorn.run(app, host='localhost', port=8005)