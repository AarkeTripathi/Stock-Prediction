from flask import Flask, request
import pickle
mod=pickle.load(open('model.pkl','rb'))

app=Flask(__name__)


@app.route('/api', methods=['POST','GET'])
def func():
    lst=[]
    inputchar=int(request.args['query'])
    for ticker in mod:
        if(mod[ticker]=='POSITIVE'):
            lst.append(ticker)
    return lst

if __name__=='__main__':
    app.run()