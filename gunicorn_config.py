bind = '0.0.0.0:8080'  # Dirección y puerto en los que Gunicorn escuchará las solicitudes
workers = 2  # Número de procesos de trabajador
#worker_class = 'gevent'  # Clase de trabajador para manejar solicitudes de manera asíncrona
timeout = 60  # Tiempo de espera para las solicitudes (en segundos)
accesslog = '/Users/diego/gunicorn_access.log'  # Ruta al archivo de registro de accesos
errorlog = '/Users/diego/log_gunicorn_error.log'  # Ruta al archivo de registro de errores