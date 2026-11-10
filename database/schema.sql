-- ==========================================================
-- AquaMitra: Digital Fishery Pond Management & Decision-Support System
-- Target Database: Microsoft SQL Server (T-SQL)
-- Database Name: AquaMitraDB
-- ==========================================================

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AquaMitraDB')
BEGIN
    CREATE DATABASE AquaMitraDB;
END;
GO

USE AquaMitraDB;
GO

-- 1. Species Master Table
IF OBJECT_ID('dbo.Species', 'U') IS NULL
CREATE TABLE dbo.Species (
    SpeciesID INT IDENTITY(1,1) PRIMARY KEY,
    CommonName NVARCHAR(50) NOT NULL UNIQUE,
    ScientificName NVARCHAR(100) NULL,
    DefaultFeedingRate DECIMAL(4,2) DEFAULT 3.00, -- Default feeding percentage (e.g. 3.00%)
    OptimalTempMin DECIMAL(4,1) NULL,
    OptimalTempMax DECIMAL(4,1) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 2. Users / Farm Managers
IF OBJECT_ID('dbo.Users', 'U') IS NULL
CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL UNIQUE,
    FullName NVARCHAR(100) NOT NULL,
    ContactPhone NVARCHAR(20) NULL,
    Role NVARCHAR(30) DEFAULT 'Farmer',
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 3. Ponds Master Table
IF OBJECT_ID('dbo.Ponds', 'U') IS NULL
CREATE TABLE dbo.Ponds (
    PondID VARCHAR(20) PRIMARY KEY, -- e.g., 'P-001'
    PondName NVARCHAR(100) NOT NULL,
    Location NVARCHAR(150) NOT NULL,
    Area DECIMAL(10,2) NOT NULL CHECK (Area > 0),
    AreaUnit NVARCHAR(20) DEFAULT 'Acres', -- 'Acres', 'Hectares', 'Sq Meters'
    WaterSource NVARCHAR(50) NOT NULL,    -- 'Borewell', 'Canal', 'Rainfed', 'River'
    PondType NVARCHAR(50) DEFAULT 'Earthen', -- 'Earthen', 'Lined', 'Biofloc', 'Nursery'
    OwnerID INT NULL FOREIGN KEY REFERENCES dbo.Users(UserID),
    OwnerName NVARCHAR(100) NULL,
    Status NVARCHAR(30) DEFAULT 'Active', -- 'Active', 'Inactive', 'Under Maintenance'
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME(),
    UpdatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 4. Water Quality Reference Ranges
IF OBJECT_ID('dbo.ReferenceRanges', 'U') IS NULL
CREATE TABLE dbo.ReferenceRanges (
    RangeID INT IDENTITY(1,1) PRIMARY KEY,
    Parameter NVARCHAR(50) NOT NULL,       -- 'pH', 'Temperature', 'DissolvedOxygen', 'Turbidity', 'Ammonia', 'WaterLevel'
    LowerValue DECIMAL(8,3) NULL,
    UpperValue DECIMAL(8,3) NULL,
    Unit NVARCHAR(20) NOT NULL,            -- 'pH', '°C', 'mg/L', 'NTU', 'ppm', 'meters'
    SpeciesID INT NULL FOREIGN KEY REFERENCES dbo.Species(SpeciesID),
    Source NVARCHAR(150) DEFAULT 'Standard Aquaculture Guidelines',
    Active BIT DEFAULT 1,
    UpdatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 5. Fish Stocking Records
IF OBJECT_ID('dbo.FishStock', 'U') IS NULL
CREATE TABLE dbo.FishStock (
    StockID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    SpeciesID INT NULL FOREIGN KEY REFERENCES dbo.Species(SpeciesID),
    Species NVARCHAR(50) NULL,
    Variety NVARCHAR(100) NULL,
    StockingDate DATE NOT NULL,
    NumberOfFish INT NOT NULL CHECK (NumberOfFish > 0),
    AvgInitialWeightGrams DECIMAL(10,2) NOT NULL CHECK (AvgInitialWeightGrams > 0),
    TotalInitialBiomassKg DECIMAL(10,2) NULL,
    SourceHatchery NVARCHAR(100) NULL,
    BatchNumber NVARCHAR(50) NULL,
    SizeCategory NVARCHAR(50) NULL,
    PricePerFish DECIMAL(10,2) NULL,
    TotalSeedCost DECIMAL(12,2) NULL,
    TransportCost DECIMAL(10,2) NULL,
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- Idempotent schema upgrades for existing FishStock instances
IF COL_LENGTH('dbo.FishStock', 'Species') IS NULL ALTER TABLE dbo.FishStock ADD Species NVARCHAR(50) NULL;
IF COL_LENGTH('dbo.FishStock', 'Variety') IS NULL ALTER TABLE dbo.FishStock ADD Variety NVARCHAR(100) NULL;
IF COL_LENGTH('dbo.FishStock', 'TotalInitialBiomassKg') IS NULL ALTER TABLE dbo.FishStock ADD TotalInitialBiomassKg DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.FishStock', 'BatchNumber') IS NULL ALTER TABLE dbo.FishStock ADD BatchNumber NVARCHAR(50) NULL;
IF COL_LENGTH('dbo.FishStock', 'SizeCategory') IS NULL ALTER TABLE dbo.FishStock ADD SizeCategory NVARCHAR(50) NULL;
IF COL_LENGTH('dbo.FishStock', 'PricePerFish') IS NULL ALTER TABLE dbo.FishStock ADD PricePerFish DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.FishStock', 'TotalSeedCost') IS NULL ALTER TABLE dbo.FishStock ADD TotalSeedCost DECIMAL(12,2) NULL;
IF COL_LENGTH('dbo.FishStock', 'TransportCost') IS NULL ALTER TABLE dbo.FishStock ADD TransportCost DECIMAL(10,2) NULL;

-- 6. Fish Growth Sampling Observations
IF OBJECT_ID('dbo.FishGrowth', 'U') IS NULL
CREATE TABLE dbo.FishGrowth (
    GrowthID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    Species NVARCHAR(50) NULL,
    ObservationDate DATE NOT NULL,
    SampleSize INT NOT NULL CHECK (SampleSize > 0),
    AvgFishWeightGrams DECIMAL(10,2) NOT NULL CHECK (AvgFishWeightGrams > 0),
    MinWeightGrams DECIMAL(10,2) NULL,
    MaxWeightGrams DECIMAL(10,2) NULL,
    EstimatedBiomassKg DECIMAL(10,2) NULL,
    SamplingMethod NVARCHAR(100) NULL,
    Observer NVARCHAR(100) NULL,
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- Idempotent schema upgrades for existing FishGrowth instances
IF COL_LENGTH('dbo.FishGrowth', 'Species') IS NULL ALTER TABLE dbo.FishGrowth ADD Species NVARCHAR(50) NULL;
IF COL_LENGTH('dbo.FishGrowth', 'MinWeightGrams') IS NULL ALTER TABLE dbo.FishGrowth ADD MinWeightGrams DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.FishGrowth', 'MaxWeightGrams') IS NULL ALTER TABLE dbo.FishGrowth ADD MaxWeightGrams DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.FishGrowth', 'EstimatedBiomassKg') IS NULL ALTER TABLE dbo.FishGrowth ADD EstimatedBiomassKg DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.FishGrowth', 'SamplingMethod') IS NULL ALTER TABLE dbo.FishGrowth ADD SamplingMethod NVARCHAR(100) NULL;
IF COL_LENGTH('dbo.FishGrowth', 'Observer') IS NULL ALTER TABLE dbo.FishGrowth ADD Observer NVARCHAR(100) NULL;

-- 7. Water Quality Observations
IF OBJECT_ID('dbo.WaterQuality', 'U') IS NULL
CREATE TABLE dbo.WaterQuality (
    ReadingID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    ReadingDate DATE NOT NULL,
    ReadingTime TIME NOT NULL,
    pH DECIMAL(4,2) NULL CHECK (pH BETWEEN 0.0 AND 14.0),
    TemperatureC DECIMAL(4,1) NULL,
    DissolvedOxygenMgL DECIMAL(5,2) NULL CHECK (DissolvedOxygenMgL >= 0),
    TurbidityNTU DECIMAL(6,2) NULL,
    AmmoniaMgL DECIMAL(5,3) NULL CHECK (AmmoniaMgL >= 0),
    WaterLevelMeters DECIMAL(4,2) NULL CHECK (WaterLevelMeters >= 0),
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 8. Feeding Logs
IF OBJECT_ID('dbo.Feeding', 'U') IS NULL
CREATE TABLE dbo.Feeding (
    FeedingID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    FeedingDate DATE NOT NULL,
    FeedType NVARCHAR(50) NOT NULL,
    FeedBrand NVARCHAR(100) NULL,
    BiomassKg DECIMAL(10,2) NOT NULL CHECK (BiomassKg >= 0),
    FeedingRatePercent DECIMAL(4,2) NOT NULL CHECK (FeedingRatePercent >= 0),
    NumberOfFeedings INT DEFAULT 2 CHECK (NumberOfFeedings > 0),
    RecommendedFeedKg DECIMAL(10,2) NOT NULL,
    ActualFeedKg DECIMAL(10,2) NOT NULL CHECK (ActualFeedKg >= 0),
    FeedCostPerKg DECIMAL(10,2) DEFAULT 0.0 CHECK (FeedCostPerKg >= 0),
    TotalFeedCost DECIMAL(10,2) NULL,
    FeedResponse NVARCHAR(50) NULL,
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- Idempotent schema upgrades for existing Feeding instances
IF COL_LENGTH('dbo.Feeding', 'FeedBrand') IS NULL ALTER TABLE dbo.Feeding ADD FeedBrand NVARCHAR(100) NULL;
IF COL_LENGTH('dbo.Feeding', 'TotalFeedCost') IS NULL ALTER TABLE dbo.Feeding ADD TotalFeedCost DECIMAL(10,2) NULL;
IF COL_LENGTH('dbo.Feeding', 'FeedResponse') IS NULL ALTER TABLE dbo.Feeding ADD FeedResponse NVARCHAR(50) NULL;

-- 9. Mortality Events
IF OBJECT_ID('dbo.MortalityEvents', 'U') IS NULL
CREATE TABLE dbo.MortalityEvents (
    IncidentID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    IncidentDate DATE NOT NULL,
    NumberOfDead INT NOT NULL CHECK (NumberOfDead >= 0),
    EstimatedMortalityPercent DECIMAL(5,2) NULL,
    ObservedBehaviour NVARCHAR(200) NULL,
    VisibleSymptoms NVARCHAR(200) NULL,
    WaterCondition NVARCHAR(100) NULL,
    Remarks NVARCHAR(MAX) NULL,
    PhotoPath NVARCHAR(255) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 10. Farm Expenses
IF OBJECT_ID('dbo.Expenses', 'U') IS NULL
CREATE TABLE dbo.Expenses (
    ExpenseID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    ExpenseDate DATE NOT NULL,
    Category NVARCHAR(50) NOT NULL, -- 'Fish Seed', 'Feed', 'Labour', 'Electricity', etc.
    Description NVARCHAR(200) NOT NULL,
    Quantity DECIMAL(10,2) NULL,
    Amount DECIMAL(12,2) NOT NULL CHECK (Amount >= 0),
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 11. Farm Sales / Revenue
IF OBJECT_ID('dbo.Sales', 'U') IS NULL
CREATE TABLE dbo.Sales (
    SaleID INT IDENTITY(1,1) PRIMARY KEY,
    PondID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE CASCADE,
    SaleDate DATE NOT NULL,
    QuantitySoldKg DECIMAL(10,2) NOT NULL CHECK (QuantitySoldKg > 0),
    PricePerKg DECIMAL(10,2) NOT NULL CHECK (PricePerKg >= 0),
    TotalRevenue DECIMAL(12,2) NOT NULL CHECK (TotalRevenue >= 0),
    BuyerMarket NVARCHAR(150) NULL,
    Notes NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 12. Centralized Decision-Support Alerts
IF OBJECT_ID('dbo.Alerts', 'U') IS NULL
CREATE TABLE dbo.Alerts (
    AlertID INT IDENTITY(1,1) PRIMARY KEY,
    Category NVARCHAR(50) NOT NULL, -- 'Water Quality', 'Growth', 'Mortality', 'Feeding', 'Weather', 'Finance'
    PondID VARCHAR(20) NULL FOREIGN KEY REFERENCES dbo.Ponds(PondID) ON DELETE SET NULL,
    Title NVARCHAR(150) NOT NULL,
    Reason NVARCHAR(MAX) NOT NULL,
    Severity NVARCHAR(20) NOT NULL CHECK (Severity IN ('INFO', 'WARNING', 'HIGH')),
    SuggestedAction NVARCHAR(MAX) NOT NULL,
    IsRead BIT DEFAULT 0,
    IsResolved BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME(),
    ResolvedAt DATETIME2 NULL
);

-- 13. Weather Cache
IF OBJECT_ID('dbo.WeatherRecords', 'U') IS NULL
CREATE TABLE dbo.WeatherRecords (
    WeatherID INT IDENTITY(1,1) PRIMARY KEY,
    Location NVARCHAR(100) NOT NULL,
    RecordDate DATE NOT NULL,
    TempMin DECIMAL(4,1) NULL,
    TempMax DECIMAL(4,1) NULL,
    HumidityPercent DECIMAL(4,1) NULL,
    RainfallMm DECIMAL(6,2) NULL,
    WindSpeedKmh DECIMAL(5,1) NULL,
    ForecastSummary NVARCHAR(250) NULL,
    IsDemoData BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- Optimized Non-Clustered Indexes
CREATE NONCLUSTERED INDEX IX_WaterQuality_Pond_Date ON dbo.WaterQuality(PondID, ReadingDate DESC);
CREATE NONCLUSTERED INDEX IX_Feeding_Pond_Date ON dbo.Feeding(PondID, FeedingDate DESC);
CREATE NONCLUSTERED INDEX IX_Mortality_Pond_Date ON dbo.MortalityEvents(PondID, IncidentDate DESC);
CREATE NONCLUSTERED INDEX IX_FishGrowth_Pond_Date ON dbo.FishGrowth(PondID, ObservationDate DESC);
CREATE NONCLUSTERED INDEX IX_Alerts_Unresolved ON dbo.Alerts(IsResolved, Severity);
CREATE NONCLUSTERED INDEX IX_Expenses_Pond_Category ON dbo.Expenses(PondID, Category);
CREATE NONCLUSTERED INDEX IX_Sales_Pond_Date ON dbo.Sales(PondID, SaleDate DESC);
GO

-- Seed Default Species
IF NOT EXISTS (SELECT 1 FROM dbo.Species WHERE CommonName = 'Rohu')
    INSERT INTO dbo.Species (CommonName, ScientificName, DefaultFeedingRate, OptimalTempMin, OptimalTempMax)
    VALUES ('Rohu', 'Labeo rohita', 3.0, 24.0, 32.0);

IF NOT EXISTS (SELECT 1 FROM dbo.Species WHERE CommonName = 'Catla')
    INSERT INTO dbo.Species (CommonName, ScientificName, DefaultFeedingRate, OptimalTempMin, OptimalTempMax)
    VALUES ('Catla', 'Gibelion catla', 3.2, 25.0, 32.0);

IF NOT EXISTS (SELECT 1 FROM dbo.Species WHERE CommonName = 'Mrigal')
    INSERT INTO dbo.Species (CommonName, ScientificName, DefaultFeedingRate, OptimalTempMin, OptimalTempMax)
    VALUES ('Mrigal', 'Cirrhinus mrigala', 2.8, 24.0, 31.0);

IF NOT EXISTS (SELECT 1 FROM dbo.Species WHERE CommonName = 'Tilapia')
    INSERT INTO dbo.Species (CommonName, ScientificName, DefaultFeedingRate, OptimalTempMin, OptimalTempMax)
    VALUES ('Tilapia', 'Oreochromis niloticus', 3.5, 26.0, 33.0);

IF NOT EXISTS (SELECT 1 FROM dbo.Species WHERE CommonName = 'Other')
    INSERT INTO dbo.Species (CommonName, ScientificName, DefaultFeedingRate, OptimalTempMin, OptimalTempMax)
    VALUES ('Other', 'Configurable Species', 3.0, 22.0, 32.0);

-- Seed Standard Reference Ranges (Configurable, labeled as baseline references)
IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'pH')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('pH', 6.5, 8.5, 'pH', 'Standard Freshwater Reference', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'DissolvedOxygen')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('DissolvedOxygen', 5.0, 10.0, 'mg/L', 'Standard Freshwater Reference', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'Temperature')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('Temperature', 24.0, 32.0, '°C', 'Standard Freshwater Reference', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'Turbidity')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('Turbidity', 20.0, 40.0, 'NTU', 'Standard Freshwater Reference', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'Ammonia')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('Ammonia', 0.0, 0.05, 'mg/L', 'Standard Freshwater Reference', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.ReferenceRanges WHERE Parameter = 'WaterLevel')
    INSERT INTO dbo.ReferenceRanges (Parameter, LowerValue, UpperValue, Unit, Source, Active)
    VALUES ('WaterLevel', 1.2, 2.0, 'meters', 'Standard Freshwater Reference', 1);
GO
