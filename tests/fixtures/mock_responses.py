#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Mock HTTP Responses
Description: Realistic mock HTTP responses for external race websites.
             Used for testing web scraping functionality without external dependencies.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 14/03/2026
Version: 1.0.0
Python Version: 3.8+
License: [boazusa@hotmail.com]
===============================================================================
"""

class MockResponses:
    """Collection of mock HTTP responses for testing."""
    
    @staticmethod
    def get_3plus_participants_response():
        """Mock response for 3plus participants page."""
        return {
            'url': 'https://regi.3plus.co.il/events/page/17492',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'text': '''
            <!DOCTYPE html>
            <html dir="rtl" lang="he">
            <head>
                <meta charset="utf-8">
                <title>משתתפים - TEST Race</title>
            </head>
            <body>
                <div class="container">
                    <h1>רשימת משתתפים</h1>
                    <table id="m_ph4wp1_tblData" class="table table-striped">
                        <thead>
                            <tr>
                                <th>מקום</th>
                                <th>שם פרטי</th>
                                <th>שם משפחה</th>
                                <th>שנת לידה</th>
                                <th>מגדר</th>
                                <th>מקצה</th>
                                <th>קבוצה</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1</td>
                                <td>דני</td>
                                <td>כהן</td>
                                <td>1980</td>
                                <td>ז</td>
                                <td>10 ק"מ</td>
                                <td>מכבי תל אביב</td>
                            </tr>
                            <tr>
                                <td>2</td>
                                <td>משה</td>
                                <td>לוי</td>
                                <td>1975</td>
                                <td>ז</td>
                                <td>10 ק"מ</td>
                                <td>הפועל ירושלים</td>
                            </tr>
                            <tr>
                                <td>3</td>
                                <td>יוסי</td>
                                <td>ישראלי</td>
                                <td>1985</td>
                                <td>ז</td>
                                <td>5 ק"מ</td>
                                <td>בית"ר תל אביב</td>
                            </tr>
                            <tr>
                                <td>4</td>
                                <td>שרה</td>
                                <td>לוי</td>
                                <td>1982</td>
                                <td>נ</td>
                                <td>10 ק"מ</td>
                                <td>מכבי חיפה</td>
                            </tr>
                            <tr>
                                <td>5</td>
                                <td>רחל</td>
                                <td>כהן</td>
                                <td>1976</td>
                                <td>נ</td>
                                <td>21 ק"מ</td>
                                <td>הפועל תל אביב</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            '''
        }
    
    @staticmethod
    def get_realtiming_participants_response():
        """Mock response for realtiming participants page."""
        return {
            'url': 'https://www.realtiming.co.il/events/1242/list',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'text': '''
            <!DOCTYPE html>
            <html dir="rtl" lang="he">
            <head>
                <meta charset="utf-8">
                <title>תוצאות ריצה - Beit Shemesh Race</title>
            </head>
            <body>
                <div class="container">
                    <h1>רשימת משתתפים</h1>
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>מקום</th>
                                <th>מספר</th>
                                <th>שם פרטי</th>
                                <th>שם משפחה</th>
                                <th>שנת לידה</th>
                                <th>מגדר</th>
                                <th>מקצה</th>
                                <th>קבוצה</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1</td>
                                <td>101</td>
                                <td>דני</td>
                                <td>כהן</td>
                                <td>1980</td>
                                <td>ז</td>
                                <td>10 ק"מ</td>
                                <td>מכבי תל אביב</td>
                            </tr>
                            <tr>
                                <td>2</td>
                                <td>102</td>
                                <td>משה</td>
                                <td>לוי</td>
                                <td>1975</td>
                                <td>ז</td>
                                <td>10 ק"מ</td>
                                <td>הפועל ירושלים</td>
                            </tr>
                            <tr>
                                <td>3</td>
                                <td>103</td>
                                <td>שרה</td>
                                <td>לוי</td>
                                <td>1982</td>
                                <td>נ</td>
                                <td>10 ק"מ</td>
                                <td>מכבי חיפה</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            '''
        }
    
    @staticmethod
    def get_shvoong_search_results_response():
        """Mock response for shvoong search results page."""
        return {
            'url': 'https://raceresults.shvoong.co.il/race-result/?q=דני%20כהן',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'text': '''
            <!DOCTYPE html>
            <html dir="rtl" lang="he">
            <head>
                <meta charset="utf-8">
                <title>תוצאות ריצה - דני כהן</title>
            </head>
            <body>
                <div class="container">
                    <h1>תוצאות ריצה עבור דני כהן</h1>
                    <table class="race-results">
                        <thead>
                            <tr>
                                <th>תאריך</th>
                                <th>מקום</th>
                                <th>שם פרטי</th>
                                <th>שם משפחה</th>
                                <th>מקצה</th>
                                <th>תוצאה</th>
                                <th>זמן אישי</th>
                                <th>מיקום כללי</th>
                                <th>מיקום בקבוצה</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>15/02/2024</td>
                                <td>תל אביב</td>
                                <td>דני</td>
                                <td>כהן</td>
                                <td>10 ק"מ</td>
                                <td>00:44:15</td>
                                <td>00:44:15</td>
                                <td>12</td>
                                <td>2</td>
                            </tr>
                            <tr>
                                <td>01/03/2024</td>
                                <td>ירושלים</td>
                                <td>דני</td>
                                <td>כהן</td>
                                <td>10 ק"מ</td>
                                <td>00:45:30</td>
                                <td>00:44:15</td>
                                <td>15</td>
                                <td>3</td>
                            </tr>
                            <tr>
                                <td>20/04/2024</td>
                                <td>חיפה</td>
                                <td>דני</td>
                                <td>כהן</td>
                                <td>21 ק"מ</td>
                                <td>01:38:45</td>
                                <td>01:38:45</td>
                                <td>8</td>
                                <td>1</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            '''
        }
    
    @staticmethod
    def get_modiin_participants_response():
        """Mock response for Modiin participants page."""
        return {
            'url': 'https://www.matnasmodiin.org.il/html5/UAPI.TAF?get=209',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'text': '''
            <!DOCTYPE html>
            <html dir="rtl" lang="he">
            <head>
                <meta charset="utf-8">
                <title>מכבים ריצה - משתתפים</title>
            </head>
            <body>
                <div class="content">
                    <table>
                        <tr>
                            <td>דני</td>
                            <td>כהן</td>
                            <td>1980</td>
                            <td>זכר</td>
                            <td>10 ק"מ</td>
                            <td>מכבי תל אביב</td>
                        </tr>
                        <tr>
                            <td>משה</td>
                            <td>לוי</td>
                            <td>1975</td>
                            <td>זכר</td>
                            <td>10 ק"מ</td>
                            <td>הפועל ירושלים</td>
                        </tr>
                        <tr>
                            <td>שרה</td>
                            <td>לוי</td>
                            <td>1982</td>
                            <td>נקבה</td>
                            <td>5 ק"מ</td>
                            <td>מכבי חיפה</td>
                        </tr>
                    </table>
                </div>
            </body>
            </html>
            '''
        }
    
    @staticmethod
    def get_error_responses():
        """Collection of error responses for testing error handling."""
        return {
            'timeout': {
                'exception': 'Timeout',
                'message': 'Request timeout after 30 seconds'
            },
            '404_not_found': {
                'status_code': 404,
                'text': '<html><body><h1>404 Not Found</h1></body></html>'
            },
            '500_server_error': {
                'status_code': 500,
                'text': '<html><body><h1>Internal Server Error</h1></body></html>'
            },
            'no_table_found': {
                'status_code': 200,
                'text': '''
                <!DOCTYPE html>
                <html>
                <head><title>No Table</title></head>
                <body>
                    <div>No participants table found</div>
                </body>
                </html>
                '''
            },
            'malformed_html': {
                'status_code': 200,
                'text': '<html><body><div>Malformed HTML content</div></body>'
            },
            'empty_table': {
                'status_code': 200,
                'text': '''
                <!DOCTYPE html>
                <html>
                <body>
                    <table id="m_ph4wp1_tblData">
                        <thead><tr><th>שם פרטי</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </body>
                </html>
                '''
            }
        }
    
    @staticmethod
    def get_large_dataset_response():
        """Mock response with large dataset for performance testing."""
        rows = []
        for i in range(1000):
            rows.append(f'''
                <tr>
                    <td>{i+1}</td>
                    <td>שם{i}</td>
                    <td>משפחה{i}</td>
                    <td>{1980 + (i % 40)}</td>
                    <td>{"ז" if i % 2 == 0 else "נ"}</td>
                    <td>{"10 ק\"מ" if i % 3 == 0 else "21 ק\"מ" if i % 3 == 1 else "5 ק\"מ"}</td>
                    <td>קבוצה{i}</td>
                </tr>
            ''')
        
        return {
            'url': 'https://regi.3plus.co.il/events/page/large',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'text': f'''
            <!DOCTYPE html>
            <html dir="rtl" lang="he">
            <head>
                <meta charset="utf-8">
                <title>Large Dataset Test</title>
            </head>
            <body>
                <table id="m_ph4wp1_tblData">
                    <thead>
                        <tr>
                            <th>מקום</th>
                            <th>שם פרטי</th>
                            <th>שם משפחה</th>
                            <th>שנת לידה</th>
                            <th>מגדר</th>
                            <th>מקצה</th>
                            <th>קבוצה</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </body>
            </html>
            '''
        }


class ResponseBuilder:
    """Builder for creating custom mock responses."""
    
    def __init__(self):
        self.url = "https://example.com"
        self.status_code = 200
        self.headers = {'Content-Type': 'text/html; charset=utf-8'}
        self.text = ""
        self.exception = None
    
    def with_url(self, url):
        """Set URL for the response."""
        self.url = url
        return self
    
    def with_status(self, status_code):
        """Set status code for the response."""
        self.status_code = status_code
        return self
    
    def with_headers(self, headers):
        """Set headers for the response."""
        self.headers.update(headers)
        return self
    
    def with_html(self, html_content):
        """Set HTML content for the response."""
        self.text = html_content
        return self
    
    def with_exception(self, exception_type, message=""):
        """Set exception for the response."""
        self.exception = exception_type
        self.exception_message = message
        return self
    
    def build(self):
        """Build the mock response."""
        response = {
            'url': self.url,
            'status_code': self.status_code,
            'headers': self.headers,
            'text': self.text
        }
        
        if self.exception:
            response['exception'] = self.exception
            response['exception_message'] = getattr(self, 'exception_message', "")
        
        return response


# Utility functions for creating specific responses
def create_3plus_response(participants_data):
    """Create a 3plus response with custom participant data."""
    rows = []
    for i, participant in enumerate(participants_data, 1):
        rows.append(f'''
            <tr>
                <td>{i}</td>
                <td>{participant.get('first_name', 'שם')}</td>
                <td>{participant.get('last_name', 'משפחה')}</td>
                <td>{participant.get('birth_year', '1980')}</td>
                <td>{participant.get('gender', 'ז')}</td>
                <td>{participant.get('race', '10 ק"מ')}</td>
                <td>{participant.get('team', 'קבוצה')}</td>
            </tr>
        ''')
    
    html = f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="utf-8">
        <title>Custom 3plus Response</title>
    </head>
    <body>
        <table id="m_ph4wp1_tblData">
            <thead>
                <tr>
                    <th>מקום</th>
                    <th>שם פרטי</th>
                    <th>שם משפחה</th>
                    <th>שנת לידה</th>
                    <th>מגדר</th>
                    <th>מקצה</th>
                    <th>קבוצה</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </body>
    </html>
    '''
    
    return ResponseBuilder().with_html(html).build()


def create_shvoong_results_response(results_data):
    """Create a shvoong results response with custom results data."""
    rows = []
    for result in results_data:
        rows.append(f'''
            <tr>
                <td>{result.get('date', '01/01/2024')}</td>
                <td>{result.get('location', 'תל אביב')}</td>
                <td>{result.get('first_name', 'שם')}</td>
                <td>{result.get('last_name', 'משפחה')}</td>
                <td>{result.get('race', '10 ק"מ')}</td>
                <td>{result.get('result', '00:45:00')}</td>
                <td>{result.get('personal_best', '00:45:00')}</td>
                <td>{result.get('overall_position', '10')}</td>
                <td>{result.get('group_position', '2')}</td>
            </tr>
        ''')
    
    html = f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="utf-8">
        <title>Custom Shvoong Results</title>
    </head>
    <body>
        <table>
            <thead>
                <tr>
                    <th>תאריך</th>
                    <th>מקום</th>
                    <th>שם פרטי</th>
                    <th>שם משפחה</th>
                    <th>מקצה</th>
                    <th>תוצאה</th>
                    <th>זמן אישי</th>
                    <th>מיקום כללי</th>
                    <th>מיקום בקבוצה</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </body>
    </html>
    '''
    
    return ResponseBuilder().with_html(html).build()
