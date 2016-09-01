import numpy as np
import random as rnd
import socket, pickle, sys

def genSymMatrix(size):
    M = np.zeros((size,size))
    for i in range(size):
        for j in range(size):
            r = rnd.randint(0, size)
            M[i,j]=r
            M[j,i]=r
    return M

def genRandomVector(size):
    X = np.zeros((size,1))
    for i in range(size):
        X[i,0]=rnd.randint(0, size)
    return X

def recvMatrix(sock):
    recvd = sock.recv(3276800).decode()
    M = pickle.loads(recvd)
    return M

def sendMatrix(sock, M):
    serialized = pickle.dumps(M, protocol=0)
    sock.send(serialized.encode())
    return

def vernamCrypt(message, key):
    result = ""
    for i in range(len(message)):
        result += chr((ord(message[i])+int(key[i]))%128)
    return result

def vernamDecrypt(message, key):
    result = ""
    for i in range(len(message)):
        result += chr((ord(message[i])-int(key[i]))%128)
    return result

class Server:
    symMatrixA = None
    symMatrixB = None
    socket = None
    stat = None
    port = None
    size = None

    def __init__(self, serverPort, size):
        self.port = serverPort
        self.size = size
        self.symMatrixA = genSymMatrix(size)
        self.symMatrixB = genSymMatrix(size)
        return

    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('127.0.0.1',self.port))
            print "Server started on port ", self.port
        except IOError:
            print("\n\n\a\tNetwork error encountered. Encrypted channel closed.")
            sys.exit()
        self.socket.listen(8)
        clientSocket, connection = self.socket.accept()
        OPEN_CONNECTION = clientSocket.recv(8).decode()
        if OPEN_CONNECTION != "OPEN":
            print("Error encountered. Exiting now...")
            sys.exit()
        sendMatrix(clientSocket, self.symMatrixA)
        sendMatrix(clientSocket, self.symMatrixB)
        print("Secure channel ready. Receiving message...")
        messageSize = int(clientSocket.recv(10).decode())
        keyArray = []
        for i in range(messageSize):
            Y = genRandomVector(self.size)
            MAY = np.dot(self.symMatrixA,Y)
            MBY = np.dot(self.symMatrixB,Y)
            recvVector = recvMatrix(clientSocket)
            l = np.split(recvVector, 2)
            MAX = l[0]
            MBX = l[1]
            sendMatrix(clientSocket, np.concatenate((MAY, MBY), axis=0))
            key = np.dot(np.transpose(Y),MAX)[0,0]+np.dot(np.transpose(Y),MBX)[0,0]
            keyArray.append(key)
        message = vernamDecrypt(clientSocket.recv(messageSize + 10).decode(), keyArray)
        print "Decrypted message: "
        print message
        self.socket.close()
        return

class Client:
    socket = None
    host = None
    port = None
    OPEN_CHANNEL = "OPEN"
    CLOSE_CHANNEL = "CLOSE"

    def __init__(self, targetIP, targetPort):
        self.host = targetIP
        self.port = targetPort
        self.OPEN_CHANNEL.encode()
        self.CLOSE_CHANNEL.encode()
        return

    def run(self, message):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except IOError:
            print("\n\n\a\tNetwork error encountered. Encrypted channel closed.")
            sys.exit()
        print("Connected to ", self.host)
        self.socket.send(self.OPEN_CHANNEL)
        MA = recvMatrix(self.socket)
        MB = recvMatrix(self.socket)
        print("Secure channel ready. Sending message...")
        l = str(len(message))
        self.socket.send(l.encode())
        size = len(MA[0])
        keyArray = []
        for i in range(len(message)):
            X = genRandomVector(size)
            MAX = np.dot(MA,X)
            MBX = np.dot(MB,X)
            sendMatrix(self.socket, np.concatenate((MAX,MBX), axis=0))
            recvVector = recvMatrix(self.socket)
            l = np.split(recvVector, 2)
            MAY = l[0]
            MBY = l[1]
            key = np.dot(np.transpose(X),MAY)[0,0] + np.dot(np.transpose(X),MBY)[0,0]
            keyArray.append(key)
        encryptedMessage = vernamCrypt(message, keyArray)
        print encryptedMessage
        self.socket.send(encryptedMessage.encode())
        print "Message sent."
        print "Closing channel now."
        self.socket.close()
