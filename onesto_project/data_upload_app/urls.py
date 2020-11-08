'''
Url routing for the `data` django app
'''

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from data_upload_app import views


app_name = 'data_upload_app'

# Register drf views
router = DefaultRouter()

router.register('abstractmodel', views.AbstractModelViewSet)
router.register('amlink', views.AMLinkViewSet)
router.register('attribute', views.AttributeViewSet)
router.register('instance', views.InstanceViewSet)
router.register('measure', views.MeasureViewSet)

urlpatterns = [
	path('upload-csv/', views.UploadCsvFileView.as_view(), name='upload-csv'),
    path('', include(router.urls)),
]
