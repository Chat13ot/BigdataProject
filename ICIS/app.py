import elasticsearch
import json
from flask import Flask, request
from flask import render_template

app = Flask(__name__)
es_client = elasticsearch.Elasticsearch('localhost:9200')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shop-grid')
def shop_grid():
    return render_template('shop-grid.html')


@app.route('/search', methods=['POST'])
def search():
    titles = []
    imgs = []

    search_term = request.form['search']
    doc = es_client.search(index='_all', body={
        "query": {
            "match_phrase": {
                "title": search_term
            }
        }
    }, size=999)

    resultCount = len(doc['hits']['hits'])

    # for i in range(resultCount):
    #     print(json.dumps(doc['hits']['hits'][i]['_source'], ensure_ascii=False, indent=2))

    for i in range(resultCount):
        titles.append(doc['hits']['hits'][i]['_source']['title'])

    for i in range(resultCount):
        imgs.append(doc['hits']['hits'][i]['_source']['img'])

    return render_template('shop-grid.html', titles=titles, imgs=imgs)


if __name__ == '__main__':
    app.run()
