from dotenv import dotenv_values
config = dotenv_values(".env")

#Flower configuration
port =5555
max_tasks = 10000
auto_refresh = True
# db ='flower.db' #SQLite database file
basic_auth=[f'admin:{config.get("CELERY_FLOWER_PASSWORD","")}']