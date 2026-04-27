# -*- coding: utf-8 -*-
import sys, bcrypt
sys.stdout.reconfigure(encoding="utf-8")
h = bcrypt.hashpw("user20260414".encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")
print(h)
