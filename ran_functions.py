import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import classes
from ftplib import FTP
from io import BytesIO,StringIO

neList = classes.ranControllers()

def populateLteGraphs(pointer, startTime, lteBandList, volteCssrNetworkWideGraph, cssrNetworkWideGraph, volteDcrNetworkWideGraph, dcrNetworkWideGraph):
    startTimeNetworkWide = (datetime.now()-timedelta(days=startTime)).strftime("%Y-%m-%d")
    for band in lteBandList:
        pointer.execute('SELECT time,erabssr,dcr FROM ran_pf_data.ran_report_4g_report_network_wide where ltecellgroup = \'' + band + '\' and time > \'' + str(startTimeNetworkWide) + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        lteDataDataframe = pd.DataFrame(queryPayload, columns=['time', 'erabssr', 'dcr'])
        # Add dataframe data to figure object
        cssrNetworkWideGraph.add_trace(go.Scatter(x=lteDataDataframe['time'], y=lteDataDataframe['erabssr'], name=band))
        dcrNetworkWideGraph.add_trace(go.Scatter(x=lteDataDataframe['time'], y=lteDataDataframe['dcr'], name=band))
        queryRaw.clear()
        # Since there's no VoLTE on B42, we must skip it from the VolTE graphs
        if band != 'Network Band=42':
            pointer.execute('SELECT time,volteerabssr,voltedcr FROM ran_pf_data.ran_report_4g_report_network_wide where ltecellgroup = \'' + band + '\' and time > \'' + str(startTimeNetworkWide) + '\';')
            queryRaw = pointer.fetchall()
            queryPayload = np.array(queryRaw)
            # Transform the query payload into a dataframe
            wttxDataDataframe = pd.DataFrame(queryPayload, columns=['time', 'volteerabssr', 'voltedcr'])
            volteCssrNetworkWideGraph.add_trace(go.Scatter(x=wttxDataDataframe['time'], y=wttxDataDataframe['volteerabssr'], name=band))
            volteDcrNetworkWideGraph.add_trace(go.Scatter(x=wttxDataDataframe['time'], y=wttxDataDataframe['voltedcr'], name=band))
            queryRaw.clear()
        queryRaw.clear()
    return volteCssrNetworkWideGraph, cssrNetworkWideGraph, volteDcrNetworkWideGraph, dcrNetworkWideGraph

def populateUmtsGraphs(pointer, startTime, rncNameList, umtsCssrNetworkWideGraph, hsdpaCssrNetworkWideGraph, hsupaCssrNetworkWideGraph, umtsDcrNetworkWideGraph, hsdpaDcrNetworkWideGraph, hsupaDcrNetworkWideGraph):
    startTimeNetworkWide = (datetime.now()-timedelta(days=startTime)).strftime("%Y-%m-%d")
    for rnc in rncNameList:
        pointer.execute('SELECT time,hsdpadcr,hsupadcr,csdcr,hsdpacssr,hsupacssr,cscssr FROM ran_pf_data.ran_report_3g_report_network_wide where rncname = \'' + rnc + '\' and time > \'' + str(startTimeNetworkWide) + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        umtsDataDataframe = pd.DataFrame(queryPayload, columns=['time', 'hsdpadcr', 'hsupadcr', 'csdcr', 'hsdpacssr', 'hsupacssr', 'cscssr'])
        hsdpaCssrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['hsdpacssr'], name=rnc))
        hsupaCssrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['hsupacssr'], name=rnc))
        umtsCssrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['cscssr'], name=rnc))
        hsdpaDcrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['hsdpadcr'], name=rnc))
        hsupaDcrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['hsupadcr'], name=rnc))
        umtsDcrNetworkWideGraph.add_trace(go.Scatter(x=umtsDataDataframe['time'], y=umtsDataDataframe['csdcr'], name=rnc))
        queryRaw.clear()
    return umtsCssrNetworkWideGraph, hsdpaCssrNetworkWideGraph, hsupaCssrNetworkWideGraph, umtsDcrNetworkWideGraph, hsdpaDcrNetworkWideGraph, hsupaDcrNetworkWideGraph

def populateGsmGraphs(pointer, startTime, bscNameList, gsmCsCssrNetworkWideGraph, gsmPsCssrNetworkWideGraph, gsmCsDcrNetworkWideGraph):
    startTimeNetworkWide = (datetime.now()-timedelta(days=startTime)).strftime("%Y-%m-%d")
    for bsc in bscNameList:
        pointer.execute('SELECT time,cscssr,csdcr,pscssr FROM ran_pf_data.ran_report_2g_report_network_wide where gbsc = \'' + bsc + '\' and time > \'' + str(startTimeNetworkWide) + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        gsmDataDataframe = pd.DataFrame(queryPayload, columns=['time', 'cscssr', 'csdcr', 'pscssr'])
        gsmCsCssrNetworkWideGraph.add_trace(go.Scatter(x=gsmDataDataframe['time'], y=gsmDataDataframe['cscssr'], name=bsc))
        gsmPsCssrNetworkWideGraph.add_trace(go.Scatter(x=gsmDataDataframe['time'], y=gsmDataDataframe['pscssr'], name=bsc))
        gsmCsDcrNetworkWideGraph.add_trace(go.Scatter(x=gsmDataDataframe['time'], y=gsmDataDataframe['csdcr'], name=bsc))
        queryRaw.clear()
    return gsmCsCssrNetworkWideGraph, gsmPsCssrNetworkWideGraph, gsmCsDcrNetworkWideGraph

def bscHighRefreshQuery(pointer, startTime, bscHighRefresh, bscNameList, gsmGraphValueConversionDict, dataTypeDropdown):
    for bsc in bscNameList:
        pointer.execute('SELECT ' + gsmGraphValueConversionDict[dataTypeDropdown] + ', lastupdate FROM ran_pf_data.bsc_performance_data where nename = \'' + bsc + '\' and lastupdate >= \'' + startTime + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        df = pd.DataFrame({dataTypeDropdown:queryPayload[:,0], 'Time':queryPayload[:,1]})
        # Add trace to the plot
        bscHighRefresh.add_trace(go.Scatter(x=df["Time"], y=df[dataTypeDropdown], name=bsc))
        queryRaw.clear()
    return bscHighRefresh

def rncHighRefreshQuery(pointer, startTime, rncHighRefresh, rncNameList, umtsGraphValueConversionDict, dataTypeDropdown):
    for rnc in rncNameList:
        pointer.execute('SELECT ' + umtsGraphValueConversionDict[dataTypeDropdown] + ', lastupdate FROM ran_pf_data.rnc_performance_data where nename = \'' + rnc + '\' and lastupdate >= \'' + startTime + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        df = pd.DataFrame({ dataTypeDropdown:queryPayload[:,0], 'Time':queryPayload[:,1] })
        rncHighRefresh.add_trace(go.Scatter(x=df["Time"], y=df[dataTypeDropdown], name=rnc))
        queryRaw.clear()
    return rncHighRefresh

def neOosGraph(pointer, startTime, neOosLineChart, hiddenNeOosLineChartDatatableValue):
    # Query NE Current Alarms information from DB
    pointer.execute('select locationinformation from datatable_data.networkcurrentalarms where alarmname = \'NE Is Disconnected\' and created_at > \'' + startTime + '\';')
    queryRaw = pointer.fetchall()
    queryPayload = np.array(queryRaw)
    # Create pie chart dataframe
    neOosDataframe = pd.DataFrame(queryPayload, columns=['locationinformation'])
    # Temporal list to store ne oos reasons quantity
    tmpList = []
    neOosListDataTableData = []
    for i in range(len(neOosDataframe['locationinformation'])):
        # Filter NE Name from data
        neNameStartIndex = neOosDataframe['locationinformation'][i].find('neName=') + 7
        neNameEndIndex = neOosDataframe['locationinformation'][i].find(',', neNameStartIndex)
        neName = neOosDataframe['locationinformation'][i][neNameStartIndex:neNameEndIndex]
        # If the name does NOT contain P or U, then...
        if 'P' not in neName and 'U' not in neName:
            # Filter NE OOS Reason from data
            startIndex = neOosDataframe['locationinformation'][i].find('Error message=') + 14
            endIndex = neOosDataframe['locationinformation'][i].find(',', startIndex)
            neOosDataframe['locationinformation'][i] = neOosDataframe['locationinformation'][i][startIndex:endIndex]
            # Append data to datatable value list
            neOosListDataTableData.append({'NE':neName, 'Reason':neOosDataframe['locationinformation'][i]})
            # Append reason quantity (so we can construct pie chart later on)
            tmpList.append(1)
        else:
            # Drop row from DF
            neOosDataframe = neOosDataframe.drop([i], axis=0)
    neOosDataframe['count'] = tmpList
    # Append current data to NE OOS line chart
    hiddenNeOosLineChartDatatableValue.append({'time':datetime.now().strftime("%Y/%m/%d %H:%M:%S"), 'counter':len(tmpList)})
    # Construct temporary dataframe to pass parameters to plot
    tmpDataFrame = pd.DataFrame(hiddenNeOosLineChartDatatableValue)
    neOosDataframe = neOosDataframe.groupby('locationinformation').count().reset_index()
    pieChartGraph = px.pie(neOosDataframe, values='count', names='locationinformation')
    neOosLineChart.add_trace(go.Scatter(x=tmpDataFrame['time'], y=tmpDataFrame['counter'], name=''))
    return pieChartGraph, neOosLineChart, hiddenNeOosLineChartDatatableValue, neOosListDataTableData

def graphInsightQuery(currentGraph, startTime, selectedKPI, pointer, selectedGroup, graphInsightValueDict):
    startTimeNetworkWide = (datetime.now()-timedelta(days=startTime)).strftime("%Y-%m-%d")
    kpiDict = {'LTE Data CSSR':'erabssr', 'LTE Data DCR': 'dcr', 'VoLTE CSSR': 'volteerabssr', 'VoLTE DCR': 'voltedcr', 'GSM CS CSSR': 'cscssr', 'GSM PS CSSR': 'pscssr', 'GSM CS DCR': 'csdcr', 'UMTS CSSR': 'cscssr', 'UMTS DCR': 'csdcr', 'HSDPA CSSR': 'hsdpacssr', 'HSDPA DCR': 'hsdpadcr', 'HSUPA CSSR': 'hsupacssr', 'HSUPA DCR': 'hsupadcr'}
    kpiSpecificDict = {'LTE Data CSSR':'dataerabssr', 'LTE Data DCR': 'datadcr', 'VoLTE CSSR': 'volteerabssr', 'VoLTE DCR': 'voltedcr', 'GSM CS CSSR': 'cscssr', 'GSM PS CSSR': 'pscssr', 'GSM CS DCR': 'csdcr', 'UMTS CSSR': 'cscssr', 'UMTS DCR': 'csdcr', 'HSDPA CSSR': 'hsdpacssr', 'HSDPA DCR': 'hsdpadcr', 'HSUPA CSSR': 'hsupacssr', 'HSUPA DCR': 'hsupadcr'}
    networkWidetable = ''
    topTable = ''
    condition = ''
    order = ''
    currentList = ''
    delta = 0
    if 'LTE' in selectedKPI or 'VoLTE' in selectedKPI:
        if selectedGroup == 'All':
            currentList = neList.lteBandList
        else:
            currentList = [selectedGroup]
        networkWidetable = 'ran_report_4g_report_network_wide'
        topTable = 'ran_report_4g_report_specific'
        condition = 'ltecellgroup = \''
    elif 'UMTS' in selectedKPI or 'HSDPA' in selectedKPI or 'HSUPA' in selectedKPI:
        if selectedGroup == 'All':
            currentList = neList.rncNameList
        else:
            currentList = [selectedGroup]
        networkWidetable = 'ran_report_3g_report_network_wide'
        topTable = 'ran_report_3g_report_specific'
        condition = 'rncname = \''
    elif 'GSM' in selectedKPI:
        if selectedGroup == 'All':
            currentList = neList.bscNameList
        else:
            currentList = [selectedGroup]
        networkWidetable = 'ran_report_2g_report_network_wide'
        topTable = 'ran_report_2g_report_specific'
        condition = 'gbsc = \''
    else:
        return currentGraph, graphInsightValueDict

    if 'DCR' in selectedKPI:
        order = 'desc'
    elif 'CSSR' in selectedKPI:
        order = 'asc'
    else:
        return currentGraph, graphInsightValueDict
    # Query TOP cell names from DB
    pointer.execute('select b.time,b.cellname,b.' + kpiSpecificDict[selectedKPI] + ' from (select a.time,a.cellname,a.' + kpiSpecificDict[selectedKPI] + ',row_number() over (partition by a.time order by a.' + kpiSpecificDict[selectedKPI] + ' ' + order + ') as rn from ran_pf_data.' + topTable + ' a where a.time >= \'' + str(startTimeNetworkWide) + '\') b where b.rn = 1')
    queryRaw = pointer.fetchall()
    queryPayload = np.array(queryRaw)
    topWorstPerHourDataFrame = pd.DataFrame(queryPayload, columns=['time', 'cellname', kpiSpecificDict[selectedKPI]])
    queryRaw.clear()
    # Plot graph
    for ne in currentList:
        query = 'select time,' + kpiDict[selectedKPI] + ' from ran_pf_data.' + networkWidetable + ' where ' + condition + ne + '\' and time > \'' + str(startTimeNetworkWide) + '\';'
        pointer.execute(query)
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        DataDataframe = pd.DataFrame(queryPayload, columns=['time', kpiDict[selectedKPI]])
        currentGraph.add_trace(go.Scatter(x=DataDataframe['time'], y=DataDataframe[kpiDict[selectedKPI]], name=ne, text=topWorstPerHourDataFrame['cellname']))
        # If there's only 1 NE selected, then add graph average threshold
        if len(currentList) == 1:
            # If selected KPI is DCR, delta must be positive
            if '4g' in networkWidetable and 'DCR' in selectedKPI:
                delta = 1.2
            # If it's CSSR, delta must be negative. Delta value varies due to graph min & max peaks.
            if '4g' in networkWidetable and 'CSSR' in selectedKPI:
                delta = 0.999
            if '3g' in networkWidetable and 'DCR' in selectedKPI:
                delta = 1.2
            if '3g' in networkWidetable and 'CSSR' in selectedKPI:
                delta = 0.999
            if '2g' in networkWidetable and 'DCR' in selectedKPI:
                delta = 1.2
            if '2g' in networkWidetable and 'CSSR' in selectedKPI:
                delta = 0.999
            # Copy original dataframe
            avgBusyHourDataframe = DataDataframe.copy()
            # Transform time column to datetime type and set index
            avgBusyHourDataframe['time'] = pd.to_datetime(avgBusyHourDataframe['time'], format='%Y-%m-%d %H:%M:%S')
            avgBusyHourDataframe = avgBusyHourDataframe.set_index(pd.DatetimeIndex(avgBusyHourDataframe['time']))
            # Filter data in busy hour
            avgBusyHourDataframe = avgBusyHourDataframe.loc[avgBusyHourDataframe['time'].between_time('08:00:00', '20:00:00')]
            # Construct the average value list, needed to plot. We loop through DataDataframe to populate all time values, regardless of busy hour
            avgBusyHourList = [avgBusyHourDataframe[kpiDict[selectedKPI]].mean() for y in DataDataframe['time']]            
            deltaRangeList = [avgBusyHourDataframe[kpiDict[selectedKPI]].mean()*delta for y in DataDataframe['time']]
            currentGraph.add_trace(go.Scatter(x=DataDataframe['time'], y=deltaRangeList, name='Busy Hour Delta Range'))
            currentGraph.add_trace(go.Scatter(x=DataDataframe['time'], y=avgBusyHourList, name='Busy Hour Average'))
        queryRaw.clear()
    # Query current and week-ago data
    query = 'SELECT ' + kpiDict[selectedKPI] + ' FROM ran_pf_data.' + networkWidetable + ' where ' + condition + ne + '\' and time > date_sub(current_timestamp(), interval 171 hour) order by time desc;'
    pointer.execute(query)
    queryRaw = pointer.fetchall()
    graphInsightValueDict['Parameter'] = selectedKPI
    graphInsightValueDict['Last Week'] = float(queryRaw[-1][0])
    graphInsightValueDict['Current'] = float(queryRaw[0][0])
    graphInsightValueDict['Delta'] = graphInsightValueDict['Current'] - graphInsightValueDict['Last Week']
    return currentGraph, graphInsightValueDict

def queryTxData(pointer, startTime, bscNameList, rncNameList, umtsNetworkPacketLossGraph, umtsNetworkDelayGraph, gsmNetworkPacketLossGraph, gsmNetworkDelayGraph):
    startTimeNetworkWide = (datetime.now()-timedelta(days=startTime)).strftime("%Y-%m-%d")
    for rnc in rncNameList:
        pointer.execute('SELECT date,delay,lost FROM ran_pf_data.rnc_packetloss_data where rncname = \'' + rnc + '\' and date > \'' + str(startTimeNetworkWide) + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        umtsDataDataframe = pd.DataFrame(queryPayload, columns=['date', 'delay', 'lost'])
        umtsNetworkPacketLossGraph.add_trace(go.Scatter(x=umtsDataDataframe['date'], y=umtsDataDataframe['lost'], name=rnc))
        umtsNetworkDelayGraph.add_trace(go.Scatter(x=umtsDataDataframe['date'], y=umtsDataDataframe['delay'], name=rnc))
        queryRaw.clear()
    for bsc in bscNameList:
        pointer.execute('SELECT date,delay,lost FROM ran_pf_data.bsc_packetloss_data where bscname = \'' + bsc + '\' and date > \'' + str(startTimeNetworkWide) + '\';')
        queryRaw = pointer.fetchall()
        queryPayload = np.array(queryRaw)
        # Transform the query payload into a dataframe
        gsmDataDataframe = pd.DataFrame(queryPayload, columns=['date', 'delay', 'lost'])
        gsmNetworkPacketLossGraph.add_trace(go.Scatter(x=gsmDataDataframe['date'], y=gsmDataDataframe['lost'], name=bsc))
        gsmNetworkDelayGraph.add_trace(go.Scatter(x=gsmDataDataframe['date'], y=gsmDataDataframe['delay'], name=bsc))
        queryRaw.clear()
    return umtsNetworkPacketLossGraph, umtsNetworkDelayGraph, gsmNetworkPacketLossGraph, gsmNetworkDelayGraph

def queryTopRecords(pointer, dataTableColumns, dbTable):
    dataTableData = []
    # Check if db table content
    pointer.execute('SELECT * FROM datatable_data.' + dbTable + ';')
    # If it's not empty, the append to the datatable content
    queryRaw = pointer.fetchall()
    if queryRaw:
        tempDict = {}
        # Loop the column headers list
        for i in range(len(queryRaw)):
            # Loop the db content list
            for y in range(len(dataTableColumns)):
                # Populate the entry's dictionary
                tempDict[dataTableColumns[y]['id']] = queryRaw[i][y]
            # Append that dictionary to the list
            dataTableData.append(tempDict)
            tempDict = {}
    # If the query content is empty, append an empty line to data
    else:
        dataTableData.append({'': ''})
    return dataTableData

def insertDataTable(pointer, connectr, dbTable, dataTableData):
    # First, we must query the column names from the table
    pointer.execute('SELECT * FROM datatable_data.' + dbTable + ';')
    # Description method of pointer return a tuple of tuples, containing the column name on positon 0 on each tuple
    columnNames = [column[0] for column in pointer.description]
    # Clean up the entire table
    pointer.execute('DELETE FROM datatable_data.' + dbTable + ';')
    # Now, we must construct the REPLACE query
    query = 'REPLACE INTO `datatable_data`.`' + dbTable + '` ('
    for i in range(len(columnNames)-1):
        query += '`' + str(columnNames[i]) + '`'
        # Add , to separate column names in query
        if i < len(columnNames)-2:
            query += ', '
    query += ') VALUES ('
    # Create temporary list with datatable data values
    tempList = []
    try:
        # We must always delete the key '' in case the datatable comes with an empty value
        dataTableData[0].pop('')
    except:
        pass
    #print(dataTableData[0])
    for i in range(len(dataTableData)):
        tempList.append([v for v in dataTableData[i].values()])
    for i in range(len(tempList)):
        for y in range(len(columnNames)-1):
            query += '\'' + str(tempList[i][y]) + '\''
            # Separate values by coma
            if y < len(columnNames)-2:
                query += ', '
        query += ")"
        # Separate groups of values by coma
        if i < len(dataTableData)-1:
            query += ', ('
    # Close query
    query += ";"
    pointer.execute(query)
    connectr.commit()

def getFtpPathFileList(ftpLogin, filePath):
    fileName = ""
    # Instantiate FTP connection
    ftp = FTP(host=ftpLogin.hostname)
    ftp.login(user=ftpLogin.username, passwd=ftpLogin.password)
    # Move to desired path
    ftp.cwd(filePath)
    fileName = ftp.nlst()
    return fileName

def downloadFtpFile(ftpLogin, filePath, fileName):
    # Instantiate FTP connection
    ftp = FTP(host=ftpLogin.hostname)
    ftp.login(user=ftpLogin.username, passwd=ftpLogin.password)
    # Move to desired path
    ftp.cwd(filePath)
    # Instantiate a BytesIO object to temp store the xlsx file from the FTP server
    b = BytesIO()
    # Return file as binary with retrbinary functon. Must send according RETR command as part of FTP protocol
    ftp.retrbinary('RETR ' + fileName, b.write)
    # Open as Dataframe
    b
    ftp.quit()
    return b

# Takes ftpLogin object, filepath and file name and returns file content in memory
def downloadFtpFileString(ftpLogin, filePath, fileName):
    # Instantiate FTP connection
    ftp = FTP(host=ftpLogin.hostname)
    ftp.login(user=ftpLogin.username, passwd=ftpLogin.password)
    # Move to desired path
    ftp.cwd(filePath)
    # Instantiate a StringIO object to temp store the file from the FTP server
    s = StringIO()
    # Return file as string with retrlines functon. Must send according RETR command as part of FTP protocol
    ftp.retrlines('RETR ' + fileName, s.write)
    # Open as Dataframe
    ftp.quit()
    return s

# Function to query Network Map Data
def networkMapFunction(mysqlPointer, bscList, rncList, lteList, gateOneDropdown, gateTwoDropdown):
    whereStatement = ''
    tempCounter = 0
    # If list contains all BSC & N/A, then there is no WHERE clause on query
    if bscList:
        whereStatement += ' WHERE ('
        for bsc in bscList:
            whereStatement += ' bsc = \'' + bsc + '\''
            tempCounter += 1
            # If counter is less than len(bscList), append OR to query
            if tempCounter < len(bscList):
                whereStatement += ' OR '
            # Else, we're finished
            else:
                whereStatement += ')'
    else:
        pass
    tempCounter = 0
    # If list contains all RNC, then there is no WHERE clause on query
    if rncList:
        # Check if there's something already on whereStatement and there's at least 1 RNC selected
        if whereStatement == '' and rncList:
            whereStatement += ' WHERE ('
        # Check if there's something on rncList
        elif rncList:
            whereStatement += ' ' + gateOneDropdown + ' ('
        else:
            pass
        for rnc in rncList:
            whereStatement += ' rnc = \'' + rnc + '\''
            tempCounter += 1
            # If counter is less than len(bscList), append OR to query
            if tempCounter < len(rncList):
                whereStatement += ' OR '
            # Else, we're finished
            else:
                whereStatement += ')'
    else:
        pass
    # Let's work with Band list now
    tempCounter = 0
    if lteList:
        if whereStatement == '' and lteList:
            whereStatement += ' WHERE ('
        # Check if there's something on rncList OR bscList
        elif rncList or bscList:
            whereStatement += ' ' + gateTwoDropdown + ' ('
        else:
            pass
        for band in lteList:
            whereStatement += ' ' + band + ' != \'N/A\''
            tempCounter += 1
            # If counter is less than len(lteList), append OR to query
            if tempCounter < len(lteList):
                whereStatement += ' OR '
            # Else, we're finished
            else:
                whereStatement += ')'
    else:
        pass
    mysqlPointer.execute('SELECT site,lat,lon,bsc,rnc,provincia,AWS,WTTX,L850,L900,L1900 FROM alticedr_sitedb.raningdata' + whereStatement + ';')
    queryRaw = mysqlPointer.fetchall()
    if queryRaw:
        queryPayload = np.array(queryRaw)
        siteDataframe = pd.DataFrame(queryPayload, columns=['site', 'lat', 'lon', 'bsc', 'rnc', 'provincia', 'AWS', 'WTTX', 'L850', 'L900', 'L1900'])
        # Cast columns to float type
        siteDataframe['lat'] = siteDataframe['lat'].astype(float)
        siteDataframe['lon'] = siteDataframe['lon'].astype(float)
        # Add a column with fixed value 1
        bscPieDataframe = pd.DataFrame()
        bscPieDataframe['bsc'] = siteDataframe['bsc']
        bscPieDataframe['site_count'] = 1
        bscPieDataframe = bscPieDataframe.groupby('bsc').count().reset_index()
        rncPieDataframe = pd.DataFrame()
        rncPieDataframe['rnc'] = siteDataframe['rnc']
        rncPieDataframe['site_count'] = 1
        rncPieDataframe = rncPieDataframe.groupby('rnc').count().reset_index()
        ltePieDataframe = pd.DataFrame()
        ltePieDataframe['band'] = lteList
        ltePieDataframe['site_count'] = 0
        for n in range(len(siteDataframe['site'])):
            for z in range(len(lteList)):
                if siteDataframe[lteList[z]][n] != 'N/A':
                    ltePieDataframe['site_count'][z] += 1
        bscPieChart = px.pie(bscPieDataframe, values='site_count', names='bsc')
        rncPieChart = px.pie(rncPieDataframe, values='site_count', names='rnc')
        ltePieChart = px.pie(ltePieDataframe, values='site_count', names='band')
        return siteDataframe, bscPieChart, rncPieChart, ltePieChart
    # In case the data fetched is empty, return an empty map
    else:
        queryPayload = []
        siteDataframe = pd.DataFrame(queryPayload, columns=['site', 'lat', 'lon', 'bsc', 'rnc', 'provincia'])
        bscPieChart = px.pie()
        rncPieChart = px.pie()
        ltePieChart = px.pie()
        return siteDataframe, bscPieChart, rncPieChart, ltePieChart