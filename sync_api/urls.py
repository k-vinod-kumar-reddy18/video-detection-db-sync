from django.urls import path

from .views import (
    test_api,
    create_mongodb_detection,
    get_mongodb_detections,
    get_mongodb_detection,
    update_mongodb_detection,
    delete_mongodb_detection,
    sync_postgres_to_mongodb
)


urlpatterns = [

    # JWT protected test
    path(
        'test/',
        test_api
    ),

    # MongoDB CRUD

    # CREATE
    path(
        'mongodb/detection/',
        create_mongodb_detection
    ),

    # READ ALL
    path(
        'mongodb/detections/',
        get_mongodb_detections
    ),

    # READ ONE
    path(
        'mongodb/detection/<str:detection_id>/',
        get_mongodb_detection
    ),

    # UPDATE
    path(
        'mongodb/detection/<str:detection_id>/update/',
        update_mongodb_detection
    ),

    # DELETE
    path(
        'mongodb/detection/<str:detection_id>/delete/',
        delete_mongodb_detection
    ),

    # PostgreSQL → MongoDB
    path(
        'sync/',
        sync_postgres_to_mongodb
    ),
]