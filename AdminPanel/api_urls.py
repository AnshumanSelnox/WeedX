from django.urls import path
from .views import *
from .qwe import *
from .serializer import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('Add-Category/', AddCategories.as_view()),
    path('Get-Category/', GetCategories.as_view()),
    path('update-Category/<int:id>', UpdateCategories.as_view()),
    path('delete-Category/<int:id>', DeleteCategory.as_view()),
    ###################################################################################################
    path('Add-SubCategory/', AddSubCategories.as_view()),
    path('Get-SubCategory/', GetSubCategories.as_view()),
    path('update-SubCategory/<int:id>', UpdateSubCategories.as_view()),
    path('delete-SubCategory/<int:id>', DeleteSubCategory.as_view()),
    ###################################################################################################
    path("Login/",LoginAPI.as_view()),
    path("get-UserAPI/",UserAPI.as_view()),
    path('register/',RegisterAPI.as_view()),
    path('VerifyOtp/',VerifyOtpLogin.as_view()),
    # path('logout/',knox_views.LogoutView.as_view(),name='logout'),
    path('ResetPasswordAPI/',ResetPasswordAPI.as_view(),name='ResetPasswordAPI'),
    path('VerifyOtpResetPassword/',VerifyOtpResetPassword.as_view(),name='VerifyOtpResetPassword'),
    # path('logoutall/',knox_views.LogoutAllView.as_view(),name='logoutall'),
    ########################################################################################################
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ####################################################################################################
    path('Add-Country/', AddCountry.as_view()),
    path('Get-Country/', GetCountry.as_view()),
    path('update-Country/<int:id>', UpdateCountry.as_view()),
    path('delete-Country/<int:id>', DeleteCountry.as_view()),
    ####################################################################################################
    path('Add-States/', AddStates.as_view()),
    path('Get-States/', GetStates.as_view()),
    path('update-States/<int:id>', UpdateStates.as_view()),
    path('delete-States/<int:id>', DeleteStates.as_view()),
    ###################################################################################################
    path('Add-Brand/', AddBrand.as_view()),
    path('Get-Brand/', GetBrand.as_view()),
    path('update-Brand/<int:id>', UpdateBrand.as_view()),
    path('delete-Brand/<int:id>', DeleteBrand.as_view()),
    ####################################################################################################
    path('Add-SalesTax/', AddSalesTax.as_view()),
    path('Get-SalesTax/', GetSalesTax.as_view()),
    path('update-SalesTax/<int:id>', UpdateSalesTax.as_view()),
    path('delete-SalesTax/<int:id>', DeleteSalesTax.as_view()),
    ####################################################################################################
    path('Add-EsteemedTax/', AddEsteemedTax.as_view()),
    path('Get-EsteemedTax/', GetEsteemedTax.as_view()),
    path('update-EsteemedTax/<int:id>', UpdateEsteemedTax.as_view()),
    path('delete-EsteemedTax/<int:id>', DeleteEsteemedTax.as_view()),
    #####################################################################################################
    path('Add-News/', AddNews.as_view()),
    path('Get-News/', GetNews.as_view()),
    path('update-News/<int:id>', UpdateNews.as_view()),
    path('delete-News/<int:id>', DeleteNews.as_view()),
    #####################################################################################################
    path('Add-Cities/', AddCities.as_view()),
    path('Get-Cities/', GetCities.as_view()),
    path('update-Cities/<int:id>', UpdateCities.as_view()),
    path('delete-Cities/<int:id>', DeleteCities.as_view()),
    #####################################################################################################
    path('Add-Stores/', AddStores.as_view()),
    path('Get-Stores/', GetStores.as_view()),
    path('update-Stores/<int:id>', UpdateStores.as_view()),
    path('delete-Stores/<int:id>', DeleteStores.as_view()),
    #############################################################################################################################
    path('Get-TotalProductGraph/', TotalProductGraph.as_view()),
    path('Get-TotalCount/', TotalCount.as_view()),
    path('Add-NewsCategory/', AddNewsCategories.as_view()),
    path('Get-NewsCategory/', GetNewsCategories.as_view()),
    path('update-NewsCategory/<int:id>', UpdateNewsCategories.as_view()),
    path('delete-NewsCategory/<int:id>', DeleteNewsCategory.as_view()),
    ###################################################################################################
    path('Add-NewsSubCategory/', AddNewsSubCategories.as_view()),
    path('Get-NewsSubCategory/', GetNewsSubCategories.as_view()),
    path('update-NewsSubCategory/<int:id>', UpdateNewsSubCategories.as_view()),
    path('delete-NewsSubCategory/<int:id>', DeleteNewsSubCategory.as_view()),
    path('FilterbyNewsSubCategory/', FilterbyNewsSubCategory.as_view()),
    ######################################################################################################################
    path('FilterStatesByCountry/<int:id>', FilterStatesByCountry.as_view()),
    path('FilterCitiesByStates/<int:id>', FilterCitiesByStates.as_view()),
    ###############################################################################################################
    path('ActiveCategory/', ActiveCategory.as_view()),
    path('ActiveSubCategory/', ActiveSubCategory.as_view()),
    path('ActiveCountry/', ActiveCountry.as_view()),
    path('ActiveStates/', ActiveStates.as_view()),
    path('ActiveCities/', ActiveCities.as_view()),
    path('ActiveStores/', ActiveStores.as_view()),
    path('ActiveBrand/', ActiveBrand.as_view()),
    path('ActiveNetWeight/', ActiveNetWeight.as_view()),
    path('FilterbyCategory/<int:id>', FilterbyCategory.as_view()),
    ##########################################################################################################################################################
    path('delete-User/<int:id>', DeleteVendor.as_view()),
    path('GetAllUsers/', GetAllUsers.as_view()),
    path('GetActiveVendor/', GetActiveVendor.as_view()),
    path('GetHideVendor/', GetHideVendor.as_view()),
    ###################################################################################################
    path('Add-HomePageBanner/', Add_Home_Page_Banner.as_view()),
    path('Get-HomePageBanner/', Get_Home_Page_Banner.as_view()),
    path('update-HomePageBanner/<int:id>', Update_Home_Page_Banner.as_view()),
    path('delete-HomePageBanner/<int:id>', Delete_Home_Page_Banner.as_view()),
    ###################################################################################################
    path('upload/', FileUploadAPIView.as_view(), name='upload-file'),
    path('Get-AllVendor/', GetAllVendor.as_view()),
    #######################################################################################################################
    path('Add-Law/', AddLaw.as_view()),
    path('Get-Law/', GetLaw.as_view()),
    path('update-Law/<int:id>', UpdateLaw.as_view()),
    path('delete-Law/<int:id>', DeleteLaw.as_view()),
    #######################################################################################################################
    path('Add-AboutUs/', AddAboutUs.as_view()),
    path('Get-AboutUs/', GetAboutUs.as_view()),
    path('update-AboutUs/<int:id>', UpdateAboutUs.as_view()),
    path('delete-AboutUs/<int:id>', DeleteAboutUs.as_view()),
    #######################################################################################################################
    path('Add-TermsAndCondition/', AddTermsandCondition.as_view()),
    path('Get-TermsAndCondition/', GetTermsandCondition.as_view()),
    path('update-TermsAndCondition/<int:id>', UpdateTermsandCondition.as_view()),
    path('delete-TermsAndCondition/<int:id>', DeleteTermsandCondition.as_view()),
    #######################################################################################################################
    path('Add-PrivacyAndPolicies/', AddPrivacyandPolicies.as_view()),
    path('Get-PrivacyAndPolicies/', GetPrivacyandPolicies.as_view()),
    path('update-PrivacyAndPolicies/<int:id>', UpdatePrivacyandPolicies.as_view()),
    path('delete-PrivacyAndPolicies/<int:id>', DeletePrivacyandPolicies.as_view()),
    #######################################################################################################################
    path('Add-PromotionalBanners/', AddPromotionalBanners.as_view()),
    path('Get-PromotionalBanners/', GetPromotionalBanners.as_view()),
    path('update-PromotionalBanners/<int:id>', UpdatePromotionalBanners.as_view()),
    path('delete-PromotionalBanners/<int:id>', DeletePromotionalBanners.as_view()),
    #######################################################################################################################
    path('Add-NetWeight/', AddNet_Weight.as_view()),
    path('Get-NetWeight/', GetNet_Weight.as_view()),
    path('update-NetWeight/<int:id>', UpdateNet_Weight.as_view()),
    path('delete-NetWeight/<int:id>', DeleteNet_Weight.as_view()),
    path('Get-Subscribe/', GetSubscribe.as_view()),
    # path('generate_sitemap/', generate_sitemap.as_view()),
    path('ExportImportExcel/', ExportImportExcel.as_view()),
    #######################################################################################################################
    path('Add-StaticImages/', AddStaticImages.as_view()),
    path('Get-StaticImages', GetStaticImages.as_view()),
    path('Update-StaticImages/<int:id>', UpdateStaticImages.as_view()),
    path('Delete-StaticImages/<int:id>', DeleteStaticImages.as_view()),








]


