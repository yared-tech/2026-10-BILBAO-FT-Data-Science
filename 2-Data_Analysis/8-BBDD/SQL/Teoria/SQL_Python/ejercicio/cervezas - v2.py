
import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE CERVEZAS (
    CodC TEXT PRIMARY KEY,
    Envase TEXT,
    Capacidad REAL,
    Stock INTEGER
);

CREATE TABLE BARES (
    CodB TEXT PRIMARY KEY,
    Cif TEXT,
    Nombre TEXT,
    Localidad TEXT
);

CREATE TABLE EMPLEADOS (
    CodE INTEGER PRIMARY KEY,
    Nombre TEXT,
    Sueldo REAL
);

CREATE TABLE REPARTO (
    CodE INTEGER,
    CodB TEXT,
    CodC TEXT,
    Fecha TEXT,
    Cantidad INTEGER,
    FOREIGN KEY(CodE) REFERENCES EMPLEADOS(CodE),
    FOREIGN KEY(CodB) REFERENCES BARES(CodB),
    FOREIGN KEY(CodC) REFERENCES CERVEZAS(CodC)
);

INSERT INTO CERVEZAS VALUES ('01', 'Botella', 0.2, 3600);
INSERT INTO CERVEZAS VALUES ('02', 'Botella', 0.33, 1200);
INSERT INTO CERVEZAS VALUES ('03', 'Lata', 0.33, 2400);
INSERT INTO CERVEZAS VALUES ('04', 'Botella', 1, 288);
INSERT INTO CERVEZAS VALUES ('05', 'Barril', 60, 30);

INSERT INTO BARES VALUES ('001', '11111111X', 'Stop', 'Villa Botijo');
INSERT INTO BARES VALUES ('002', '22222222Y', 'Las Vegas', 'Villa Botijo');
INSERT INTO BARES VALUES ('003', '-', 'Club Social', 'Las Ranas');
INSERT INTO BARES VALUES ('004', '33333333Z', 'Otra Ronda', 'La Esponja');

INSERT INTO EMPLEADOS VALUES (1, 'Prudencio Caminero', 120000);
INSERT INTO EMPLEADOS VALUES (2, 'Vicente Merario', 110000);
INSERT INTO EMPLEADOS VALUES (3, 'Valentin Siempre', 100000);

INSERT INTO REPARTO VALUES (1, '001', '01', '10/21/05', 240);
INSERT INTO REPARTO VALUES (1, '001', '02', '10/21/05', 48);
INSERT INTO REPARTO VALUES (1, '002', '03', '10/22/05', 60);
INSERT INTO REPARTO VALUES (1, '004', '05', '10/22/05', 4);
INSERT INTO REPARTO VALUES (2, '002', '03', '10/22/05', 48);
INSERT INTO REPARTO VALUES (2, '002', '05', '10/23/05', 2);
INSERT INTO REPARTO VALUES (2, '004', '01', '10/23/05', 480);
INSERT INTO REPARTO VALUES (2, '004', '02', '10/24/05', 72);
INSERT INTO REPARTO VALUES (3, '003', '03', '10/24/05', 48);
INSERT INTO REPARTO VALUES (3, '003', '04', '10/25/05', 20);
""")

queries = [
    ("# 1. Obtener el nombre de los empleados que hayan repartido al bar Stop durante la semana del 17 al 23 de octubre de 2005.",
     "SELECT DISTINCT E.Nombre FROM EMPLEADOS E JOIN REPARTO R ON E.CodE = R.CodE JOIN BARES B ON R.CodB = B.CodB WHERE B.Nombre = 'Stop' AND R.Fecha BETWEEN '10/17/05' AND '10/23/05'"),
    
    ("# 2. Obtener el Cif y nombre de los bares a los que se ha repartido cerveza de tipo Botella y capacidad inferior a 1 litro, ordenados por localidad.",
     "SELECT DISTINCT B.Cif, B.Nombre FROM BARES B JOIN REPARTO R ON B.CodB = R.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE C.Envase = 'Botella' AND C.Capacidad < 1 ORDER BY B.Localidad"),
    
    ("# 3. Obtener los repartos (nombre del bar, envase y capacidad de la bebida, fecha y cantidad) realizados por Prudencio Caminero.",
     "SELECT B.Nombre, C.Envase, C.Capacidad, R.Fecha, R.Cantidad FROM REPARTO R JOIN EMPLEADOS E ON R.CodE = E.CodE JOIN BARES B ON R.CodB = B.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE E.Nombre = 'Prudencio Caminero'"),
    
    ("# 4. Obtener los bares a los que se les ha repartido envases de tipo botella y capacidad 0.2 ó 0.33.",
     "SELECT DISTINCT B.* FROM BARES B JOIN REPARTO R ON B.CodB = R.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE C.Envase = 'Botella' AND C.Capacidad IN (0.2, 0.33)"),
    
    ("# 5. Nombre de los empleados que han repartido a los bares \"Stop\" y \"Las Vegas\" cervezas con envase botella.",
     "SELECT E.Nombre FROM EMPLEADOS E JOIN REPARTO R ON E.CodE = R.CodE JOIN BARES B ON R.CodB = B.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE C.Envase = 'Botella' AND B.Nombre = 'Stop' INTERSECT SELECT E.Nombre FROM EMPLEADOS E JOIN REPARTO R ON E.CodE = R.CodE JOIN BARES B ON R.CodB = B.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE C.Envase = 'Botella' AND B.Nombre = 'Las Vegas'"),
    
    ("# 6. Obtener el nombre y número de viajes que ha realizado cada empleado fuera de Villa Botijo.",
     "SELECT E.Nombre, COUNT(*) AS Viajes FROM EMPLEADOS E JOIN REPARTO R ON E.CodE = R.CodE JOIN BARES B ON R.CodB = B.CodB WHERE B.Localidad != 'Villa Botijo' GROUP BY E.CodE, E.Nombre"),
    
    ("# 7. Obtener el nombre y localidad del bar que más litros de cerveza ha comprado.",
     "SELECT B.Nombre, B.Localidad FROM BARES B JOIN REPARTO R ON B.CodB = R.CodB JOIN CERVEZAS C ON R.CodC = C.CodC GROUP BY B.CodB, B.Nombre, B.Localidad ORDER BY SUM(R.Cantidad * C.Capacidad) DESC LIMIT 1"),
    
    ("# 8. Obtener los bares que han adquirido todos los tipos de cerveza con envase de botella y capacidad menor que 1 litro.",
     "SELECT B.Nombre FROM BARES B JOIN REPARTO R ON B.CodB = R.CodB JOIN CERVEZAS C ON R.CodC = C.CodC WHERE C.Envase = 'Botella' AND C.Capacidad < 1 GROUP BY B.CodB, B.Nombre HAVING COUNT(DISTINCT C.CodC) = (SELECT COUNT(*) FROM CERVEZAS WHERE Envase = 'Botella' AND Capacidad < 1)"),
    
    ("# 9. Subir un 5% el sueldo del empleado que más días haya trabajado.",
     "UPDATE EMPLEADOS SET Sueldo = Sueldo * 1.05 WHERE CodE = (SELECT CodE FROM REPARTO GROUP BY CodE ORDER BY COUNT(DISTINCT Fecha) DESC LIMIT 1)"),
    
    ("# 10. Insertar un nuevo reparto del empleado \"Vicente Merario\" al bar \"Stop\" de 48 cervezas de tipo lata el día 10/26/05.",
     "INSERT INTO REPARTO (CodE, CodB, CodC, Fecha, Cantidad) SELECT E.CodE, B.CodB, C.CodC, '10/26/05', 48 FROM EMPLEADOS E, BARES B, CERVEZAS C WHERE E.Nombre = 'Vicente Merario' AND B.Nombre = 'Stop' AND C.Envase = 'Lata'")
]

for comment, sql in queries:
    print(comment)
    cursor.execute(sql)
    if sql.strip().upper().startswith("SELECT"):
        for row in cursor.fetchall():
            print(row)
    else:
        conn.commit()
        if sql.strip().upper().startswith("UPDATE"):
            cursor.execute("SELECT Nombre, Sueldo FROM EMPLEADOS")
            for row in cursor.fetchall():
                print(row)
        elif sql.strip().upper().startswith("INSERT"):
            cursor.execute("SELECT * FROM REPARTO WHERE Fecha = '10/26/05'")
            for row in cursor.fetchall():
                print(row)
    print()

conn.close()