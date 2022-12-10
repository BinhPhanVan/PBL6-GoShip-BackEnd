import firebase_admin
from firebase_admin import credentials, messaging, db
from UserApi.models import Shipper
from numpy import sin, cos, arccos, pi, round
from BaseApi.models import Notification


def rad2deg(radians):
    degrees = radians * 180 / pi
    return degrees


def deg2rad(degrees):
    radians = degrees * pi / 180
    return radians


def getDistanceBetweenPointsNew(latitude1, longitude1, latitude2, longitude2, unit='miles'):

    theta = longitude1 - longitude2

    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) +
            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        )
    )

    if unit == 'miles':
        return round(distance, 2)
    if unit == 'kilometers':
        return round(distance * 1.609344, 2)


cred = credentials.Certificate(
    "BaseApi/serviceAccountKey.json")
firebase_admin.initialize_app(
    cred, {'databaseURL': 'https://pbl6-goship-default-rtdb.asia-southeast1.firebasedatabase.app/'})


def sendPush(title, msg, registration_token, phone_numbers, dataObject=None):
    # See documentation on defining a message payload.
    print(registration_token)
    reference = db.reference('/')
    for phone_number in phone_numbers:
        reference.child("notification").child(phone_number).push({
            "title": title,
            "body": msg,
            "data": dataObject,
        })
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=dataObject,
        tokens=registration_token,
    )

    response = messaging.send_multicast(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)


def sendNotificationToShipper(lat, long, order_id):
    reference = db.reference('/')
    result = reference.child("location").get()
    shippers = Shipper.objects.all()
    for key in result.keys():
        latitude = result[key]["latitude"]
        longitude = result[key]["longitude"]
        distance = getDistanceBetweenPointsNew(
            lat, long, latitude, longitude, 'kilometers')
        if lat == latitude and long == longitude:
            distance = 0
        shipper = shippers.filter(account__phone_number=key)
        tokens = []
        phone_numbers = []
        if shipper.exists():
            shipper = shipper.first()
            if distance <= shipper.distance_receive:
                tokens.append(str(shipper.account.token_device))
                phone_numbers.append(str(shipper.account.phone_number))
    notification = Notification.objects.get(type=1)
    sendPush(notification.title, notification.body,
             tokens, phone_numbers, dataObject={"order_id": str(order_id), "type": "1"})


def sendNotificationUser(token_device, phone_number, order_id, type):
    notification = Notification.objects.get(type=type)
    sendPush(notification.title, notification.body,
             [token_device], [phone_number],  dataObject={"order_id": str(order_id), "type": str(type)})
