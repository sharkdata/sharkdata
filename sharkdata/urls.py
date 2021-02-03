from django.urls import include, path
import app_sharkdata_base.views

urlpatterns = [
    path("about/", app_sharkdata_base.views.viewAbout),
    path("documentation/", app_sharkdata_base.views.viewDocumentation),
    path("examplecode/", app_sharkdata_base.views.viewExampleCode),
    path("datapolicy/", app_sharkdata_base.views.viewDataPolicy),
    #
    path("datasets/", include("app_datasets.urls")),
    path("ctdprofiles/", include("app_ctdprofiles.urls")),
    path("resources/", include("app_resources.urls")),
    path("exportformats/", include("app_exportformats.urls")),
    #
    path("", include("app_datasets.urls")),  # Default page.
]
