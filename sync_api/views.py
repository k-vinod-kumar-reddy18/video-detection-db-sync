from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .mongo import (
    insert_detection,
    get_detections,
    get_detection_by_id,
    update_detection,
    delete_detection
)

from .postgres import (
    get_detections as get_postgres_detections,
    mark_as_synced
)


# =========================
# JWT PROTECTED TEST API
# =========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_api(request):

    return Response({
        "message": "Django Common API is working",
        "user": request.user.username
    })


# =========================
# CREATE - MongoDB
# =========================

@api_view(['POST'])
def create_mongodb_detection(request):

    data = request.data

    mongo_id = insert_detection(data)

    return Response(
        {
            "message": "Detection stored in MongoDB",
            "id": mongo_id
        },
        status=status.HTTP_201_CREATED
    )


# =========================
# READ ALL - MongoDB
# =========================

@api_view(['GET'])
def get_mongodb_detections(request):

    detections = get_detections()

    return Response({
        "count": len(detections),
        "data": detections
    })


# =========================
# READ ONE - MongoDB
# =========================

@api_view(['GET'])
def get_mongodb_detection(request, detection_id):

    try:
        detection = get_detection_by_id(detection_id)

    except Exception:
        return Response(
            {
                "error": "Invalid MongoDB ID"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not detection:

        return Response(
            {
                "error": "Detection not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(detection)


# =========================
# UPDATE - MongoDB
# =========================

@api_view(['PUT'])
def update_mongodb_detection(request, detection_id):

    data = request.data

    try:
        updated_count = update_detection(
            detection_id,
            data
        )

    except Exception:
        return Response(
            {
                "error": "Invalid MongoDB ID"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if updated_count == 0:

        return Response(
            {
                "error": "Detection not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    updated_detection = get_detection_by_id(
        detection_id
    )

    return Response({
        "message": "Detection updated successfully",
        "data": updated_detection
    })


# =========================
# DELETE - MongoDB
# =========================

@api_view(['DELETE'])
def delete_mongodb_detection(request, detection_id):

    try:
        deleted_count = delete_detection(
            detection_id
        )

    except Exception:
        return Response(
            {
                "error": "Invalid MongoDB ID"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if deleted_count == 0:

        return Response(
            {
                "error": "Detection not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "message": "Detection deleted successfully"
    })


# =========================
# POSTGRESQL → MONGODB SYNC
# =========================

@api_view(['GET'])
def sync_postgres_to_mongodb(request):

    rows = get_postgres_detections()

    synced_count = 0

    for row in rows:

        postgres_id = row[0]

        detection = {
            "postgres_id": postgres_id,
            "video_name": row[1],
            "source_id": row[2],
            "object_id": row[3],
            "object_class": row[4],
            "confidence": row[5],
            "timestamp": (
                row[6].isoformat()
                if row[6]
                else None
            ),
            "frame_number": row[7],
            "bbox": row[8],
            "json_data": row[9],
            "created_on": (
                row[10].isoformat()
                if row[10]
                else None
            )
        }

        mongo_id = insert_detection(detection)

        if mongo_id:

            mark_as_synced(postgres_id)

            synced_count += 1

    return Response({
        "message": "PostgreSQL data synchronized to MongoDB",
        "synced_count": synced_count
    })