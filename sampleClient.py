# -*- coding: utf-8 -*-

from Core import Client

string = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec placerat neque at ullamcorper convallis. Nullam in rutrum urna. Cras eleifend metus purus, in porttitor nulla semper id. Curabitur lectus ligula."
#string = "Hello"
a = Client("127.0.0.1", 9888)
a.run()