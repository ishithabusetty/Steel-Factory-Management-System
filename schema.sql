-- =========================================
-- SEED.SQL • Full Database Setup + Inserts
-- Steel Factory Management System
-- Fully Compatible with app.py
-- =========================================

DROP DATABASE IF EXISTS steel_factory_db;
CREATE DATABASE steel_factory_db;
USE steel_factory_db;

-- =========================================
-- USERS TABLE
-- =========================================
CREATE TABLE users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('admin','user') NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed admin user (username: mrudula, password: mrudula)
INSERT INTO users (Username, PasswordHash, Role)
VALUES ('mrudula', 'scrypt:32768:8:1$K3yDMKaig6xCP7m6$7cf03d9f6d758614c276e40ecaab9810b32f4569dd69c935ecb1c1c5ef967f03edc560a52f76eb3bdf58ff846feeee9e6c8e067bc3033aacd56f2cdfcdce77a6', 'admin');

-- =========================================
-- MACHINE TABLE
-- =========================================
CREATE TABLE Machine (
    MachineID INT PRIMARY KEY AUTO_INCREMENT,
    MachineName VARCHAR(100) NOT NULL,
    MachineType VARCHAR(50),
    Location VARCHAR(50),
    Status VARCHAR(20)
);

-- =========================================
-- PRODUCTION BATCH TABLE
-- =========================================
CREATE TABLE Production_Batch (
    BatchID INT PRIMARY KEY AUTO_INCREMENT,
    BatchCode VARCHAR(50),
    StartTime DATETIME,
    EndTime DATETIME,
    ProductType VARCHAR(50),
    QuantityPlanned INT
);

-- =========================================
-- PERFORMANCE DATA TABLE
-- (correct columns for your Flask app)
-- =========================================
CREATE TABLE Performance_Data (
    PerformanceID INT PRIMARY KEY AUTO_INCREMENT,
    MachineID INT,
    BatchID INT,
    OperatingTime FLOAT,
    Downtime FLOAT DEFAULT 0,
    ActualOutput INT,
    IdealOutput INT,
    GoodUnits INT,
    TotalUnits INT,
    OEE FLOAT,
    FOREIGN KEY (MachineID) REFERENCES Machine(MachineID),
    FOREIGN KEY (BatchID) REFERENCES Production_Batch(BatchID)
);

-- =========================================
-- ALERTS TABLE
-- =========================================
CREATE TABLE Alerts (
    AlertID INT PRIMARY KEY AUTO_INCREMENT,
    MachineID INT,
    AlertMessage TEXT,
    Severity VARCHAR(20),
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MachineID) REFERENCES Machine(MachineID)
);

-- =========================================
-- MAINTENANCE LOG
-- =========================================
CREATE TABLE Maintenance_Log (
    MaintenanceID INT PRIMARY KEY AUTO_INCREMENT,
    MachineID INT,
    IssueDescription TEXT,
    MaintenanceDate DATETIME,
    Status VARCHAR(20),
    FOREIGN KEY (MachineID) REFERENCES Machine(MachineID)
);

-- =========================================
-- ANOMALY DETECTION
-- =========================================
CREATE TABLE Anomaly_Detection (
    AnomalyID INT PRIMARY KEY AUTO_INCREMENT,
    MachineID INT,
    PerformanceID INT,
    AnomalyScore FLOAT,
    IsAnomaly BOOLEAN,
    Timestamp DATETIME,
    FOREIGN KEY (MachineID) REFERENCES Machine(MachineID),
    FOREIGN KEY (PerformanceID) REFERENCES Performance_Data(PerformanceID)
);

-- =========================================
-- BLOCKCHAIN LOG (correct schema)
-- =========================================
CREATE TABLE Blockchain_Log (
    BlockID INT PRIMARY KEY AUTO_INCREMENT,
    PerformanceID INT,
    Hash VARCHAR(255),
    PrevHash VARCHAR(255),
    Data TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PerformanceID) REFERENCES Performance_Data(PerformanceID)
);

-- =========================================
-- INSERT: MACHINE
-- =========================================
INSERT INTO Machine (MachineName, MachineType, Location, Status) VALUES
('Furnace A1', 'Furnace', 'Zone 1', 'Active'),
('Rolling Machine R2', 'Rolling', 'Zone 2', 'Active'),
('Cooling Unit C1', 'Cooling', 'Zone 3', 'Inactive'),
('Cutter CT3', 'Cutter', 'Zone 4', 'Active');

-- =========================================
-- INSERT: PRODUCTION BATCHES
-- =========================================
INSERT INTO Production_Batch 
(BatchCode, StartTime, EndTime, ProductType, QuantityPlanned)
VALUES
('101', '2025-11-11 22:45:44', '2025-11-11 22:45:44', '8', 950),
('102', '2025-11-11 22:45:44', '2025-11-11 22:45:44', '8', 850),
('103', '2025-11-11 22:45:44', '2025-11-11 22:45:44', '8', 1000),
('104', '2025-11-11 22:45:44', '2025-11-11 22:45:44', '8', 920);

-- =========================================
-- INSERT: PERFORMANCE DATA
-- Using correct PerformanceID 1–7
-- =========================================
INSERT INTO Performance_Data
(MachineID, BatchID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits, OEE)
VALUES
(1, 1, 7.5, 0.5, 970,1000,590,600, 89.4219),
(2, 2, 6.0, 2.0, 967,1000,589,600, 71.1954),
(3, 3, 8.0, 0.0, 990,1000,450,600, 74.25),
(4, 4, 7.0, 1.0, 920,1000,950,1000,76.475),
(1, 1, 7.5, 0.5, 950,1000,480,500, 85.5),
(1, 1, 4.0, 1.0, 585,600,489,500, 76.284),
(3, 3, 5.5, 5.0, 954,960,945,960, 51.2402);

-- =========================================
-- INSERT: ALERTS
-- =========================================
INSERT INTO Alerts (MachineID, AlertMessage, Severity, Timestamp) VALUES
(3, 'Anomaly detected for Machine 3 (score -0.02)', 'MEDIUM', '2025-11-30 16:20:22'),
(3, 'Anomaly detected for Machine 3 (score -0.02)', 'MEDIUM', '2025-11-30 16:20:27'),
(3, 'Anomaly detected for Machine 3 (score -0.02)', 'MEDIUM', '2025-11-30 16:20:49'),
(3, 'Cooling Unit C1: ML anomaly detected (score -0.013)', 'MEDIUM', '2025-11-30 16:27:07'),
(3, 'Cooling Unit C1: ML anomaly detected (score -0.028)', 'MEDIUM', '2025-11-30 16:55:42');

-- =========================================
-- INSERT: BLOCKCHAIN LOG
-- All PerformanceID references fixed
-- =========================================
INSERT INTO Blockchain_Log
(BlockID, PerformanceID, Hash, PrevHash, Data, Timestamp)
VALUES
(1,5,'ca2c5865ea06d63e580402ac3d4cb98e3e044e2affbb10dd21905483974425ba','0',
 'PerformanceID=5|MachineID=1|OperatingTime=7.5|ActualOutput=950|IdealOutput=1000|OEE=88.125',
 '2025-11-26 23:05:36'),

(2,6,'ae25bcaa414a2f75144a9894e9405e6adbf739d02b17757a05bfc36f5e5c846e',
 'ca2c5865ea06d63e580402ac3d4cb98e3e044e2affbb10dd21905483974425ba',
 'PerformanceID=6|MachineID=1|OperatingTime=4.0|ActualOutput=500|IdealOutput=600|GoodUnits=480|TotalUnits=500|OEE=64.0',
 '2025-11-26 23:42:44'),

(3,3,'3e90f399019e3e45f8f424bf2fe55207c57aad36ce9d827bba70104d0c81166d',
 'ae25bcaa414a2f75144a9894e9405e6adbf739d02b17757a05bfc36f5e5c846e',
 'MODIFICATION|PerformanceID=3|NewOperatingTime=8.0|NewActualOutput=990|NewIdealOutput=1000|NewGoodUnits=450|NewTotalUnits=600|NewOEE=66.0',
 '2025-11-27 10:07:35'),

(5,NULL,'c00a080cab3d15e1ac96500881b0f7d3554f39e8d59d86c0fd87c010085b2369',
 '3e90f399019e3e45f8f424bf2fe55207c57aad36ce9d827bba70104d0c81166d',
 'ADD_MACHINE|MachineID=12|Name=Furnace A3|Type=Furnace|Loc=Zone 3|Status=Active',
 '2025-11-27 20:20:24'),

(6,5,'caf45c89231b3c48a84af167479c58858a5c633af41e0c16f3f15cac3d56ccc8',
 'c00a080cab3d15e1ac96500881b0f7d3554f39e8d59d86c0fd87c010085b2369',
 'MODIFY_PERFORMANCE|PerformanceID=5|NewOperatingTime=7.5|NewDowntime=0.5|NewActualOutput=950|NewIdealOutput=1000|NewGoodUnits=480|NewTotalUnits=500|NewOEE=85.5',
 '2025-11-27 20:35:27'),

(7,4,'46117a1578197442722e50d21735ebcda8c1f7abfd7ec217227b8e18238737e7',
 'caf45c89231b3c48a84af167479c58858a5c633af41e0c16f3f15cac3d56ccc8',
 'MODIFY_PERFORMANCE|PerformanceID=4|NewOperatingTime=7.0|NewDowntime=1.0|NewActualOutput=920|NewIdealOutput=1000|NewGoodUnits=950|NewTotalUnits=1000|NewOEE=76.475',
 '2025-11-27 20:35:44'),

(8,7,'eeb1c18863ad8ca96a966866702ea993a01c6ff1c5575cf934f4d349e314b3cb',
 '46117a1578197442722e50d21735ebcda8c1f7abfd7ec217227b8e18238737e7',
 'ADD_PERFORMANCE|PerformanceID=7|MachineID=3|OperatingTime=5.5|Downtime=5.0|ActualOutput=850|IdealOutput=960|GoodUnits=760|TotalUnits=800|OEE=44.06',
 '2025-11-27 20:36:24'),

(9,NULL,'022af4a0e7dfd08f159a4b011402f39d3e380054d9604b4e200cfd4afbeeb4d9',
 'eeb1c18863ad8ca96a966866702ea993a01c6ff1c5575cf934f4d349e314b3cb',
 'ADD_MACHINE|MachineID=13|Name=Furnace A3|Type=Furnace|Loc=Zone 3|Status=Active',
 '2025-11-27 20:36:43'),

(11,NULL,'a38efcff51a59155db0ba25704803b9f157ba0b4ac2b9960b7a505c3b5fb4f1f',
 '022af4a0e7dfd08f159a4b011402f39d3e380054d9604b4e200cfd4afbeeb4d9',
 'ADD_MACHINE|MachineID=14|Name=Furnace A3|Type=Furnace|Loc=Zone 3|Status=Active',
 '2025-11-27 20:37:01'),

(13,NULL,'8f86f1e7e4ae0867d10da58c3dea21d15629a98f54c4a27ebe734bfdcc23237d',
 'a38efcff51a59155db0ba25704803b9f157ba0b4ac2b9960b7a505c3b5fb4f1f',
 'ADD_MACHINE|MachineID=15|Name=Furnace A3|Type=Furnace|Loc=Zone 3|Status=Active',
 '2025-11-27 20:46:59'),

(14,NULL,'457cb9e76e84fe153596509ce36052c4602e026324adbf03513b588d61a8bc89',
 '8f86f1e7e4ae0867d10da58c3dea21d15629a98f54c4a27ebe734bfdcc23237d',
 'DELETE_MACHINE|MachineID=15|By=admin',
 '2025-11-27 20:47:03'),

(15,2,'90d0081039248388b1559d543acb9b1c74069e1325e96f4aa7bd148840bfbc13',
 '457cb9e76e84fe153596509ce36052c4602e026324adbf03513b588d61a8bc89',
 'MODIFY_PERFORMANCE|PerformanceID=2|NewOperatingTime=6.0|NewDowntime=2.0|NewActualOutput=967|NewIdealOutput=1000|NewGoodUnits=589|NewTotalUnits=600|NewOEE=71.195',
 '2025-11-27 23:21:11'),

(16,6,'63616c56cb0184c5d8fdde66d9eff2dda4c05ed4f4d89fca9a2079728e72020a',
 '90d0081039248388b1559d543acb9b1c74069e1325e96f4aa7bd148840bfbc13',
 'MODIFY_PERFORMANCE|PerformanceID=6|NewOperatingTime=4.0|NewDowntime=1.0|NewActualOutput=585|NewIdealOutput=600|NewGoodUnits=489|NewTotalUnits=500|NewOEE=76.284',
 '2025-11-27 23:21:45'),

(17,7,'90b1ffc6399a915f85b7c3316836f76fc7734d0f160528d433f59f0dfcec8cf0',
 '63616c56cb0184c5d8fdde66d9eff2dda4c05ed4f4d89fca9a2079728e72020a',
 'MODIFY_PERFORMANCE|PerformanceID=7|NewOperatingTime=5.5|NewDowntime=5.0|NewActualOutput=954|NewIdealOutput=960|NewGoodUnits=945|NewTotalUnits=960|NewOEE=51.24',
 '2025-11-27 23:22:40');
