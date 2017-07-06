from django.shortcuts import render 

def handle404(req):
    resp = render(req,'404.html')
    resp.status_code = 404
    return resp