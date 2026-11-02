-- PRIMERA PARTE

-- 1. Obtén los clientes de brasil
SELECT * FROM customers WHERE Country = 'Brazil';

-- 2. Obtén los empleados que son agentes de ventas
SELECT * FROM employees WHERE Title = 'Sales Support Agent';

-- 3. Obtén las canciones de 'AC/DC'
SELECT tracks.* FROM tracks 
JOIN albums ON tracks.AlbumId = albums.AlbumId 
JOIN artists ON albums.ArtistId = artists.ArtistId 
WHERE artists.Name = 'AC/DC';

-- 4. Obtén los campos de los clientes que no sean de USA: Nombre completo, ID, País
SELECT FirstName || ' ' || LastName AS NombreCompleto, CustomerId, Country FROM customers WHERE Country != 'USA';

-- 5. Obtén los empleados que son agentes de ventas: Nombre completo, Dirección (Ciudad, Estado, País) y email
SELECT FirstName || ' ' || LastName AS NombreCompleto, City, State, Country, Email FROM employees WHERE Title = 'Sales Support Agent';

-- 6. Obtén una lista con los países no repetidos a los que se han emitido facturas
SELECT DISTINCT BillingCountry FROM invoices;

-- 7. Obtén una lista con los estados de USA no repetidos de donde son los clientes y cuántos clientes en cada uno.
SELECT State, COUNT(*) FROM customers WHERE Country = 'USA' GROUP BY State;

-- 8. Cuántos artículos tiene la factura 37
SELECT COUNT(*) FROM invoice_items WHERE InvoiceId = 37;

-- 9. Cuántas canciones tiene 'AC/DC'
SELECT COUNT(*) FROM tracks 
JOIN albums ON tracks.AlbumId = albums.AlbumId 
JOIN artists ON albums.ArtistId = artists.ArtistId 
WHERE artists.Name = 'AC/DC';

-- 10. Cuántos artículos tiene cada factura
SELECT InvoiceId, COUNT(*) FROM invoice_items GROUP BY InvoiceId;

-- 11. Cuántas facturas hay de cada país
SELECT BillingCountry, COUNT(*) FROM invoices GROUP BY BillingCountry;

-- 12. Cuántas facturas ha habido en 2009 y 2011
SELECT COUNT(*) FROM invoices WHERE strftime('%Y', InvoiceDate) = '2009' OR strftime('%Y', InvoiceDate) = '2011';

-- 13. Cuántas facturas ha habido entre 2009 y 2011
SELECT COUNT(*) FROM invoices WHERE strftime('%Y', InvoiceDate) BETWEEN '2009' AND '2011';

-- 14. Cuántas clientes hay de España y de Brasil
SELECT Country, COUNT(*) FROM customers WHERE Country IN ('Spain', 'Brazil') GROUP BY Country;

-- 15. Obtén las canciones que su título empieza por 'You'
SELECT * FROM tracks WHERE Name LIKE 'You%';


-- SEGUNDA PARTE

-- 1. Facturas de Clientes de Brasil, Nombre del cliente, Id de factura, fecha de la factura y el país de la factura
SELECT c.FirstName || ' ' || c.LastName AS NombreCliente, i.InvoiceId, i.InvoiceDate, i.BillingCountry 
FROM invoices i 
JOIN customers c ON i.CustomerId = c.CustomerId 
WHERE c.Country = 'Brazil';

-- 2. Obtén cada factura asociada a cada agente de ventas con su nombre completo
SELECT i.*, e.FirstName || ' ' || e.LastName AS NombreAgente 
FROM invoices i 
JOIN customers c ON i.CustomerId = c.CustomerId 
JOIN employees e ON c.SupportRepId = e.EmployeeId;

-- 3. Obtén el nombre del cliente, el país, el nombre del agente y el total
SELECT c.FirstName || ' ' || c.LastName AS NombreCliente, c.Country, e.FirstName || ' ' || e.LastName AS NombreAgente, i.Total 
FROM invoices i 
JOIN customers c ON i.CustomerId = c.CustomerId 
JOIN employees e ON c.SupportRepId = e.EmployeeId;

-- 4. Obtén cada artículo de la factura con el nombre de la canción
SELECT ii.*, t.Name AS NombreCancion 
FROM invoice_items ii 
JOIN tracks t ON ii.TrackId = t.TrackId;

-- 5. Muestra todas las canciones con su nombre, formato, álbum y género
SELECT t.Name AS NombreCancion, m.Name AS Formato, al.Title AS Album, g.Name AS Genero 
FROM tracks t 
JOIN media_types m ON t.MediaTypeId = m.MediaTypeId 
JOIN albums al ON t.AlbumId = al.AlbumId 
JOIN genres g ON t.GenreId = g.GenreId;

-- 6. Cuántas canciones hay en cada playlist
SELECT p.PlaylistId, p.Name, COUNT(pt.TrackId) AS TotalCanciones 
FROM playlists p 
LEFT JOIN playlist_track pt ON p.PlaylistId = pt.PlaylistId 
GROUP BY p.PlaylistId, p.Name;

-- 7. Cuánto ha vendido cada empleado
SELECT e.EmployeeId, e.FirstName || ' ' || e.LastName AS NombreEmpleado, SUM(i.Total) AS TotalVentas 
FROM employees e 
JOIN customers c ON e.EmployeeId = c.SupportRepId 
JOIN invoices i ON c.CustomerId = i.CustomerId 
GROUP BY e.EmployeeId;

-- 8. ¿Quién ha sido el agente de ventas que más ha vendido en 2009?
SELECT e.FirstName || ' ' || e.LastName AS NombreAgente, SUM(i.Total) AS TotalVentas 
FROM employees e 
JOIN customers c ON e.EmployeeId = c.SupportRepId 
JOIN invoices i ON c.CustomerId = i.CustomerId 
WHERE strftime('%Y', i.InvoiceDate) = '2009' 
GROUP BY e.EmployeeId 
ORDER BY TotalVentas DESC 
LIMIT 1;

-- 9. ¿Cuáles son los 3 grupos que más han vendido?
SELECT ar.Name AS Artista, SUM(ii.UnitPrice * ii.Quantity) AS TotalVendido 
FROM artists ar 
JOIN albums al ON ar.ArtistId = al.ArtistId 
JOIN tracks t ON al.AlbumId = t.AlbumId 
JOIN invoice_items ii ON t.TrackId = ii.TrackId 
GROUP BY ar.ArtistId 
ORDER BY TotalVendido DESC 
LIMIT 3;
