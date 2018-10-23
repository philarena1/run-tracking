import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib
import datetime

def format_health_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for neighbor in root.iter('HealthData'):
        for export_date in root.iter('ExportDate'):
            for me in root.iter('Me'):
                raw_list = []

                for record_type in root.iter('Record'):
                    raw_list.append(
                                record_type.attrib['device'] +',' +
                                record_type.attrib['sourceName'] + ',' +
                                record_type.attrib['sourceVersion']+ ',' +
                                record_type.attrib['type']+',' +
                                record_type.attrib['startDate']+',' +
                                record_type.attrib['endDate']+',' +
                                record_type.attrib['creationDate']+',' +
                                record_type.attrib['value']+',' +
                                record_type.attrib['unit']
                            )

    pd.options.display.float_format = '{:.2f}'.format #get rid of scientific notation

    df = pd.DataFrame([sub.split(",") for sub in raw_list], columns=['device','devicename','deviceManufacturer','deviceModel','deviceHardware','device2','deviceSoftware','sourceName','sourceVersion'
                                ,'type','startDate','endDate'
                                ,'creationDate','value','unit'])


    df['creationDate'] =  pd.to_datetime(df['creationDate'])-pd.Timedelta(hours=4)
    df['startDate'] =  pd.to_datetime(df['startDate'])-pd.Timedelta(hours=4)
    df['endDate'] =  pd.to_datetime(df['endDate'])-pd.Timedelta(hours=4)
    df['interval_seconds'] = (df['endDate'] - df['startDate']).astype('timedelta64[s]')
    df['interval_minutes'] = (df['interval_seconds'])/60
    df['value']= df['value'].astype('float')
    df['pace'] = df['value']/df['interval_minutes']
    df['day'] = (df['startDate']).dt.date
    return df

def get_running_distance(df, days_ago):
    run = df
    run = df[['pace', 'creationDate', 'value', 'day']][df['type'] == 'HKQuantityTypeIdentifierDistanceWalkingRunning']
    start_date_ago = datetime.datetime.now() + datetime.timedelta(-days_ago)
    prev_ = run.loc[run['day'] > start_date_ago.date()]
    prev_sum = prev_.groupby(['day'])['value'].sum()
    return prev_sum

df = format_health_data('export.xml')

run_df = get_running_distance(df,90)

