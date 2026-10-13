#%%writefile ejercicios_funciones.py

def week_day(dia):

    dias_semana = {1: "Lunes",

               2: "Martes",

               3: "Miércoles",

               4: "Jueves",

               5: "Viernes",

               6: "Sábado",

               7: "Domingo"}

    if dia in dias_semana:

        return dias_semana[dia]

    else:

        return "Día erróneo"
#%%writefile -a ejercicios_funciones.py

def piramide(num_filas):

    for i in range(int(num_filas), 0, -1):

        for j in range(i, 0, -1):

            print(j, end=" ")

        print()

#%%writefile -a ejercicios_funciones.py

def comparaNumeros(num_1, num_2):

    # La lambda debe ejecutarse pasando los argumentos (num_1, num_2) al final

    return (lambda a, b: "Son iguales" if a == b else ("El primero es mayor" if a > b else "El segundo es mayor"))(num_1, num_2)

#%%writefile -a ejercicios_funciones.py

def contador_letras(texto, letra):

    contador = 0

    for letra_i in texto:

        if(letra.lower() == letra_i.lower()):

            contador += 1

    return contador

#%%writefile -a ejercicios_funciones.py

def contador_letras_light(texto, letra):

    return texto.lower().count(letra.lower())

#%%writefile -a ejercicios_funciones.py

def string_2_dic(cadena):

    dic = {}

    for letra in cadena:

        dic[letra] = cadena.lower().count(letra.lower())

    return dic

#%%writefile -a ejercicios_funciones.py

def operar_lista(lista, comando, elemento=None):

    if len(lista) > 0 and elemento != None:

         match comando:

               case "add":

                    lista.append(elemento)

               case "remove":

                    if elemento in lista: lista.remove(elemento)

    print(lista)   

#%%writefile -a ejercicios_funciones.py

def devuelveFrase(*args):

    frase = ""

    lista = []

    for palabra in args:

        lista.append(palabra)

    frase = " ".join(lista)

    return frase

#%%writefile -a ejercicios_funciones.py

def recursiva(n):

    if n <= 1:

        return n

    return recursiva(n-1) + recursiva(n-2)

#%%writefile -a ejercicios_funciones.py

import math

def area_cuadrado(lado):

    return lado * lado

def area_triangulo(base, altura):

    return base * altura / 2

def area_circulo(radio):

    return math.pi * (radio ** 2)
