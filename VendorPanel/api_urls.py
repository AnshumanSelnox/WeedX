from django.urls import path
from .views import *
# from knox import views as knox_views
urlpatterns = [    
    path("Login/",LoginAPI.as_view()),
    path("get-UserAPI/",UserAPI.as_view()),
    path('register/',RegisterAPI.as_view()),
    path('VerifyOtpLogin/',VerifyOtpLogin.as_view()),
    # path('logout/',knox_views.LogoutView.as_view(),name='logout'),
    path('ResetPassword/', ResetPassword.as_view()),
    # path('logoutall/',knox_views.LogoutAllView.as_view(),name='logoutall'),
    path('OTPverificationForRegisterAPI/', OTPverificationForRegisterAPI.as_view()),
    path('ForgetPasswordEmailsentAPI/',ForgetPasswordAPI.as_view(),name='ResetPasswordAPI'),
    path('OTPValidationForgetPasswordAPI/',ValidateOTPForgetPassword.as_view()),
    path('ForgetPassword/',VerifyOtpForgetPassword.as_view(),name='VerifyOtpResetPassword'),
    ###################################################################################################
    path('Add-Product/', AddProduct.as_view()),
    path('Get-Product/', GetProduct.as_view()),
    path('update-Product/', UpdateProduct.as_view()),
    path('delete-Product/<int:id>', DeleteProduct.as_view()),
    #################################################################################################
    path('Add-Brand/', AddBrand.as_view()),
    path('Get-Brand/', GetBrand.as_view()),
    path('update-Brand/<int:id>', UpdateBrand.as_view()),
    #################################################################################################
    path('Add-Stores/', AddStores.as_view()),
    path('Get-Stores/', GetStores.as_view()),
    path('update-Stores/<int:id>', UpdateStores.as_view()),
    #####################################################################################################
    path('Add-NetWeight/', AddNet_Weight.as_view()),
    path('Get-NetWeight/', GetNet_Weight.as_view()),
    path('update-NetWeight/<int:id>', UpdateNet_Weight.as_view()),
    #####################################################################################################
    path('Get-Category/', GetCategories.as_view()),
    #####################################################################################################
    path('Get-SubCategory/', GetSubCategories.as_view()),
    #################################################################################################################
    path('ActiveCategory/', ActiveCategory.as_view()),
    path('ActiveSubCategory/', ActiveSubCategory.as_view()),
    path('ActiveCountry/', ActiveCountry.as_view()),
    path('ActiveStates/', ActiveStates.as_view()),
    path('ActiveCities/', ActiveCities.as_view()),
    path('ActiveStores/', ActiveStores.as_view()),
    path('ActiveBrand/', ActiveBrand.as_view()),
    path('ActiveNetWeight/', ActiveNetWeight.as_view()), 
    path('FilterStatesByCountry/<int:id>', FilterStatesByCountry.as_view()),
    path('FilterCitiesByStates/<int:id>', FilterCitiesByStates.as_view()),    
    #########################################################################################################################################################
    path('CategoryOnProduct/<int:id>', CategoryOnProduct.as_view()),
    path('Get-OrderByVendors/', GetOrderByVendors.as_view()),
    path('Delete-ProductImage/<int:id>', DeleteProductImage.as_view()),
    path('StatusVendor/<int:id>', StatusVendor.as_view()),
    path('Get-TotalCountOrder/', TotalCountOrder.as_view()),
    ###################################################################################################
    path('Add-ApplyCoupoun/', AddApplyCoupoun.as_view()),
    path('Get-ApplyCoupoun/', GetApplyCoupoun.as_view()),
    path('update-ApplyCoupoun/<int:id>', UpdateApplyCoupoun.as_view()),
    path('delete-ApplyCoupoun/<int:id>', DeleteApplyCoupoun.as_view()),
    path('Get-GetStoreByVendor/', GetStoreByVendor.as_view()),
    path('Get-StoreById/<int:id>', GetStoreById.as_view()),
    path('Get-VendorCardDashBoard/', VendorCardDashBoard.as_view()),
    path('Get-CountryFilter/',CountryFilter.as_view()),
    path('Get-Law/<int:id>', GetLaw.as_view()),
    path('Get-Law/<int:id>', GetLawbyid.as_view()),
    path('Get-Law/',GetLaw.as_view()),
    path('Get-AboutUs/',GetAboutUs.as_view()),
    path('Get-TermsandCondition/',GetTermsandCondition.as_view()),
    path('Get-PrivacyandPolicies/',GetPrivacyandPolicies.as_view()),
    path('Get-CategoryByStore/',CategoryByStore.as_view()),
    path('Get-ProductByCategory/',ProductByCategory.as_view()),
    path('Get-CustomerSegmentsCustomersWhoHavePurchasedMoreThanOnce/',CustomerSegmentsCustomersWhoHavePurchasedMoreThanOnce.as_view()),
    path('Get-ConvertZipIntoName/',ConvertZipIntoName.as_view()),
    path('MainCategoryProductCount/',MainCategoryProductCount.as_view()),
    ############################################################################################################################################
    path('Get-PendingOrder/<int:id>', GetPendingOrder.as_view()),
    path('Get-DeliveredOrder/<int:id>', GetDeliveredOrder.as_view()),
    path('Get-CancelOrder/<int:id>', GetCancelOrder.as_view()),
    path('Get-ProcessingOrder/<int:id>', GetProcessingOrder.as_view()),
    path('Get-OrderBYID/<int:id>', GetOrderBYID.as_view()),
    path('Update-Order/<int:id>', UpdateOrder.as_view()),
    path('SearchOrder/<int:id>', SearchOrder.as_view()),
    path('GetTopSellingProduct/<int:id>',GetTopSellingProduct.as_view()),
    path('AddReplyonStoreReview/<int:id>',AddReplyonStoreReview.as_view()),
    path('Reply-ProductReview/<int:id>',ReplyProductReview.as_view()),
    path('SearchProduct/<int:id>', SearchProduct.as_view()),
    
    

]

