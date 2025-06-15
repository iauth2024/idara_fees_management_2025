from django.urls import path
from .views import (
    index_view,
    screener_list, 
    trading_data_view,
    TradingAccountListView,
    TradingAccountCreateView,
    TradingAccountUpdateView,
    TradingAccountDeleteView,
    add_screener,
    edit_screener,
    delete_screener,
)
from Lucky_Bulls import views

urlpatterns = [
    # Home page
    path('', index_view, name='index'), 

    # Trading Data
    path('trading_data/', trading_data_view, name='trading_data'),

    # Trading Accounts
    path('accounts/', TradingAccountListView.as_view(), name='trading_account_list'),
    path('accounts/add/', TradingAccountCreateView.as_view(), name='trading_account_add'),
    path('accounts/<int:pk>/edit/', TradingAccountUpdateView.as_view(), name='trading_account_edit'),
    path('accounts/<int:pk>/delete/', TradingAccountDeleteView.as_view(), name='trading_account_delete'),

    # Screener Results
    path('screener_results/', views.screener_results, name='screener_results'),

    # Combined Screener Results
    path('combined_results/', views.combined_results, name='combined_results'),

    # Performance Tracking Page
    path('performance/', views.performance_page, name='performance_page'),


    # Screener Management
     path('screeners/', screener_list, name='screener_list'),
    
    # Add Screener
    path('screeners/add/', add_screener, name='add_screener'),
    
    # Edit Screener
    path('screeners/edit/<int:screener_id>/', edit_screener, name='edit_screener'),
    
    # Delete Screener
    path('screeners/delete/<int:screener_id>/', delete_screener, name='delete_screener'),
    # Trading Journal Page
    # path('trading_journal/', views.trading_journal, name='trading_journal'),

    # Delete selected stocks from the performance page (if needed)
    # path('delete-selected-stocks/', views.delete_selected_stocks, name='delete_selected_stocks'),
]
