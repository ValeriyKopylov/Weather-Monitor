# Schedule

Task | Assigned to | Deadline | Status
---- | ----------- | -------- | ------
Register on github | Vladimir | 02/10 | 
Establish radio connection between carrier and outpost | Vladimir | 02/10 | 
Prepare carrier-outpost comm protocol | @EvgenyAgafonchikov | | 
Make outpost prototype with some sensors | @EvgenyAgafonchikov | | 
Implement comm protocol on outpost | @EvgenyAgafonchikov | | 
Implement comm protocol on carrier | @EvgenyAgafonchikov | | 
Implement data storing on carrier | @EvgenyAgafonchikov | | 
Implement web server on carrier | @EvgenyAgafonchikov+@RomanGromov | | 
Implement data sending through http on carrier | @EvgenyAgafonchikov+@RomanGromov | | 
Create VM for server | @ValeriyKopylov | | *Done*
Create DB with sample data | @ValeriyKopylov | 02/10 | 
Deploy VM to work PC | @ValeriyKopylov | 02/11 | 
Prepare script-carrier comm protocol | @ValeriyKopylov | 02/13 | 
Implement data collector script | @ValeriyKopylov | 02/15 | 
Implement carrier emulator for test purposes | @ValeriyKopylov | 02/15 | 
Deploy script to VM, add to cron | @ValeriyKopylov | 02/16 | 
Install Node.js on VM | @RomanGromov | | 
Make web service | @RomanGromov | | 
Make client application | @RomanGromov | | 
Prepare math module command line interface | @ValeriyKopylov+Vladimir | 02/13 | 
Implement math module barebone: read argv, connect to DB, read & write dummy values | Vladimir | | 
Prepare first math module model | Vladimir | | 
Add tables & fields for math module to DB | Vladimir+@ValeriyKopylov | | 
Implement math module model | Vladimir | | 
Deploy math module to VM, add to cron | Vladimir+@ValeriyKopylov | | 

# Components and their functions

## Sensor box (outpost)
A hardware device based on microcontroller (Arduino or probably another, cheaper one). 

### Main purposes
1. Make measurements
2. Send results to the main module

### Main components
1. Microcontroller
2. Several sensors to indicate:
  * Temperature
  * Humidity
  * Air pressure
  * CO<sub>2</sub> concentration level
  * O<sub>2</sub> concentration level
  * Luminosity
3. Radio module – translator
4. LED and audio indicators
5. Autonomous power source

### Workflow
1. The sensors make measurements in the infinite loop.
2. The processor reads data, encodes it, and translates encoded data by radio channel.

## Main module (carrier)
A hardware Arduino-based device

### Main purposes
1. Collect data from several sensor boxes
2. Store data  in memory
3. Provide access to stored data using http over Ethernet connection

### Main components
1. Microcontroller
2. Radio module – receiver
3. Flash (or other) memory module
4. Ethernet module
5. LED and audio indicators
6. AC power supply

### Workflow
Thread 1: receives sensors data from radio module, decodes it, and stores into memory using cycling overwrite mode.

Thread 2: opens TCP socket and waits for connections. Creates new thread for each incoming connection.

Thread 3...N: receives http request for data from sensors, prepares answer using recently collected data from memory, and sends http response back to the socket.

## Data collector script
Cross-platform daemon without GUI, works on server	

### Main purposes
Retrieve sensors data from single carrier and save it to DB

### Workflow
1. Daemon is started by web service and receives all parameters through command line arguments:
  * DB connection parameters
  * Carrier id on DB
2. Periodically daemon sends http request to its carrier, receives http response with sensors data, and inserts measurements results into DB.

## Database
DB with fast engine capable to work with compressed tables. MySQL, for instance.

### Main purposes
1. Store measurements from sensors.
2. Compress old measurements.
3. Perform SELECT queries as fast as possible.

### Main tables
1. Carriers – dictionary of carriers
  * Carrier id
  * Carrier name
  * Carrier description
  * Last contact time
2. Sensors – dictionary of sensor types
  * Sensor id
  * Sensor name
  * Sensor description
3. Measurements – main table with sensors data
  * Carrier id
  * Sensor id
  * Measurement time
  * Value
4. Math processors – dictionary of statistics calculators and weather predictors
  * Processor id
  * Processor name
  * Processor description
  * Processor file name
5. Statistics – set of tables, one per math processor, containing results of math processor calculations
  * Calculation id
  * Calculation time
  * Calculation results, names and types of fields depend on math processor

### Data size estimation
Let’s suppose that we have 1 carrier with 10 outposts. Measurements are made each second. In case all value are changed each measurement, measurements table has 10 outposts * 6 sensors * 16 bytes per record = 960 bytes per second or 79.1 MB per day:

Period  | Number of rows | Size of data
------- | -------------- | -------------
Daily   | 5 184 000      | 79 MB
Monthly | 155 520 000    | 2.3 GB
Yearly  | 1 892 160 000  | 28 GB

However, the more realistic is that values are changed once per minute (or even less frequent), so data amount generated by a carrier may be estimated as follows:

Period  | Number of rows | Size of data
------- | -------------- | -------------
Daily   | 86 400         | 1.3 MB
Monthly | 2 592 000      | 40 MB
Yearly  | 31 536 000     | 481 MB

### Workflow
Having only 1 carrier, DB is small and does not need any optimization. Otherwise, if we plan to make the solution scalable, DB must compress old data that is unlikely to be often requested. We can create new table each month and compress all tables older than 2 months: in this case we always have plain data for last 30–60 days and may easily and fast enough access the compressed data from certain month.

## Math processor
Cross-platform C++ (or other proper language) program without GUI

### Main purposes
1. Calculate complex statistic characteristics involving strong math that requires fast calculations
2. Find correlations and make predictions based on collected measurements

### Workflow
1. Processor is called by web service and receives all parameters through command line arguments:
  * DB connection parameters
  * Processor id on DB
  * Processor specific parameters to configure calculation parameters
2. Processor connects to DB and gets all required data from there
3. Processor calculates statistics or make predictions and store results into its own table on DB
4. Processor’s return code notifies web service whether calculation has finished successfully or not.

## Web service
Works on server, processes requests from client application and controls DB

### Workflow
1. Upon start:
  * Open connection to DB
  * Start data collector script for each carrier registered on DB
2. Upon accepting a client request, web service decides if it is able to process the request by itself:
  * Simple request: enquire data from DB and return it to client
  * Complex request: call math processor, wait till it finishes, extract its results from DB, and return them to client

## Client web application
Mobile/browser application

### Functionalities and use cases
1. Show status of carriers and outpost
2. Register new carriers and delete old from the system
3. Show current measurements from selected sensors
4. Draw graph from sensor in real time
5. Draw graph from sensor for past period
6. Draw several curves from sensors of same type on single graph
7. Find correlations between measurements
8. Predict weather

# Communications
![Comm diagram](https://raw.githubusercontent.com/ValeriyKopylov/Weather-Monitor/master/Diagrams/CommDiagram.png)

# Key principles
1. Module system – each component is as independent as possible, we also should have certain and transparent descriptions of communications protocols between modules.
2. Scalability – most of system modules should be easily expandable:
  * Number of outposts per carrier – limited by radio module restrictions, below the maximum frequencies limit we should be able to easily add new outposts.
  * Carrier management – it should be easy to add a new carrier into the system. Since carriers communicate with server only by TCP, new carriers may be placed anywhere, for example, in my apartments. I can even place an outpost into my car, and it should be visible by either the office carrier or by my home carrier depending on where the car is now.
  *  Math processors – universal processor interface should allow ease adding of new processors calculating different statistics.
  * Web service interface should simplify adding new clients of different kinds: mobile, browser, desktop, console apps.
3. Publicity – all sources should be shared on github, and we must decide which license to use.