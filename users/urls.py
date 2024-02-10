from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    # Account creation, authorization, and authentication
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_login_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("email-verification/<str:token>/", views.account_verification_view, name="account_verification"),
    path("password-verification/", views.password_verification_view, name="password_verification"),

    # Reports generation
    path("reports/", views.store_report_redirect_view, name="store_report_redirect"),

    # Account management
    path("<str:username>/", views.user_account_view, name="account_management"),
    path("<str:username>/change-password/", views.user_account_password_change_view, name="password_change"),
    path("<str:username>/update/", views.user_account_update_view, name="account_update"),
    path("<str:username>/delete/", views.user_account_delete_view, name="account_delete"),

]
