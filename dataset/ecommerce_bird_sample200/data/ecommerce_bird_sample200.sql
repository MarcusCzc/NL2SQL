SELECT COUNT(CustomerID) FROM Customers WHERE City = 'London'	retail_world
SELECT T.l_orderkey FROM ( SELECT T2.l_orderkey, COUNT(T2.l_partkey) AS num FROM part AS T1 INNER JOIN lineitem AS T2 ON T1.p_partkey = T2.l_partkey WHERE T1.p_container = 'JUMBO CASE' GROUP BY T2.l_orderkey ) AS T WHERE T.num > 2	retails
SELECT COUNT(T2.Category) FROM east_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T1.`Ship Mode` = 'Standard Class'	superstore
SELECT MiddleInitial FROM Employees GROUP BY MiddleInitial ORDER BY COUNT(MiddleInitial) DESC LIMIT 1	sales
SELECT DISTINCT T2.`Product Name` FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Region = 'Central' AND T1.Profit < 0	superstore
SELECT east, west FROM ( SELECT COUNT(`Order ID`) AS east , ( SELECT COUNT(`Order ID`) FROM west_superstore WHERE `Order Date` LIKE '2015%' ) AS west FROM east_superstore WHERE `Order Date` LIKE '2015%' )	superstore
SELECT DISTINCT T2.`Customer Name` FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.Quantity = 8 AND T1.Region = 'West'	superstore
SELECT T2.c_name FROM orders AS T1 INNER JOIN customer AS T2 ON T1.o_custkey = T2.c_custkey WHERE T1.o_orderdate = '1997-12-10' AND T1.o_clerk = 'Clerk#000000803'	retails
SELECT COUNT(ProductID) FROM Products WHERE Price = 0	sales
SELECT CAST(SUM(IIF(T3.s_acctbal < ( SELECT AVG(supplier.s_acctbal) FROM supplier ), 1, 0)) AS REAL) * 100 / COUNT(T1.n_nationkey) FROM nation AS T1 INNER JOIN region AS T2 ON T1.n_regionkey = T2.r_regionkey INNER JOIN supplier AS T3 ON T1.n_nationkey = T3.s_nationkey WHERE T2.r_name = 'EUROPE'	retails
SELECT T1.n_name, T3.r_name FROM nation AS T1 INNER JOIN customer AS T2 ON T1.n_nationkey = T2.c_nationkey INNER JOIN region AS T3 ON T1.n_regionkey = T3.r_regionkey WHERE T2.c_address = 'wH55UnX7 VI'	retails
SELECT T1.LastName FROM Employees AS T1 INNER JOIN Sales AS T2 ON T1.EmployeeID = T2.SalesPersonID WHERE T2.SalesID = 100	sales
SELECT T2.CategoryName FROM Products AS T1 INNER JOIN Categories AS T2 ON T1.CategoryID = T2.CategoryID WHERE T1.ProductName = 'Tofu'	retail_world
SELECT DISTINCT T2.Sales / (1 - T2.Discount) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Aimee Bixby' AND T3.`Product Name` = 'Xerox 1952' AND T2.`Order Date` = '2014-09-10'	superstore
SELECT FirstName, LastName FROM Employees WHERE BirthDate = '1955-03-04 00:00:00'	retail_world
SELECT T2.FirstName, T2.LastName FROM Sales AS T1 INNER JOIN Customers AS T2 ON T1.CustomerID = T2.CustomerID WHERE T1.Quantity = 403 AND T1.SalesID BETWEEN 30 AND 40	sales
SELECT COUNT(l_orderkey) FROM lineitem WHERE STRFTIME('%Y', l_shipdate) = '1997' AND l_shipmode = 'MAIL'	retails
SELECT T2.`Product Name` FROM south_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Region = 'South' ORDER BY T1.Sales DESC LIMIT 1	superstore
SELECT COUNT(T2.`Customer ID`) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.`Customer Name` = 'Corey Roper' AND STRFTIME('%Y', T2.`Ship Date`) = '2015'	superstore
SELECT COUNT(T1.s_suppkey) FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T2.n_name = 'GERMANY' AND T1.s_comment LIKE '%carefully regular packages%'	retails
SELECT SUM(T1.ps_availqty) FROM partsupp AS T1 INNER JOIN part AS T2 ON T1.ps_partkey = T2.p_partkey WHERE T2.p_name = 'hot spring dodger dim light'	retails
SELECT COUNT(T2.EmployeeID) FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID WHERE T1.FirstName = 'Margaret' AND T1.LastName = 'Peacock'	retail_world
SELECT AVG(Price) FROM Products WHERE Price BETWEEN 100 AND 200	sales
SELECT T3.r_name FROM nation AS T1 INNER JOIN customer AS T2 ON T1.n_nationkey = T2.c_nationkey INNER JOIN region AS T3 ON T1.n_regionkey = T3.r_regionkey WHERE T2.c_custkey = 106936	retails
SELECT SUM(T2.l_extendedprice * (1 - T2.l_discount) - T1.ps_supplycost * T2.l_quantity) / COUNT(T1.ps_partkey) FROM partsupp AS T1 INNER JOIN lineitem AS T2 ON T1.ps_suppkey = T2.l_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey WHERE T3.p_type = 'PROMO BRUSHED STEEL'	retails
SELECT DISTINCT T3.`Product Name` FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T2.`Customer Name` = 'Alejandro Grove'	superstore
SELECT DISTINCT T1.Name FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE T2.SalesPersonID = 10	sales
SELECT DISTINCT T2.Name FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T1.Quantity < ( SELECT AVG(Quantity) FROM Sales )	sales
SELECT o_orderdate FROM orders WHERE o_orderpriority = '1-URGENT'	retails
SELECT CAST(SUM(IIF(c_acctbal < 0, 1, 0)) AS REAL) * 100 / COUNT(c_custkey) FROM customer	retails
SELECT T2.CategoryName, T2.Description FROM Products AS T1 INNER JOIN Categories AS T2 ON T1.CategoryID = T2.CategoryID WHERE T1.ProductName = 'Mozzarella di Giovanni'	retail_world
SELECT T1.Price FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE T2.CustomerID BETWEEN 1 AND 100 ORDER BY T1.Price DESC LIMIT 1	sales
SELECT s_name FROM supplier ORDER BY s_acctbal DESC LIMIT 3	retails
SELECT COUNT(T2.OrderID) FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID WHERE T1.FirstName = 'Michael' AND T1.LastName = 'Suyama'	retail_world
SELECT DISTINCT T2.Segment FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.Region = 'West' AND T1.`Order ID` = 'CA-2011-108189'	superstore
SELECT COUNT(DISTINCT T1.`Order ID`) FROM east_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T2.`Customer Name` = 'Maxwell Schwartz' AND STRFTIME('%Y', T1.`Order Date`) = '2015'	superstore
SELECT T2.`Product Name` FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Region = 'Central' AND STRFTIME('%Y', T1.`Order Date`) = '2016' ORDER BY T1.Profit ASC LIMIT 1	superstore
SELECT T2.SalesID FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE T1.Name LIKE 'Hex Nut%' AND T1.Price > 100	sales
SELECT ( SELECT Price FROM Products WHERE Name = 'HL Mountain Frame - Black, 42' ) - ( SELECT Price FROM Products WHERE Name = 'LL Mountain Frame - Black, 42' ) AS num	sales
SELECT T2.ps_supplycost FROM part AS T1 INNER JOIN partsupp AS T2 ON T1.p_partkey = T2.ps_partkey WHERE T1.p_type = 'large plated tin'	retails
SELECT COUNT(EmployeeID) FROM Employees	sales
SELECT COUNT(T1.ps_partkey) FROM partsupp AS T1 INNER JOIN lineitem AS T2 ON T1.ps_suppkey = T2.l_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey WHERE T3.p_mfgr = 'Manufacturer#5' AND T3.p_retailprice < 1000 AND T2.l_shipmode = 'RAIL'	retails
SELECT COUNT(CustomerID) FROM Sales GROUP BY SalesPersonID	sales
SELECT COUNT(T2.SalesPersonID) FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE T1.Name = 'ML Road Frame-W - Yellow, 40'	sales
SELECT T2.l_shipdate FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey ORDER BY T1.o_totalprice DESC LIMIT 1	retails
SELECT T2.ps_supplycost FROM part AS T1 INNER JOIN partsupp AS T2 ON T1.p_partkey = T2.ps_partkey WHERE T1.p_name = 'violet olive rose ivory sandy'	retails
SELECT CAST(SUM(IIF(T2.n_name = 'GERMANY', 1, 0)) AS REAL) * 100 / COUNT(T1.s_suppkey) FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T1.s_acctbal < 0	retails
SELECT COUNT(T1.ProductID) FROM Products AS T1 INNER JOIN Categories AS T2 ON T1.CategoryID = T2.CategoryID WHERE T2.CategoryName = 'Dairy Products'	retail_world
SELECT COUNT(City) FROM Customers WHERE Country = 'Germany' AND City = 'Berlin'	retail_world
SELECT (CAST(SUM(IIF(STRFTIME('%Y', T2.l_shipdate) = 1995, 1, 0)) AS REAL) / 12) - (CAST(SUM(IIF(STRFTIME('%Y', T2.l_shipdate) = 1996, 1, 0)) AS REAL) / 12) FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T1.o_orderpriority = '5-LOW' AND T2.l_shipmode = 'TRUCK'	retails
SELECT AVG(T3.o_totalprice) FROM nation AS T1 INNER JOIN customer AS T2 ON T1.n_nationkey = T2.c_nationkey INNER JOIN orders AS T3 ON T2.c_custkey = T3.o_custkey WHERE T1.n_name = 'GERMANY'	retails
SELECT DISTINCT strftime('%J', `Ship Date`) - strftime('%J', `Order Date`) AS duration FROM central_superstore WHERE `Order ID` = 'CA-2011-134103'	superstore
SELECT T1.o_clerk FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T2.l_shipmode = 'MAIL'	retails
SELECT COUNT(*) FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Category = 'Furniture'	superstore
SELECT COUNT(DISTINCT T2.`Order ID`) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.`Customer Name` = 'Aimee Bixby'	superstore
SELECT T1.`Order ID` FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.`Product Name` = 'Logitech G600 MMO Gaming Mouse' GROUP BY T1.`Order ID` ORDER BY SUM((T1.Sales / (1 - T1.Discount)) * T1.Quantity - T1.Profit) DESC LIMIT 1	superstore
SELECT T.n_name FROM ( SELECT T2.n_name, COUNT(T1.c_custkey) AS num FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey GROUP BY T2.n_name ) AS T ORDER BY T.num DESC LIMIT 1	retails
SELECT l_orderkey FROM lineitem ORDER BY l_extendedprice DESC LIMIT 2	retails
SELECT l_extendedprice * (1 - l_discount) FROM lineitem WHERE l_linenumber = 1	retails
SELECT T.r_name FROM ( SELECT T1.r_name, COUNT(T2.n_name) AS num FROM region AS T1 INNER JOIN nation AS T2 ON T1.r_regionkey = T2.n_regionkey GROUP BY T1.r_name ) AS T ORDER BY T.num LIMIT 1	retails
SELECT T3.s_name FROM part AS T1 INNER JOIN partsupp AS T2 ON T1.p_partkey = T2.ps_partkey INNER JOIN supplier AS T3 ON T2.ps_suppkey = T3.s_suppkey WHERE T1.p_name = 'smoke red pale saddle plum'	retails
SELECT c_phone FROM customer WHERE c_name = 'Customer#000000001'	retails
SELECT T3.r_name FROM nation AS T1 INNER JOIN supplier AS T2 ON T1.n_nationkey = T2.s_nationkey INNER JOIN region AS T3 ON T1.n_regionkey = T3.r_regionkey WHERE T2.s_name = 'Supplier#000000129'	retails
SELECT T3.p_name FROM partsupp AS T1 INNER JOIN supplier AS T2 ON T1.ps_suppkey = T2.s_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey WHERE T2.s_name = 'Supplier#000000034'	retails
SELECT SUM(T2.Quantity * T3.Price) FROM Employees AS T1 INNER JOIN Sales AS T2 ON T1.EmployeeID = T2.SalesPersonID INNER JOIN Products AS T3 ON T2.ProductID = T3.ProductID WHERE T1.FirstName = 'Abraham' AND T1.MiddleInitial = 'e' AND T1.LastName = 'Bennet' AND T3.Name = 'Road-650 Red, 60'	sales
SELECT c_phone FROM customer ORDER BY c_acctbal DESC LIMIT 1	retails
SELECT COUNT(c_custkey) FROM customer WHERE c_acctbal < 0 AND c_mktsegment = 'MACHINERY'	retails
SELECT DISTINCT T3.`Product Name` FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Phillina Ober'	superstore
SELECT COUNT(ProductID) FROM Products WHERE Price = 0	sales
SELECT Name FROM Products WHERE Price IN (( SELECT MAX(Price) FROM Products ), ( SELECT MIN(Price) FROM Products ))	sales
SELECT T3.`Product Name` FROM east_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T2.`Customer Name` = 'Jonathan Doherty' AND T2.Region = 'East' ORDER BY T1.Quantity DESC LIMIT 1	superstore
SELECT T3.p_name FROM partsupp AS T1 INNER JOIN lineitem AS T2 ON T1.ps_suppkey = T2.l_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey WHERE T2.l_discount = 0.0000	retails
SELECT T3.FirstName, T3.MiddleInitial, T3.LastName FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID INNER JOIN Customers AS T3 ON T2.CustomerID = T3.CustomerID ORDER BY T2.Quantity * T1.Price DESC LIMIT 1	sales
SELECT T1.FirstName, T1.LastName FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID WHERE T2.OrderID = 10274	retail_world
SELECT COUNT(T1.SalesID) FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T2.Name = 'Flat Washer 8'	sales
SELECT p_brand FROM part WHERE p_type = 'PROMO BRUSHED STEEL'	retails
SELECT SUM(T2.Quantity) FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE SUBSTR(T1.Name, 1, 1) = 'C'	sales
SELECT COUNT(DISTINCT T1.`Order ID`) FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.`Product Name` = 'O''Sullivan Plantations 2-Door Library in Landvery Oak' AND T2.Region = 'Central' AND T1.`Ship Mode` = 'First Class'	superstore
SELECT T1.FirstName FROM Customers AS T1 INNER JOIN Sales AS T2 ON T1.CustomerID = T2.CustomerID WHERE T1.LastName = 'Valdez' ORDER BY T2.Quantity DESC LIMIT 1	sales
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey ORDER BY T1.s_suppkey DESC LIMIT 1	retails
SELECT T1.FirstName, T1.MiddleInitial, T1.LastName FROM Employees AS T1 INNER JOIN Sales AS T2 ON T1.EmployeeID = T2.SalesPersonID GROUP BY T2.SalesPersonID, T1.FirstName, T1.MiddleInitial, T1.LastName ORDER BY COUNT(T2.SalesID) DESC LIMIT 3	sales
SELECT T1.FirstName, T1.LastName FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID WHERE T2.OrderID = 10280	retail_world
SELECT T2.Country FROM Products AS T1 INNER JOIN Suppliers AS T2 ON T1.SupplierID = T2.SupplierID WHERE T1.ProductName = 'Scottish Longbreads'	retail_world
SELECT SUM(T1.Quantity) FROM west_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.`Product Name` = 'Hon Pagoda Stacking Chairs'	superstore
SELECT T1.c_name, T1.c_phone FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_acctbal > ( SELECT AVG(c_acctbal) FROM customer ) ORDER BY T1.c_name	retails
SELECT T2.`Product Name` FROM south_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T1.`Ship Date` = '2013-03-04' AND T2.Region = 'South' AND T1.`Order Date` = '2013-03-04'	superstore
SELECT COUNT(T1.SupplierID) FROM Products AS T1 INNER JOIN Suppliers AS T2 ON T1.SupplierID = T2.SupplierID WHERE T2.Country = 'Japan'	retail_world
SELECT COUNT(T1.l_linenumber) FROM lineitem AS T1 INNER JOIN supplier AS T2 ON T1.l_suppkey = T2.s_suppkey WHERE T1.l_orderkey = 4 AND T2.s_acctbal < 0	retails
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T1.s_suppkey = 34	retails
SELECT AVG(l_linenumber) FROM lineitem WHERE l_shipdate BETWEEN '1994-01-01' AND '1994-01-30'	retails
SELECT DISTINCT T2.`Customer Name` FROM south_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T1.Region = 'South' AND T3.`Product Name` = 'Xerox 23'	superstore
SELECT COUNT(T1.n_nationkey) FROM nation AS T1 INNER JOIN region AS T2 ON T1.n_regionkey = T2.r_regionkey INNER JOIN supplier AS T3 ON T1.n_nationkey = T3.s_nationkey WHERE T2.r_name = 'EUROPE' AND T3.s_acctbal < 0	retails
SELECT T3.c_name FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey INNER JOIN customer AS T3 ON T1.o_custkey = T3.c_custkey WHERE T2.l_discount = 0.1 AND STRFTIME('%Y', T1.o_orderdate) BETWEEN 1994 AND 1995	retails
SELECT COUNT(T2.l_partkey) FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T1.o_orderdate = '1994-09-21' AND T2.l_shipdate = '1994-11-19'	retails
SELECT COUNT(DISTINCT T1.`Order ID`) FROM west_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` INNER JOIN people AS T3 ON T3.`Customer ID` = T1.`Customer ID` WHERE T1.Sales > 5000 AND T3.State = 'California' AND T2.Region = 'West'	superstore
SELECT l_linenumber FROM lineitem WHERE l_discount = 0.1 LIMIT 3	retails
SELECT COUNT(p_partkey) FROM part WHERE p_type = 'PROMO BRUSHED STEEL' AND p_mfgr = 'Manufacturer#5'	retails
SELECT T3.`Product Name` FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Darren Powers' ORDER BY T2.`Order Date` DESC LIMIT 1	superstore
SELECT CAST((MAX(T1.ps_supplycost) - MIN(T1.ps_supplycost)) AS REAL) * 100 / MIN(T1.ps_supplycost) FROM partsupp AS T1 INNER JOIN supplier AS T2 ON T1.ps_suppkey = T2.s_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey WHERE T3.p_name = 'hot spring dodger dim light'	retails
SELECT T1.p_name FROM part AS T1 INNER JOIN partsupp AS T2 ON T1.p_partkey = T2.ps_partkey WHERE T2.ps_supplycost > 1000	retails
SELECT T1.Name FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID INNER JOIN Customers AS T3 ON T2.CustomerID = T3.CustomerID WHERE T3.FirstName = 'Kathryn' AND T3.LastName = 'Ashe' ORDER BY T2.Quantity DESC LIMIT 1	sales
SELECT l_orderkey FROM lineitem WHERE l_orderkey IN (4, 36) ORDER BY l_shipdate DESC LIMIT 1	retails
SELECT T2.FirstName, T2.LastName FROM Sales AS T1 INNER JOIN Customers AS T2 ON T1.CustomerID = T2.CustomerID WHERE T2.FirstName = 'Kate' ORDER BY T1.Quantity DESC LIMIT 1	sales
SELECT SUM(T1.Quantity) FROM south_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T2.`Customer Name` = 'Cindy Stewart' AND T3.`Product Name` = 'Lexmark X 9575 Professional All-in-One Color Printer'	superstore
SELECT CAST(SUM(IIF(ps_supplycost > 500, 1, 0)) AS REAL) * 100 / COUNT(ps_suppkey) FROM partsupp	retails
SELECT COUNT(OrderID) FROM Orders WHERE OrderDate LIKE '1996-08%' GROUP BY CustomerID ORDER BY COUNT(OrderID) DESC LIMIT 1	retail_world
SELECT SUM(T2.Profit) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.City = 'Houston' AND T1.State = 'Texas' AND T2.Region = 'Central'	superstore
SELECT COUNT(T1.c_custkey) FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T2.n_name = 'INDIA'	retails
SELECT T.p_name FROM ( SELECT T3.p_name , T2.l_extendedprice * (1 - T2.l_discount) - T1.ps_supplycost * T2.l_quantity AS num FROM partsupp AS T1 INNER JOIN lineitem AS T2 ON T1.ps_suppkey = T2.l_suppkey INNER JOIN part AS T3 ON T1.ps_partkey = T3.p_partkey ) AS T ORDER BY T.num DESC LIMIT 1	retails
SELECT T1.FirstName, T1.MiddleInitial, T1.LastName FROM Employees AS T1 INNER JOIN Sales AS T2 ON T2.SalesPersonID = T1.EmployeeID GROUP BY T2.SalesPersonID, T1.FirstName, T1.MiddleInitial, T1.LastName ORDER BY COUNT(T2.SalesID) DESC LIMIT 1	sales
SELECT DISTINCT T2.FirstName, T2.MiddleInitial, T2.LastName FROM Sales AS T1 INNER JOIN Employees AS T2 ON T1.SalesPersonID = T2.EmployeeID WHERE T1.Quantity = 1000	sales
SELECT SUM(T1.Sales) FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.`Product Name` = 'Avery Hi-Liter EverBold Pen Style Fluorescent Highlighters, 4/Pack' AND T2.Region = 'Central'	superstore
SELECT AVG(T1.Sales) FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T3.`Product Name` = 'Sharp AL-1530CS Digital Copier'	superstore
SELECT T1.LastName FROM Customers AS T1 INNER JOIN Sales AS T2 ON T1.CustomerID = T2.CustomerID WHERE T2.SalesID = 178	sales
SELECT COUNT(T2.c_name) FROM orders AS T1 INNER JOIN customer AS T2 ON T1.o_custkey = T2.c_custkey WHERE T2.c_mktsegment = 'BUILDING' AND T1.o_totalprice > 50000	retails
SELECT COUNT(T1.r_regionkey) FROM region AS T1 INNER JOIN nation AS T2 ON T1.r_regionkey = T2.n_regionkey INNER JOIN supplier AS T3 ON T2.n_nationkey = T3.s_nationkey WHERE T1.r_name = 'EUROPE'	retails
SELECT JULIANDAY(T2.l_receiptdate) - JULIANDAY(T2.l_commitdate) FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T1.o_custkey = '129301' AND T1.o_orderdate = '1996-07-27'	retails
SELECT COUNT(T1.o_orderkey) FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T2.l_shipmode = 'SHIP' AND T1.o_orderpriority = '3-MEDIUM'	retails
SELECT DISTINCT (T2.Sales / (1 - T2.discount)) * T2.Quantity - Profit FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Aimee Bixby' AND T3.`Product Name` = 'Xerox 1952' AND T2.`Order Date` = '2014-09-10'	superstore
SELECT SUM(IIF(l_returnflag = 'A', 1, 0)) - SUM(IIF(l_returnflag = 'N', 1, 0)) AS diff FROM lineitem WHERE l_extendedprice < 16947.7	retails
SELECT COUNT(T1.n_nationkey) FROM nation AS T1 INNER JOIN region AS T2 ON T1.n_regionkey = T2.r_regionkey INNER JOIN supplier AS T3 ON T1.n_nationkey = T3.s_nationkey WHERE T2.r_name = 'EUROPE'	retails
SELECT CAST(SUM(CASE  WHEN T2.Discount = 0.2 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.State = 'Texas'	superstore
SELECT CAST(SUM(IIF(T2.Price BETWEEN 200 AND 300, 1, 0)) AS REAL) * 100 / COUNT(T2.Price) FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T1.SalesID BETWEEN 1 AND 200	sales
SELECT DISTINCT T2.`Product Name` FROM east_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T1.`Order ID` = 'CA-2011-141817'	superstore
SELECT COUNT(DISTINCT T2.`Order ID`) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.State = 'Texas'	superstore
SELECT T1.s_phone FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T2.n_name = 'Germany'	retails
SELECT COUNT(l_linenumber) FROM lineitem WHERE l_orderkey = 5 AND l_returnflag = 'R'	retails
SELECT COUNT(l_orderkey) FROM lineitem WHERE STRFTIME('%Y', l_shipdate) = '1998'	retails
SELECT SUM(num) FROM ( SELECT COUNT(T3.s_name) AS num FROM part AS T1 INNER JOIN partsupp AS T2 ON T1.p_partkey = T2.ps_partkey INNER JOIN supplier AS T3 ON T2.ps_suppkey = T3.s_suppkey WHERE T1.p_type = 'PROMO BRUSHED STEEL' GROUP BY T2.ps_partkey HAVING SUM(T2.ps_availqty) < 5000 ) T	retails
SELECT Name FROM Products WHERE Price = 0	sales
SELECT COUNT(T1.c_custkey) FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_mktsegment = 'AUTOMOBILE' AND T2.n_name = 'BRAZIL'	retails
SELECT DISTINCT T2.`Customer Name` FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.`Order Date` = '2013-08-12' AND T1.Discount = 0.2 AND T1.Region = 'West'	superstore
SELECT T1.c_name FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_acctbal > 5000 AND T2.n_name = 'INDIA'	retails
SELECT T1.FirstName, T1.LastName FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID GROUP BY T1.FirstName, T1.LastName ORDER BY COUNT(*) DESC LIMIT 1	retail_world
SELECT COUNT(T1.o_orderkey) FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T2.l_shipmode = 'REG AIR' AND T1.o_orderdate = '1995-03-22'	retails
SELECT DISTINCT T2.`Customer Name` FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.Region = 'West' AND T1.`Ship Mode` = 'Second Class' LIMIT 5	superstore
SELECT COUNT(DISTINCT T2.`Order ID`) FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Aimee Bixby' AND T3.`Product Name` = 'Xerox 1952'	superstore
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey GROUP BY T1.s_nationkey ORDER BY COUNT(T1.s_name) LIMIT 1	retails
SELECT CAST(SUM(IIF(T1.r_name = 'ASIA', 1, 0)) AS REAL) * 100 / COUNT(T1.r_regionkey) FROM region AS T1 INNER JOIN nation AS T2 ON T1.r_regionkey = T2.n_regionkey INNER JOIN supplier AS T3 ON T2.n_nationkey = T3.s_nationkey	retails
SELECT T2.c_name FROM orders AS T1 INNER JOIN customer AS T2 ON T1.o_custkey = T2.c_custkey WHERE T1.o_totalprice = 191918.92 AND T1.o_custkey = 93697	retails
SELECT T1.Description FROM Categories AS T1 INNER JOIN Products AS T2 ON T1.CategoryID = T2.CategoryID WHERE T2.ProductName = 'tofu'	retail_world
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey ORDER BY T1.s_acctbal LIMIT 1	retails
SELECT COUNT(T2.c_custkey) FROM orders AS T1 INNER JOIN customer AS T2 ON T1.o_custkey = T2.c_custkey WHERE T2.c_acctbal > 0 AND T1.o_orderpriority = '1-URGENT'	retails
SELECT CAST(SUM(CASE  WHEN State = 'Texas' THEN 1 ELSE 0 END) AS REAL) * 100 / SUM(CASE  WHEN State = 'Indiana' THEN 1 ELSE 0 END) FROM people	superstore
SELECT SUM(T1.Price * T2.quantity) FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID WHERE T1.Name = 'Reflector'	sales
SELECT COUNT(l_linenumber) FROM lineitem WHERE l_shipdate = '1993-12-04'	retails
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T1.s_suppkey = 1	retails
SELECT SUM(T3.Price * T2.quantity) FROM Customers AS T1 INNER JOIN Sales AS T2 ON T1.CustomerID = T2.CustomerID INNER JOIN Products AS T3 ON T2.ProductID = T3.ProductID WHERE T1.FirstName = 'Adam'	sales
SELECT CAST(SUM(IIF(T2.r_name = 'EUROPE', 1, 0)) AS REAL) * 100 / COUNT(T1.n_name) FROM nation AS T1 INNER JOIN region AS T2 ON T1.n_regionkey = T2.r_regionkey	retails
SELECT SUM(T1.o_totalprice) FROM orders AS T1 INNER JOIN customer AS T2 ON T1.o_custkey = T2.c_custkey WHERE T2.c_name = 'Customer#000000013'	retails
SELECT c_name FROM customer WHERE c_acctbal < 0 LIMIT 3	retails
SELECT DISTINCT T2.`Product Name` FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T1.`Order ID` = 'CA-2011-112326'	superstore
SELECT COUNT(T2.c_custkey) FROM nation AS T1 INNER JOIN customer AS T2 ON T1.n_nationkey = T2.c_nationkey INNER JOIN orders AS T3 ON T2.c_custkey = T3.o_custkey WHERE T1.n_name = 'GERMANY'	retails
SELECT T.s_acctbal FROM ( SELECT T1.s_acctbal, COUNT(T2.ps_suppkey) AS num FROM supplier AS T1 INNER JOIN partsupp AS T2 ON T1.s_suppkey = T2.ps_suppkey GROUP BY T1.s_suppkey ) AS T ORDER BY T.num DESC LIMIT 1	retails
SELECT T2.n_name FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey GROUP BY T2.n_name HAVING COUNT(T1.c_name) > ( SELECT COUNT(customer.c_name) / COUNT(DISTINCT nation.n_name) FROM customer INNER JOIN nation ON customer.c_nationkey = nation.n_nationkey ) ORDER BY COUNT(T1.c_name)	retails
SELECT T1.Name, SUM(T2.Quantity * T1.Price) FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID GROUP BY T1.ProductID, T1.Name ORDER BY SUM(T2.Quantity) DESC LIMIT 1	sales
SELECT FirstName, MiddleInitial, LastName FROM Employees WHERE EmployeeID = 7	sales
SELECT T.p_name FROM ( SELECT p_name, p_size FROM part WHERE p_name IN ('pink powder drab lawn cyan', 'cornflower sky burlywood green beige') ) AS T ORDER BY p_size DESC LIMIT 1	retails
SELECT COUNT(l_orderkey) FROM lineitem WHERE STRFTIME('%Y', l_shipdate) = '1994' AND l_returnflag = 'R' AND l_shipmode = 'TRUCK'	retails
SELECT T1.SalesID FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T2.Name = 'External Lock Washer 7' AND T1.Quantity = 590	sales
SELECT T1.Sales, T1.Profit, T2.`Sub-Category` FROM east_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T1.`Order ID` = 'US-2011-126571' AND T2.Region = 'East'	superstore
SELECT T2.`Product Name` FROM east_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Region = 'East' ORDER BY T1.Quantity DESC LIMIT 1	superstore
SELECT T2.l_extendedprice * (1 - T2.l_discount) * (1 + T2.l_tax) AS num FROM orders AS T1 INNER JOIN lineitem AS T2 ON T1.o_orderkey = T2.l_orderkey WHERE T1.o_clerk = 'Clerk#000000936' AND T2.l_shipmode = 'TRUCK' AND T1.o_orderstatus = '4-NOT SPECIFIED' AND T1.o_orderdate = '1995-03-13'	retails
SELECT DISTINCT T3.`Product Name` FROM west_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T2.`Customer Name` = 'Matt Abelman' AND STRFTIME('%Y', T1.`Order Date`) = '2013'	superstore
SELECT l_orderkey FROM lineitem ORDER BY l_extendedprice * (1 - l_discount) LIMIT 3	retails
SELECT CAST(SUM(CASE  WHEN T1.`Ship Mode` = 'First Class' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*) FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.Category = 'Furniture' AND STRFTIME('%Y', T1.`Ship Date`) = '2013'	superstore
SELECT COUNT(DISTINCT T1.`Product ID`) FROM east_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE T2.`Sub-Category` = 'Art' AND T1.Region = 'East' AND STRFTIME('%Y', T1.`Order Date`) = '2013'	superstore
SELECT T2.Quantity, T1.Price FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID INNER JOIN Customers AS T3 ON T2.CustomerID = T3.CustomerID WHERE T3.FirstName = 'Abigail' AND T3.LastName = 'Henderson'	sales
SELECT COUNT(T1.s_suppkey) FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T2.n_name = 'GERMANY'	retails
SELECT Name FROM Products WHERE Price = ( SELECT MAX(Price) FROM Products )	sales
SELECT T3.o_orderkey FROM nation AS T1 INNER JOIN customer AS T2 ON T1.n_nationkey = T2.c_nationkey INNER JOIN orders AS T3 ON T2.c_custkey = T3.o_custkey WHERE T1.n_name = 'GERMANY' ORDER BY T3.o_orderdate LIMIT 1	retails
SELECT SUM(T1.p_partkey) FROM part AS T1 INNER JOIN lineitem AS T2 ON T1.p_partkey = T2.l_partkey WHERE T1.p_name = 'hot spring dodger dim light'	retails
SELECT DISTINCT T2.`Customer Name` FROM east_superstore AS T1 INNER JOIN people AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T1.`Product ID` WHERE T3.`Product Name` = 'Global High-Back Leather Tilter, Burgundy' AND T1.`Order Date` = '2013-10-13' AND T1.Region = 'East'	superstore
SELECT T2.FirstName, T2.MiddleInitial, T2.LastName FROM Sales AS T1 INNER JOIN Customers AS T2 ON T1.CustomerID = T2.CustomerID GROUP BY T1.Quantity HAVING T1.Quantity > ( SELECT AVG(Quantity) FROM Sales )	sales
SELECT DISTINCT T2.`Order ID` FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` WHERE T1.`Customer Name` = 'Aimee Bixby' GROUP BY T2.`Product ID` HAVING COUNT(T2.`Product ID`) > 3	superstore
SELECT CAST(COUNT(T1.CustomerID) AS REAL) / COUNT(T3.EmployeeID) FROM Customers AS T1 INNER JOIN Sales AS T2 ON T1.CustomerID = T2.CustomerID INNER JOIN Employees AS T3 ON T2.SalesPersonID = T3.EmployeeID	sales
SELECT COUNT(T1.CustomerID) FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T2.Name = 'Hex Nut 9'	sales
SELECT DISTINCT T2.`Ship Date`, T3.`Product Name` FROM people AS T1 INNER JOIN central_superstore AS T2 ON T1.`Customer ID` = T2.`Customer ID` INNER JOIN product AS T3 ON T3.`Product ID` = T2.`Product ID` WHERE T1.`Customer Name` = 'Gene Hale'	superstore
SELECT T1.n_name, T1.n_nationkey FROM nation AS T1 INNER JOIN region AS T2 ON T1.n_regionkey = T2.r_regionkey WHERE T2.r_name = 'AFRICA'	retails
SELECT T1.c_phone FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_mktsegment = 'HOUSEHOLD' AND T2.n_name = 'BRAZIL'	retails
SELECT COUNT(c_custkey) FROM customer WHERE c_acctbal < 0	retails
SELECT COUNT(T2.OrderID) FROM Employees AS T1 INNER JOIN Orders AS T2 ON T1.EmployeeID = T2.EmployeeID WHERE T1.FirstName = 'Michael' AND T1.LastName = 'Suyama'	retail_world
SELECT CAST(SUM(IIF(T2.n_name = 'IRAN', 1, 0)) AS REAL) * 100 / COUNT(T2.n_name) FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_mktsegment = 'HOUSEHOLD'	retails
SELECT o_orderpriority FROM orders WHERE o_totalprice = ( SELECT MAX(o_totalprice) FROM orders )	retails
SELECT COUNT(T1.CustomerID) FROM Customers AS T1 INNER JOIN Orders AS T2 ON T1.CustomerID = T2.CustomerID WHERE STRFTIME('%Y', T2.OrderDate) = '1996' AND T1.Country = 'UK'	retail_world
SELECT IIF(SUM(IIF(T1.Name = 'HL Mountain Frame - Silver, 42', T2.SalesID, 0)) - SUM(IIF(T1.Name = 'HL Mountain Frame - Black, 42', T2.SalesID, 0)) > 0, 'Silver', 'Black') FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID	sales
SELECT COUNT(ps_suppkey) FROM partsupp WHERE ps_availqty < 10	retails
SELECT T1.FirstName, T1.LastName FROM Customers AS T1 INNER JOIN Sales AS T2 ON T1.CustomerID = T2.CustomerID WHERE T1.FirstName = 'Cameron' ORDER BY T2.Quantity DESC LIMIT 1	sales
SELECT T2.s_phone FROM lineitem AS T1 INNER JOIN supplier AS T2 ON T1.l_suppkey = T2.s_suppkey WHERE T1.l_orderkey = 1	retails
SELECT COUNT(p_partkey) FROM part WHERE p_retailprice > 1900	retails
SELECT COUNT(T1.c_name) FROM customer AS T1 INNER JOIN nation AS T2 ON T1.c_nationkey = T2.n_nationkey WHERE T1.c_mktsegment = 'HOUSEHOLD' AND T2.n_name = 'GERMANY'	retails
SELECT CAST(SUM(IIF(T3.FirstName = 'Albert' AND T3.MiddleInitial = 'I' AND T3.LastName = 'Ringer', 1, 0)) AS REAL) * 100 / COUNT(T2.CustomerID) FROM Products AS T1 INNER JOIN Sales AS T2 ON T1.ProductID = T2.ProductID INNER JOIN Employees AS T3 ON T2.SalesPersonID = T3.EmployeeID WHERE T1.Name = 'ML Bottom Bracket'	sales
SELECT c_mktsegment FROM customer WHERE c_acctbal = ( SELECT MIN(c_acctbal) FROM customer )	retails
SELECT p_name FROM part WHERE p_retailprice = ( SELECT MAX(p_retailprice) FROM part )	retails
SELECT T2.n_name FROM supplier AS T1 INNER JOIN nation AS T2 ON T1.s_nationkey = T2.n_nationkey WHERE T1.s_acctbal = 4393.04	retails
SELECT T1.Quantity FROM Sales AS T1 INNER JOIN Products AS T2 ON T1.ProductID = T2.ProductID WHERE T2.Name = 'Chainring Bolts' AND T1.SalesID = 551971	sales
SELECT DISTINCT T2.`Product Name` FROM central_superstore AS T1 INNER JOIN product AS T2 ON T1.`Product ID` = T2.`Product ID` WHERE strftime('%Y-%m', T1.`Ship Date`) = '2013-03'	superstore
SELECT MAX(s_acctbal) FROM supplier	retails
SELECT c_name FROM customer WHERE c_acctbal = ( SELECT MIN(c_acctbal) FROM customer )	retails
SELECT c_mktsegment, c_name, c_address, c_phone FROM customer WHERE c_custkey = 3	retails
