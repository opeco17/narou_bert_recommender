import json
import re

from flask import flash, redirect, request, render_template
from flask_mail import Message
import requests

from config import Config
from forms import ContactForm, TextUploadForm, URLUploadForm
from model import RecommendItemsGetter
from run import app, mail


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    app.logger.info('Web: index called.')
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about():
    app.logger.info('Web: about called.')
    return render_template('about.html')


@app.route('/search_by_text', methods=['GET', 'POST'])
def search_by_text():
    app.logger.info('Web: search_by_text called.')
    text_upload_form = TextUploadForm()
    
    if request.method == 'GET':
        return render_template('search_by_text.html', form=text_upload_form, success=False)

    is_correct_input = text_upload_form.validate()
    if not is_correct_input:
        flash('小説の本文を入力して下さい。')
        return render_template('search_by_text.html', form=text_upload_form, success=False)

    text = text_upload_form.text.data
    app.logger.info(f"Uploaded text: {text}")
    recommend_items = RecommendItemsGetter.get_recommend_items_by_text(text)
    
    if not recommend_items:
        return render_template('error.html')
    
    app.logger.info(f"Resul is called by text search.")
    return render_template('result.html', recommend_items=recommend_items)

    
@app.route('/search_by_url', methods=['GET', 'POST'])
def search_by_url():
    app.logger.info('Web: search_by_url called.')
    url_upload_form = URLUploadForm()
    
    if request.method == 'GET':
        return render_template('search_by_url.html', form=url_upload_form, success=False)
    
    is_correct_input = url_upload_form.validate()
    is_correct_url = re.fullmatch(r'https://ncode.syosetu.com/[nN].{6}/?', url:=url_upload_form.url.data)
    if (not is_correct_input) or (not is_correct_url):
        flash('小説家になろうの小説URLを入力して下さい。')
        return render_template('search_by_url.html', form=url_upload_form, success=False)
    
    ncode = url[26:33].upper()
    app.logger.info(f"Uploaded ncode: {ncode}")
    recommend_items = RecommendItemsGetter.get_recommend_items_by_ncode(ncode)
    
    if not recommend_items:
        return render_template('error.html')
    
    app.logger.info(f"Resul is called by url search.")
    return render_template('result.html', recommend_items=recommend_items)
            

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    app.logger.info('Web: contact called.')
    contact_form = ContactForm()

    if request.method == 'GET':
        return render_template('contact.html', form=contact_form, success=False)
    
    is_correct_input = contact_form.validate()
    if not is_correct_input:
        flash('全て入力して下さい。')
        return render_template('contact.html', form=contact_form, success=False)
    
    msg = Message(contact_form.subject.data, sender=Config.MAIL_USERNAME, recipients=[contact_form.email.data])
    msg.body = f"Contact Information \n Name: {contact_form.name.data} \n Mail: {contact_form.email.data}  \n Content: {contact_form.message.data}"
    mail.send(msg)
    return render_template('contact.html', success=True)


@app.route('/narou_redirect/<ncode>/<int:rank>', methods=['GET'])
def narou_redirect(ncode, rank):
    app.logger.info('Web: narou_redirect called.')
    url = f"https://ncode.syosetu.com/{ncode}/"
    app.logger.info(f"Rank: {rank}")
    return redirect(url, code=302)
