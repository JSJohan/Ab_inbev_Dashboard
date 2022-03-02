from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os
import json

class gtU():

    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.KEY_FILE_LOCATION = ''

    def runReport(self,cuenta, dateInit, dateEnd,keyJson):
        try:
            self.KEY_FILE_LOCATION = './src/' + keyJson
            respuesta = []
            response = self.get_report(self.initialize_analyticsreporting(), init = dateInit, end = dateEnd, VIEW_ID = cuenta)
            for row in response.get('reports', {})[0].get('data', {}).get('rows', {}):
                for dato in row.get('metrics', [])[0].get('values', {}):
                    respuesta.append(dato)
            return respuesta
        except Exception as e:
            return str(e)

    def initialize_analyticsreporting(self):
        """Initializes an Analytics Reporting API V4 service object.
        Returns:
        An authorized Analytics Reporting API V4 service object.
        """

        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.KEY_FILE_LOCATION, self.SCOPES)
        analytics = build('analyticsreporting', 'v4', credentials=credentials)
        return analytics

    def get_report(self, analytics,**kwargs):
        """Queries the Analytics Reporting API V4.
        Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        Returns:
        The Analytics Reporting API V4 response.
        """
        return analytics.reports().batchGet(
        body={
        'reportRequests': [{
                    'viewId': kwargs["VIEW_ID"],
                    'dateRanges': [{"startDate": kwargs["init"], "endDate": kwargs["end"]}],  
                    'metrics': [{"expression": "ga:users"},
                                {"expression": "ga:newusers"},
                                {"expression": "ga:sessions"},
                                {"expression": "ga:pageviews"},
                                {"expression": "ga:bounces"},
                                {"expression": "ga:timeOnPage"},
                                {"expression": "ga:avgSessionDuration"},
                                {"expression": "ga:bounceRate"}
                                ]
                        }]
                    }
                ).execute()

