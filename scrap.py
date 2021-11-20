from flask_sqlalchemy import SQLAlchemy
from flask import Flask , render_template, redirect , url_for
from flask import request
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Register125@localhost/WebScrapping'
db = SQLAlchemy(app)

class Coin(db.Model):
    __tablename__ = 'coins'
    id = db.Column('id',db.Integer,primary_key=True)
    coin = db.Column('coin', db.Unicode)
    news = db.Column('news',db.Unicode)
    summary = db.Column('summary',db.Unicode)

    def __init__(self,coin,news,summary):
        self.coin = coin
        self.news = news
        self.summary = summary


class Scrap:
    def __init__(self):
        print('Loading...')
    
    def pars(self,crypto):

        base_url = 'https://cryptonews.com/'
        r = requests.get('https://cryptonews.com/news/'+crypto+'-news/')
        soup = BeautifulSoup(r.text, 'html.parser')
        for div in soup.find_all("div", {'class':'article__badge article__badge--md mb-10 pt-10'}): 
            div.decompose()
           
        link = soup.find_all('div',class_='col-12 col-md-7 column-45__right d-flex flex-column justify-content-center')

        links = []

        for ssilka in link:
            links.append(ssilka.find('a').attrs['href'])


        news =[]

        for news_url in links:
            html_team = requests.get(base_url+news_url).text
            soup_team = BeautifulSoup(html_team,'html.parser')

            for div1 in soup_team.find_all("div", {'class':'left-side'}): 
                div1.decompose()

            paragraphs = soup_team.find_all('p',limit=3)
            text = [result.text for result in paragraphs]
            ARTICLE = ' '.join(text)

            news.append(ARTICLE)

        return news

    def summary(self,news):
        sumsum = []
        summarizer = pipeline("summarization")
        res = summarizer(news, max_length=120, min_length=30, do_sample=False)
        for r in res:
            sumsum.append(r['summary_text'])
        
        return sumsum
        

    
    
        

@app.route('/coin',methods=["POST","GET"])
def coin():
    if request.method == "POST":
        c = request.form['coin']
        data =Coin.query.filter_by(coin=c).first()
        if data:
            return redirect(url_for('crypto',crypto=c))
        scrap = Scrap()
        n=scrap.pars(c)

        summ=scrap.summary(n)

        coin = Coin(coin=c,news=n,summary=summ)
        db.session.add(coin)
        db.session.commit()
        return redirect(url_for('crypto',crypto=c))

    else:
        return render_template("coin.html")

@app.route('/coin/<crypto>',methods=["POST","GET"])
def crypto(crypto):
    if request.method == "POST":
        c = request.form['coin']
        data =Coin.query.filter_by(coin=c).first()
        
        if data:
            new = str(data.news).replace('"', " ").replace("{"," ").replace("}"," ").replace("\\n",'')
            sumsumsum = str(data.summary).replace('"', " ").replace("{"," ").replace("}"," ")
            s = sumsumsum.split(' , ')
            l = new.split(' , ')
            return render_template("crypto.html",rev=zip(s, l), title = data.coin)
            
        scrap = Scrap()
        n=scrap.pars(c)

        summ=scrap.summary(n)

        coin = Coin(coin=c,news=n,summary=summ)
        db.session.add(coin)
        db.session.commit()
        return redirect(url_for('crypto',crypto=c))
    
    coins = Coin.query.filter_by(coin = crypto).first()
    new = str(coins.news).replace('"', " ").replace("{"," ").replace("}"," ")
    sumsumsum = str(coins.summary).replace('"', " ").replace("{"," ").replace("}"," ")
    s = sumsumsum.split(' , ')
    l = new.split(' , ')
    return render_template("crypto.html",rev=zip(s,l), title = coins.coin)


if __name__ == '__main__':  
    app.run(debug=True)