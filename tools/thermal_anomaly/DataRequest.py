from PyQt5.QtCore import QUrl, QUrlQuery, QDateTime
from qgis.PyQt.QtCore import pyqtSignal, QObject, Qt
from PyQt5 import QtNetwork
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
import json

TAKE = 1000
AUTH_URL = "https://meteoeye.gis.by/oauth/connect/token"
THERMAL_ANOMALY_URL = "https://meteoeye.gis.by/api/Resources/hotspots"


class DataRequest(QObject):

    requestFinished = pyqtSignal([list, bool, bool, str])
    authorizationStarted = pyqtSignal()
    authorizationFinished = pyqtSignal([bool])

    def __init__(self):
        super().__init__()
        self.__authReply = None
        self.__accessToken = None
        self.__accessTokenExpires = QDateTime.currentDateTime()
        self.__manager = QtNetwork.QNetworkAccessManager()

    def isAuthorized(self):
        return self.__accessToken is not None and self.__accessTokenExpires > QDateTime.currentDateTime()

    def authRequest(self, client_id, client_secret, page=None, date_from=None, date_to=None, polygon=None):
        # print("Authorization...")
        self.authorizationStarted.emit()
        url = QUrl(AUTH_URL)
        url_query = QUrlQuery()
        url_query.addQueryItem("grant_type", "client_credentials")
        url_query.addQueryItem("scope", "read:Resources:hotspots")
        url_query.addQueryItem("client_id", client_id)
        url_query.addQueryItem("client_secret", client_secret)
        url.setQuery(url_query)

        request = QtNetwork.QNetworkRequest()
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json".encode())
        request.setUrl(url)
        self.__authReply = self.__manager.post(request, url_query.toString(QUrl.FullyEncoded).encode())
        self.__authReply.finished.connect(lambda: self.__auth_request_finished(client_id, client_secret, page, date_from, date_to, polygon))

    def __auth_request_finished(self, client_id, client_secret, page=None, date_from=None, date_to=None, polygon=None):
        if self.__authReply is None or self.__authReply.error() != QtNetwork.QNetworkReply.NoError:
            self.authorizationFinished.emit(False)
            headers = self.__authReply.rawHeaderList()

        else:
            self.authorizationFinished.emit(True)
            data = str(self.__authReply.readAll(), 'utf-8')
            try:
                json_string = json.loads(data)
                self.__accessToken = json_string["access_token"]
                self.__accessTokenExpires = QDateTime.currentDateTime().addSecs(int(json_string["expires_in"]))
                if date_from is not None and date_to is not None and polygon is not None:
                    self.__dataRequest(page, client_id, client_secret, date_from, date_to, polygon)
            except ValueError as e:
                print(e)

    def dataRequest(self, client_id, client_secret, date_from, date_to, polygon):
        self.__dataRequest(0, client_id, client_secret, date_from, date_to, polygon)

    def __dataRequest(self, page, client_id, client_secret, date_from, date_to, polygon):
        if not self.isAuthorized():
            self.authRequest(client_id, client_secret, page, date_from, date_to, polygon)
            return

        date_format = "yyyy-MM-ddThh:mm"
        url = QUrl(THERMAL_ANOMALY_URL)
        url_query = QUrlQuery()
        if polygon is not None:
            url_query.addQueryItem("polygon", polygon)
        if date_from is not None:
            url_query.addQueryItem("shooting", "ge" + date_from.toString(date_format))
        if date_to is not None:
            url_query.addQueryItem("shooting", "le" + date_to.toString(date_format))
        url_query.addQueryItem("_take", str(TAKE))
        url_query.addQueryItem("_skip", str(page * TAKE).zfill(1))

        request = QtNetwork.QNetworkRequest()
        request.setRawHeader(b'Authorization', ('Bearer ' + self.__accessToken).encode())
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json".encode())
        request.setUrl(url)

        self.dataReply = self.__manager.post(request, url_query.toString(QUrl.FullyEncoded).encode())
        self.dataReply.finished.connect(lambda dr=self.dataReply: self.__data_request_finished(dr, client_id, client_secret, date_from, date_to, polygon))

    def __data_request_finished(self, data_reply, client_id, client_secret, date_from, date_to, polygon):
        result_items = []
        current_page = 1
        page_count = 1
        msg = None

        if data_reply is None or data_reply.error() != QtNetwork.QNetworkReply.NoError:
            msg = "data error: " + str(data_reply.error()) + ", " + self.__error_string(data_reply.error())

            headers = data_reply.rawHeaderList()

        else:
            data = str(data_reply.readAll(), 'utf-8')
            if len(data) > 0:
                try:
                    json_string = json.loads(data)
                    if "items" in json_string:
                        result_items = json_string["items"]
                    else:
                        pass
                    if "pageCount" in json_string:
                        page_count = int(json_string["pageCount"])
                        if page_count == 0:
                            page_count = 1
                        current_page = int(json_string["currentPage"])
                        if current_page < page_count:
                            self.__dataRequest(current_page, client_id, client_secret, date_from, date_to, polygon)
                        if page_count > 1:
                            msg = str(current_page) + "/" + str(page_count)
                except ValueError as e:
                    msg = "Wrong server response. Can't be converted to json"
            else:
                pass
        headers = data_reply.rawHeaderList()
        self.requestFinished.emit(result_items, (page_count > 1 and current_page > 1),
                                  (page_count == current_page),
                                  msg)

    def __error_string(self, code):
        if code == QtNetwork.QNetworkReply.NoError:
            return 'no error'
        if code == QNetworkReply.ConnectionRefusedError:
            return 'ConnectionRefusedError'
        if code == QNetworkReply.RemoteHostClosedError:
            return 'RemoteHostClosedError'
        if code == QNetworkReply.HostNotFoundError:
            return 'HostNotFoundError'
        if code == QNetworkReply.TimeoutError:
            return 'TimeoutError'
        if code == QNetworkReply.OperationCanceledError:
            return 'OperationCanceledError'
        if code == QNetworkReply.SslHandshakeFailedError:
            return 'SslHandshakeFailedError'
        if code == QNetworkReply.TemporaryNetworkFailureError:
            return 'TemporaryNetworkFailureError'
        if code == QNetworkReply.NetworkSessionFailedError:
            return 'NetworkSessionFailedError'
        if code == QNetworkReply.BackgroundRequestNotAllowedError:
            return 'BackgroundRequestNotAllowedError'
        if code == QNetworkReply.TooManyRedirectsError:
            return 'TooManyRedirectsError'
        if code == QNetworkReply.InsecureRedirectError:
            return 'InsecureRedirectError'
        if code == QNetworkReply.ProxyConnectionRefusedError:
            return 'ProxyConnectionRefusedError'
        if code == QNetworkReply.ProxyConnectionClosedError:
            return 'ProxyConnectionClosedError'
        if code == QNetworkReply.ProxyNotFoundError:
            return 'ProxyNotFoundError'
        if code == QNetworkReply.ProxyTimeoutError:
            return 'ProxyTimeoutError'
        if code == QNetworkReply.ProxyAuthenticationRequiredError:
            return 'ProxyAuthenticationRequiredError'
        if code == QNetworkReply.ContentAccessDenied:
            return 'ContentAccessDenied'
        if code == QNetworkReply.ContentOperationNotPermittedError:
            return 'ContentOperationNotPermittedError'
        if code == QNetworkReply.ContentNotFoundError:
            return 'ContentNotFoundError'
        if code == QNetworkReply.AuthenticationRequiredError:
            return 'AuthenticationRequiredError'
        if code == QNetworkReply.ContentReSendError:
            return 'ContentReSendError'
        if code == QNetworkReply.ContentConflictError:
            return 'ContentConflictError'
        if code == QNetworkReply.ContentGoneError:
            return 'ContentGoneError'
        if code == QNetworkReply.InternalServerError:
            return 'InternalServerError'
        if code == QNetworkReply.OperationNotImplementedError:
            return 'OperationNotImplementedError'
        if code == QNetworkReply.ServiceUnavailableError:
            return 'ServiceUnavailableError'
        if code == QNetworkReply.ProtocolUnknownError:
            return 'ProtocolUnknownError'
        if code == QNetworkReply.ProtocolInvalidOperationError:
            return 'ProtocolInvalidOperationError'
        if code == QNetworkReply.UnknownNetworkError:
            return 'UnknownNetworkError. An unknown network-related error was detected'
        if code == QNetworkReply.UnknownProxyError:
            return 'UnknownProxyError'
        if code == QNetworkReply.UnknownContentError:
            return 'UnknownContentError'
        if code == QNetworkReply.ProtocolFailure:
            return 'ProtocolFailure. A breakdown in protocol was detected'
        if code == QNetworkReply.UnknownServerError:
            return 'UnknownServerError. An unknown error related to the server response was detected'
        return 'UnknownError. Error with unknown error code'
