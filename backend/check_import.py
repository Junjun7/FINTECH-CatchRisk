import importlib,traceback,sys
try:
    m=importlib.import_module('main')
    print('OK app=', getattr(m,'app',None))
except Exception:
    traceback.print_exc()
    sys.exit(1)
