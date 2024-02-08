from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_login_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("manage/<uuid:account_id>/", views.user_account_view, name="account_management"),
    path("manage/<uuid:account_id>/update/", views.user_account_update_view, name="account_update"),
    path("account-verification/<str:token>/", views.account_verification_view, name="account_verification"),
    path("password-verification/", views.password_verification_view, name="password_verification")
]
