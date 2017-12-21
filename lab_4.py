def serialize_form(form):
    import bs4.element
    def _add(name, value):
        if name in data:
            if not isinstance(data, list):
    
                data[name] = [data[name]]
            data[name].append(value)
        else:
            data[name] = value
    assert isinstance(form, bs4.element.Tag) and form.name == 'form'
    
    tags = ['input', 'textarea', 'select', 'button']
    
    
    elements = form.findAll(tags, dict(name=True, disabled=False))
    data = {}
    
    for element in elements:
        tag = element.name
        name = element['name']
        if tag == 'input':
            # если имя переменной совпадает с ключевым словом либо названием
           
            type_ = element.get('type').lower()
            if type_ == 'file':
                continue
            if type_ == 'checkbox' or type_ == 'radio':
                if element.has_attr('checked'):
                   
                    _add(name, element.get('value', 'on'))
            else:
                _add(name, element.get('value', ''))
        elif tag == 'textarea':
            _add(name, element.text)
        elif tag == 'select':
            if element.has_attr('multiple'):
                selected = element.findAll('option', selected=True)
                for option in selected:
                    
                    _add(name, option.get('value', option.text))
                else:
                    
                    _add(name, '')
            else:
                selected = element.find('option', selected=True)
                value = selected.get('value', selected.text)\
                        if selected else ''
                _add(name, value)
        elif tag == 'button':
            
            _add(name, element.get('value', element.text))
    return data

import requests
from bs4 import BeautifulSoup
from utils import serialize_form
r = requests.get('http://domain.tld/path/to/form')
soup = BeautifulSoup(r.text)
form = soup.find('form')
data = serialize_form(form)
print(data)