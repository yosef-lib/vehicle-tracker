import re

with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('templates.TemplateResponse("index.html", {', 'templates.TemplateResponse(request=request, name="index.html", context={')
code = code.replace('templates.TemplateResponse("vehicles.html", {', 'templates.TemplateResponse(request=request, name="vehicles.html", context={')
code = code.replace('templates.TemplateResponse("fuel.html", {', 'templates.TemplateResponse(request=request, name="fuel.html", context={')
code = code.replace('templates.TemplateResponse("maintenance.html", {', 'templates.TemplateResponse(request=request, name="maintenance.html", context={')
code = code.replace('templates.TemplateResponse("tax.html", {', 'templates.TemplateResponse(request=request, name="tax.html", context={')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)
