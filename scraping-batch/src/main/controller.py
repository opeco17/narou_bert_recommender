import json
import os
import requests

from flask import jsonify, request, Response

from run import app
from models.scraper import Scraper


@app.route('/')
def index():
    app.logger.info('Scraping Batch: index called.')
    response_body = {"message": "ScrapingApi!"}
    response = Response(
        response=json.dumps(response_body), 
        mimetype='application/json',
        status= 200
    )
    return response


@app.route('/scraping_and_add', methods=['POST'])
def scraping_and_add():
    """スクレイピングを行い、得られたデータを処理してDBとElasticsearchへ登録するバッチ処理"""
    app.logger.info('Scraping Batch: scraping_and_add called.')
    response_body = {"success": False}
    status_code = 500

    if (host := os.environ.get('HOST')) == None:
        host = 'local'

    if isinstance(test:=request.get_json().get('test'), bool) and (mode:=request.get_json().get('mode')) in ['first', 'middle']:
        if test == False or (test == True and isinstance(epoch:=request.get_json().get('epoch'), int) and epoch > 0):
            if test == False:
                epoch = None
            app.logger.info(f'test: {test}  mode: {mode}  epoch: {epoch}')
            scraper = Scraper()
            scraper.scraping_and_add(test=test, mode=mode, epoch=epoch)
            response_body['success'] = True
            message = f"{scraper.db_count} and {scraper.es_count} data were registeres to DB and ES respectively."
            status_code = 200
        else:
            message = "When test is True, epoch should be a natural number."
    else:
        message = "Please specify test(bool) and mode(first or middle)."
        
    app.logger.info(message)
    response_body["message"] = message

    response = Response(
        response=json.dumps(response_body),
        mimetype='application/json',
        status=status_code
    )
    return response
        

@app.route('/add_existing_data', methods=['POST'])
def add_existing_data():
    """既存のデータを処理してDBとElasticsearchへ登録するバッチ処理"""
    app.logger.info('Scraping Batch: add_existing_data called.')
    response_body = {"success": False}
    status_code = 500

    if (host := os.environ.get('HOST')) == None:
        host = 'local'
    
    if isinstance(test:=request.get_json().get('test'), bool):
        if test == False or (test == True and isinstance(epoch:=request.get_json().get('epoch'), int) and epoch > 0):
            if test == False:
                epoch = None
            app.logger.info(f'test: {test}  epoch: {epoch}')
            scraper = Scraper()
            scraper.add_existing_data(test=test, epoch=epoch)
            response_body['success'] = True
            message = f"{scraper.db_count} and {scraper.es_count} data were registeres to DB and ES respectively."
            status_code = 200
        else:
            message = "When test is True, epoch should be a natural number."
    else:
        message = "Please specify test(bool)."

    app.logger.info(message)
    response_body["message"] = message

    response = Response(
        response=json.dumps(response_body),
        mimetype='application/json',
        status=status_code
    )
    return response

