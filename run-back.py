# -*- coding: utf-8 -*-

from backend.route import api

if __name__=='__main__':
    api.run(host='0.0.0.0',port=81,debug=True)