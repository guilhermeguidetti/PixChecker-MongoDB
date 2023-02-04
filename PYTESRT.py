import datetime 
current_time = datetime.datetime.now() 
buscaDia = int(current_time.day)
print(buscaDia)
if(buscaDia < 10):
    lengthDia = 2
print(lengthDia)