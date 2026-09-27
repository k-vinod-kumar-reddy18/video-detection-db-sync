import os

from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")


client = MongoClient(MONGO_URI)

db = client[MONGO_DB]

detection_collection = db["detection_events"]


# CREATE
def insert_detection(data):

    result = detection_collection.insert_one(data)

    return str(result.inserted_id)


# CREATE / UPDATE VIDEO SUMMARY
def upsert_video_summary(video_name, data):

    result = detection_collection.update_one(
        {
            "video_name": video_name,
            "record_type": "video_summary"
        },
        {
            "$set": data
        },
        upsert=True
    )

    if result.upserted_id:

        return str(result.upserted_id)

    document = detection_collection.find_one(
        {
            "video_name": video_name,
            "record_type": "video_summary"
        }
    )

    if document:

        return str(document["_id"])

    return None


# READ ALL
def get_detections():

    detections = []

    for document in detection_collection.find():

        document["_id"] = str(document["_id"])

        detections.append(document)

    return detections


# READ ONE
def get_detection_by_id(detection_id):

    document = detection_collection.find_one(
        {
            "_id": ObjectId(detection_id)
        }
    )

    if document:

        document["_id"] = str(document["_id"])

    return document


# UPDATE
def update_detection(detection_id, data):

    result = detection_collection.update_one(
        {
            "_id": ObjectId(detection_id)
        },
        {
            "$set": data
        }
    )

    return result.modified_count


# DELETE
def delete_detection(detection_id):

    result = detection_collection.delete_one(
        {
            "_id": ObjectId(detection_id)
        }
    )

    return result.deleted_count