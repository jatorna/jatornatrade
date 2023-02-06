import datetime as dt
from subprojects.types.Common import *


class SymbolsResources:
    BOLSAMANIA_SYMBOLS = {'Abengoa-A': 'ABG.MC', 'Abengoa-B': 'ABG-P.MC', 'Acciona': 'ANA.MC', 'Acerinox': 'ACX.MC',
                          'ACS': 'ACS.MC', 'Adolfo Dominguez': 'ADZ.MC', 'Aedas Home': 'AEDAS.MC',
                          'Aena': 'AENA.MC', 'Airbus': 'AIR.MC', 'Airtificial': 'AI.MC',
                          'Alantra Partners': 'ALNT.MC', 'Almirall': 'ALM.MC', 'Amadeus-A': 'AMS.MC',
                          'Amper': 'AMP.MC', 'Amrest': 'EAT.MC', 'Aperam': 'APAM.MC', 'Applus Services': 'APPS.MC',
                          'Arcelormittal': 'MTS.MC', 'Arima': 'ARM.MC', 'Atresmedia': 'A3M.MC',
                          'Audax Renovables': 'ADX.MC', 'Azkoyen': 'AZK.MC', 'Banco Santander': 'SAN.MC',
                          'Banco Sabadell': 'SAB.MC', 'Bankia': 'BKIA.MC', 'Bankinter': 'BKT.MC',
                          'Barón de Ley': 'BDL.MC', 'BBVA': 'BBVA.MC', 'Berkeley energía': 'BKY.MC',
                          'Biosearch': 'BIO.MC', 'BME': 'BME.MC', 'Bodegas Riojanas': 'RIO.MC', 'Borges': 'BAIN.MC',
                          'CAF': 'CAF.MC', 'Caixabank': 'CABK.MC', 'CAM': 'CAM.MC', 'Cellnex': 'CLNX.MC',
                          'Cevasa': 'CEV.MC', 'CIE Automotive': 'CIE.MC', 'Cleop': 'CLEO.MC',
                          'Clínica Baviera': 'CBAV.MC', 'Coca-Cola Eur. Part.': 'CLEO.MC', 'Codere': 'CDR.MC',
                          'Coemac': 'CMC.MC', 'Corp. Financiera Alba': 'ALB.MC', 'Deoleo': 'OLE.MC',
                          'DESA': 'DESA.MC', 'Dia': 'DIA.MC', 'Duro Felguera': 'MDF.MC',
                          'Ebro Foods': 'EBRO.MC', 'Edreams Odigeo': 'EDR.MC', 'Elecnor': 'ENO.MC',
                          'Enagas': 'ENG.MC', 'Ence Energía': 'ENC.MC', 'Endesa': 'ELE.MC', 'Ercros': 'ECR.MC',
                          'Euskaltel': 'EKT.MC', 'Faes Farma': 'FAE.MC', 'FCC': 'FCC.MC', 'Ferrovial': 'FER.MC',
                          'Fluidra': 'FDR.MC', 'GAM': 'GALQ.MC', 'Gestamp Automoción': 'GSJ.MC',
                          'Global Dominion': 'EZE.MC', 'Grenery Renovables': 'GRE.MC', 'Grifols-A': 'GRF.MC',
                          'Grifols-B': 'GRF-P.MC', 'Grupo Catalana Occidente': 'GCO.MC',
                          'Grupo Emp. San José': 'GSJ.MC', 'Grupo Ezentis': 'EZE.MC', 'IAG': 'IAG.MC',
                          'Iberdrola': 'IBE.MC', 'Iberpapel': 'IBG.MC', 'Inditex': 'ITX.MC', 'Indra-A': 'IDR.MC',
                          'Inmob. Colonial': 'COL.MC', 'Inmobiliaria Sur': 'ISUR.MC',
                          'Laboratiorios Rovi': 'ROVI.MC', 'Lar España': 'LRE.MC', 'Liberbank': 'LBK.MC',
                          'Lingotes Especiales': 'LGT.MC', 'Logista': 'LOG.MC', 'Mapfre': 'MAP.MC',
                          'Mediaset España': 'TL5.MC', 'MELIA HOTELS': 'MEL.MC', 'Merlin Prop.': 'MRL.MC',
                          'Metrovacesa': 'MVC.MC', 'Miquel y Costas': 'MCM.MC', 'Montebalito': 'MTB.MC',
                          'MásMóvil': 'MAS.MC', 'Naturgy': 'NTGY.MC', 'Naturhouse': 'NTH.MC',
                          'Neinor Homes': 'HOME.MC', 'Nextil': 'NXT.MC', 'NH Hotel Group': 'NHH.MC',
                          'Nicolas Correa': 'NEA.MC', 'Nyesa valores': 'NYE.MC', 'OHL': 'OHL.MC',
                          'Oryzon Genomics': 'ORY.MC', 'Pescanova': 'PVA.MC', 'PharmaMar': 'PHM.MC',
                          'Prim': 'PRM.MC', 'Prisa-A': 'PRS.MC', 'Prosegur': 'PSG.MC', 'Prosegur Cash': 'CASH.MC',
                          'Quabit Inmob.': 'QBT.MC', 'Realia Business': 'RLIA.MC', 'Red Eléctrica': 'REE.MC',
                          'Reno de Medici': 'RDM.MC', 'Renta 4 Banco': 'R4.MC', 'Renta Corporación': 'REN.MC',
                          'Repsol': 'REP.MC', 'Sacyr': 'SCYR.MC', 'Service Point': 'SPS.MC',
                          'Siemens Gamesa': 'SGRE.MC', 'Sniace': 'SNC.MC', 'Solaria Energía': 'SLR.MC',
                          'SOLTEC POWR BR-UNTY': 'SPK.MC', 'Tab. Reig Jofre': 'RJF.MC', 'Talgo': 'TLGO.MC',
                          'Telefónica': 'TEF.MC', 'Tubacex': 'TUB.MC', 'Tubos Reunidos': 'TRG.MC',
                          'Técnicas Reunidas': 'TRE.MC', 'Unicaja Banco': 'UNI.MC', 'Urbas Grupo Fin.': 'UBS.MC',
                          'Vidrala': 'VID.MC', 'Viscofan': 'VIS.MC', 'Vocento': 'VOC.MC', 'Vértice 360': 'VER.MC',
                          'Zardoya Otis': 'ZOT.MC'}

    MC_SYMBOLS = ['ABG.MC', 'ABG-P.MC', 'ANA.MC', 'ACX.MC', 'ACS.MC', 'ADZ.MC', 'AEDAS.MC', 'AENA.MC', 'AIR.MC',
                  'AI.MC', 'ALNT.MC', 'ALM.MC', 'AMS.MC', 'AMP.MC', 'EAT.MC', 'APAM.MC', 'APPS.MC', 'MTS.MC', 'ARM.MC',
                  'A3M.MC', 'ADX.MC', 'CAF.MC', 'AZK.MC', 'SAN.MC', 'SAB.MC', 'BKIA.MC', 'BKT.MC', 'BDL.MC', 'CBAV.MC',
                  'BBVA.MC', 'BKY.MC', 'BIO.MC', 'BME.MC', 'RIO.MC', 'BAIN.MC', 'CABK.MC', 'CAM.MC', 'CASH.MC',
                  'CCEP.MC', 'CLNX.MC', 'CEV.MC', 'CIE.MC', 'CLEO.MC', 'CDR.MC', 'CMC.MC', 'ALB.MC', 'DESA.MC',
                  'MDF.MC', 'OLE.MC', 'DIA.MC', 'DOM.MC', 'EBRO.MC', 'EDR.MC', 'ENO.MC', 'ENG.MC', 'ENC.MC', 'ELE.MC',
                  'ECR.MC', 'EKT.MC', 'EZE.MC', 'FAE.MC', 'FCC.MC', 'FER.MC', 'FDR.MC', 'GALQ.MC', 'GEST.MC', 'GCO.MC',
                  'GRE.MC', 'GRF.MC', 'GRF-P.MC', 'IAG.MC', 'IBE.MC', 'IBG.MC', 'ITX.MC', 'IDR.MC', 'COL.MC', 'ISUR.MC',
                  'LRE.MC', 'LBK.MC', 'LGT.MC', 'LOG.MC', 'MAP.MC', 'MAS.MC', 'TL5.MC', 'MEL.MC', 'MRL.MC', 'MVC.MC',
                  'MCM.MC', 'MTB.MC', 'NTGY.MC', 'NTH.MC', 'HOME.MC', 'NXT.MC', 'NHH.MC', 'NEA.MC', 'NYE.MC', 'OHL.MC',
                  'ORY.MC', 'PVA.MC', 'PHM.MC', 'PRM.MC', 'PRS.MC', 'PSG.MC', 'QBT.MC', 'REE.MC', 'RLIA.MC', 'RJF.MC',
                  'RDM.MC', 'RDM-Q.MC', 'R4.MC', 'REN.MC', 'REP.MC', 'ROVI.MC', 'SCYR.MC', 'GSJ.MC', 'SPS.MC',
                  'SGRE.MC', 'SNC.MC', 'SLR.MC', 'SPK.MC', 'TLGO.MC', 'TRE.MC', 'TEF.MC', 'TUB.MC', 'TRG.MC', 'UNI.MC',
                  'UBS.MC', 'VER.MC', 'VID.MC', 'VIS.MC', 'VOC.MC', 'ZOT.MC']

    DE_SYMBOLS = ['ADS.DE', 'ALV.DE', 'BAS.DE', 'BAY.DE', 'BEI.DE', 'BMW.DE', 'CON.DE', '1COV.DE', 'DAI.DE', 'DBK.DE',
                  'DB1.DE', 'LHA.DE', 'DPW.DE', 'DTE.DE', 'EOA.DE', 'FRE3.DE', 'FME.DE', 'HEI.DE', 'HEN3.DE', 'IFX.DE',
                  'LIN.DE', 'MRK.DE', 'MTX.DE', 'MUV2.DE', 'RWE.DE', 'SAP.DE', 'SIE.DE', 'VOW.DE', 'VNA.DE', 'WDI.DE']

    FX_SYMBOLS = ['EURUSD', 'EURGBP', 'EURCAD', 'AUDCAD', 'AUDJPY', 'EURJPY', 'USDGBP']

    CC_SYMBOLS = ['BTC-USD', 'ETH-USD']

    US_SYMBOLS = ['MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP', 'AES', 'AFL', 'A', 'APD', 'AKAM',
                  'ALK', 'ALB', 'ARE', 'ALXN', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR',
                  'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS',
                  'ANTM', 'AON', 'AOS', 'APA', 'AIV', 'AAPL', 'AMAT', 'APTV', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO',
                  'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'BKR', 'BLL', 'BAC', 'BK', 'BAX', 'BDX', 'BRK.B', 'BBY', 'BIO',
                  'BIIB', 'BLK', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX', 'BMY', 'AVGO', 'BR', 'BF.B', 'CHRW', 'COG', 'CDNS',
                  'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'CNC', 'CNP', 'CTL',
                  'CERN', 'CF', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG',
                  'CTXS', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CAG', 'CXO', 'COP', 'ED', 'STZ',
                  'COO', 'CPRT', 'GLW', 'CTVA', 'COST', 'COTY', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA',
                  'DE', 'DAL', 'XRAY', 'DVN', 'DXCM', 'FANG', 'DLR', 'DFS', 'DISCA', 'DISCK', 'DISH', 'DG', 'DLTR',
                  'D', 'DPZ', 'DOV', 'DOW', 'DTE', 'DUK', 'DRE', 'DD', 'DXC', 'ETFC', 'EMN', 'ETN', 'EBAY', 'ECL',
                  'EIX', 'EW', 'EA', 'EMR', 'ETR', 'EOG', 'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'EVRG', 'ES', 'RE', 'EXC',
                  'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FE', 'FRC', 'FISV',
                  'FLT', 'FLIR', 'FLS', 'FMC', 'F', 'FTNT', 'FTV', 'FBHS', 'FOXA', 'FOX', 'BEN', 'FCX', 'GPS', 'GRMN',
                  'IT', 'GD', 'GE', 'GIS', 'GM', 'GPC', 'GILD', 'GL', 'GPN', 'GS', 'GWW', 'HRB', 'HAL', 'HBI', 'HIG',
                  'HAS', 'HCA', 'PEAK', 'HSIC', 'HSY', 'HES', 'HPE', 'HLT', 'HFC', 'HOLX', 'HD', 'HON', 'HRL', 'HST',
                  'HWM', 'HPQ', 'HUM', 'HBAN', 'HII', 'IEX', 'IDXX', 'INFO', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC', 'ICE',
                  'IBM', 'IP', 'IPG', 'IFF', 'INTU', 'ISRG', 'IVZ', 'IPGP', 'IQV', 'IRM', 'JKHY', 'J', 'JBHT', 'SJM',
                  'JNJ', 'JCI', 'JPM', 'JNPR', 'KSU', 'K', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KHC',
                  'KR', 'LB', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LEG', 'LDOS', 'LEN', 'LLY', 'LNC', 'LIN', 'LYV', 'LKQ',
                  'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MKC',
                  'MXIM', 'MCD', 'MCK', 'MDT', 'MRK', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MHK', 'TAP',
                  'MDLZ', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'MYL', 'NDAQ', 'NOV', 'NTAP', 'NFLX', 'NWL', 'NEM',
                  'NWSA', 'NWS', 'NEE', 'NLSN', 'NKE', 'NI', 'NBL', 'NSC', 'NTRS', 'NOC', 'NLOK', 'NCLH', 'NRG', 'NUE',
                  'NVDA', 'NVR', 'ORLY', 'OXY', 'ODFL', 'OMC', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PH', 'PAYX',
                  'PAYC', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PKI', 'PRGO', 'PFE', 'PM', 'PSX', 'PNW', 'PXD', 'PNC', 'PPG',
                  'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 'PHM', 'PVH', 'QRVO', 'PWR', 'QCOM', 'DGX',
                  'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RHI', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL',
                  'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SEE', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SLG', 'SNA', 'SO',
                  'LUV', 'SWK', 'SBUX', 'STT', 'STE', 'SYK', 'SIVB', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO',
                  'TPR', 'TGT', 'TEL', 'FTI', 'TDY', 'TFX', 'TXN', 'TXT', 'TMO', 'TIF', 'TJX', 'TSCO', 'TT', 'TDG',
                  'TRV', 'TFC', 'TWTR', 'TYL', 'TSN', 'UDR', 'ULTA', 'USB', 'UAA', 'UA', 'UNP', 'UAL', 'UNH', 'UPS',
                  'URI', 'UHS', 'UNM', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VIAC', 'V', 'VNO',
                  'VMC', 'WRB', 'WAB', 'WMT', 'WBA', 'DIS', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WU',
                  'WRK', 'WY', 'WHR', 'WMB', 'WLTW', 'WYNN', 'XEL', 'XRX', 'XLNX', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZION',
                  'ZTS', 'GNUS', 'MARK', 'NNDM', 'SOLO', 'XSPA']


class MarketCalendar:
    MC_SCHEDULE = {'Open': dt.time(9, 0, 0),
                   'Close': dt.time(17, 30, 0)}
    DE_SCHEDULE = {'Open': dt.time(9, 0, 0),
                   'Close': dt.time(17, 30, 0)}

    FX_SCHEDULE = {'Open': dt.time(0, 0, 0),
                   'Close': dt.time(0, 0, 0)}

    CC_SCHEDULE = {'Open': dt.time(0, 0, 0),
                   'Close': dt.time(0, 0, 0)}

    US_SCHEDULE = {'Open': dt.time(15, 30, 0),
                   'Close': dt.time(22, 30, 0)}

    MARKET_SCHEDULE = {'MC': MC_SCHEDULE,
                       'DE': DE_SCHEDULE,
                       'FX': FX_SCHEDULE,
                       'CC': CC_SCHEDULE,
                       'US': US_SCHEDULE}


US_EXCHANGES = [Exchange.NYSE, Exchange.NASDAQ]
